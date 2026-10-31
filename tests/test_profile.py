"""Offline tests with synthetic data. They never contact GitHub and need no token."""
from collections import Counter
from datetime import date
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect  # noqa: E402
import render  # noqa: E402

SECRET_NAME = 'zz-private-client-vault'
SECRET_URL = f'https://github.com/rx3card/{SECRET_NAME}'


def repo(name, private=False, fork=False, size=10, owner='rx3card'):
    return {'name': name, 'full_name': f'{owner}/{name}', 'private': private, 'fork': fork, 'size': size,
            'owner': {'login': owner}, 'html_url': f'https://github.com/{owner}/{name}',
            'description': 'confidential client work' if private else 'public', 'language': 'Rust',
            'pushed_at': '2026-01-02T00:00:00Z', 'id': 987654321}


REPOS = [repo('open-tool'), repo('someone-elses', fork=True), repo('rx3card'), repo('empty', size=0),
         repo(SECRET_NAME, private=True), repo('gone', private=True)]
LANGUAGES = {'open-tool': {'Python': 300, 'C': 100}, 'someone-elses': {'Go': 9000}, 'rx3card': {'SVG': 9000},
             SECRET_NAME: {'Rust': 600}}
DAYS = [[f'2026-10-{d:02d}', d % 4] for d in range(1, 29)]


def fake_api(path, token, body=None, attempts=4):
    if path.startswith('/user/repos'):
        return (REPOS if 'page=1' in path else []), {}
    if path.endswith('/languages'):
        name = path.split('/')[3]
        if name == 'gone':
            raise collect.Gone()
        return LANGUAGES[name], {}
    if path.startswith('/search/issues'):
        return {'items': [{'number': 7, 'repository_url': collect.API + '/repos/other/host'}]}, {}
    if '/pulls/7/files' in path:
        return [{'filename': 'src/a.ts', 'changes': 30}, {'filename': 'pnpm-lock.yaml', 'changes': 900},
                {'filename': 'README.md', 'changes': 5}], {}
    if path.startswith('/search/commits'):
        return {'items': [
            {'sha': 'a' * 40, 'repository': repo('host2', owner='other'), 'parents': [{}]},
            {'sha': 'b' * 40, 'repository': repo('host3', owner='other'), 'parents': [{}, {}]},
            {'sha': 'c' * 40, 'repository': repo('own'), 'parents': [{}]}]}, {}
    if '/commits/' in path:
        return {'files': [{'filename': 'x.py', 'changes': 10}]}, {}
    if path == '/graphql':
        weeks = [{'contributionDays': [{'date': d, 'contributionCount': n} for d, n in DAYS]}]
        return {'data': {'user': {'contributionsCollection': {'contributionCalendar': {
            'totalContributions': sum(n for _, n in DAYS), 'weeks': weeks}}}}}, {}
    raise AssertionError(path)


class Collecting(unittest.TestCase):
    def run_collect(self, previous=None):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'stats.json'
            if previous is not None:
                out.write_text(json.dumps(previous), encoding='utf-8')
            env = {'PROFILE_STATS_TOKEN': 'pat-secret', 'GITHUB_TOKEN': 'public-token'}
            with mock.patch.object(collect, 'api', fake_api), mock.patch.object(collect, 'OUT', out), \
                    mock.patch.dict('os.environ', env), mock.patch('sys.stdout', io.StringIO()) as printed:
                collect.main()
            return out.read_text(encoding='utf-8'), printed.getvalue()

    def test_bytes_are_weighted_not_averaged(self):
        ranked = collect.ranking(Counter({'Python': 300, 'C': 100, 'Rust': 600}))
        self.assertEqual([(r['rank'], r['name'], r['pct']) for r in ranked],
                         [(1, 'Rust', 60.0), (2, 'Python', 30.0), (3, 'C', 10.0)])

    def test_empty_group_is_empty(self):
        self.assertEqual(collect.ranking(Counter()), [])

    def test_scopes_and_exclusions(self):
        stats = json.loads(self.run_collect()[0])['languages']
        self.assertEqual([r['name'] for r in stats['global']], ['Rust', 'Python', 'C'])
        self.assertEqual([r['name'] for r in stats['public']], ['Python', 'C'])
        self.assertEqual([r['name'] for r in stats['private']], ['Rust'])
        names = {r['name'] for scope in stats.values() for r in scope}
        self.assertNotIn('Go', names, 'fork bytes must not count')
        self.assertNotIn('SVG', names, 'the profile repository must not count itself')

    def test_contributions_are_only_files_the_owner_touched(self):
        stats = json.loads(self.run_collect()[0])
        self.assertEqual({r['name']: r['pct'] for r in stats['languages']['contributions']},
                         {'TypeScript': 75.0, 'Python': 25.0})
        self.assertEqual(stats['contributions_coverage'],
                         {'merged_prs': 1, 'direct_commits': 1, 'repositories': 2, 'lines': 40})

    def test_output_never_identifies_private_repositories(self):
        text, printed = self.run_collect()
        for needle in (SECRET_NAME, SECRET_URL, 'confidential', '987654321', 'pat-secret', 'public-token', 'gone'):
            self.assertNotIn(needle, text)
            self.assertNotIn(needle, printed)
        self.assertNotIn('bytes', text, 'raw byte totals stay private')

    def test_revoked_repository_is_reported_without_a_name(self):
        self.assertFalse(json.loads(self.run_collect()[0])['complete'])

    def test_errors_carry_no_repository_or_url(self):
        secret = f'{collect.API}/repos/rx3card/{SECRET_NAME}/languages'
        error = HTTPError(secret, 500, 'x', {}, None)
        with mock.patch.object(collect, 'urlopen', side_effect=error), mock.patch.object(collect.time, 'sleep'):
            with self.assertRaises(collect.Failed) as caught:
                collect.api(f'/repos/rx3card/{SECRET_NAME}/languages', 'pat-secret')
        self.assertNotIn(SECRET_NAME, str(caught.exception))

    def test_failed_run_keeps_last_valid_file(self):
        previous = json.loads(self.run_collect()[0])
        def broken(*_a, **_k):
            raise collect.Failed('GitHub API unreachable')
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'stats.json'
            out.write_text(json.dumps(previous), encoding='utf-8')
            before = out.read_text(encoding='utf-8')
            env = {'PROFILE_STATS_TOKEN': 'a', 'GITHUB_TOKEN': 'b'}
            with mock.patch.object(collect, 'api', broken), mock.patch.object(collect, 'OUT', out), \
                    mock.patch.dict('os.environ', env), self.assertRaises(collect.Failed):
                collect.main()
            self.assertEqual(out.read_text(encoding='utf-8'), before)

    def test_private_scope_vanishing_is_refused(self):
        stats = json.loads(self.run_collect()[0])
        lost = json.loads(json.dumps(stats))
        lost['complete'] = True
        lost['languages']['private'] = []
        with self.assertRaises(collect.Failed):
            collect.validate(lost, stats)

    def test_partial_run_is_refused_when_a_complete_one_exists(self):
        stats = json.loads(self.run_collect()[0])
        with self.assertRaises(collect.Failed):
            collect.validate(stats, stats)

    def test_empty_statistics_are_refused(self):
        with self.assertRaises(collect.Failed):
            collect.validate({'languages': {'global': []}, 'calendar': {'total': 0, 'days': []}}, None)

    def test_no_commit_when_nothing_meaningful_changed(self):
        with mock.patch(f'{__name__}.REPOS', [r for r in REPOS if r['name'] != 'gone']):
            first = json.loads(self.run_collect()[0])
            text, printed = self.run_collect(previous=first)
        self.assertIn('Nothing meaningful', printed)
        self.assertEqual(json.loads(text), first)

    def test_public_token_is_required_for_public_data(self):
        with mock.patch.dict('os.environ', {'PROFILE_STATS_TOKEN': 'a', 'GITHUB_TOKEN': ''}), \
                self.assertRaises(collect.Failed):
            collect.main()

    def test_path_classifier(self):
        self.assertEqual(collect.language_of_path('src/app.tsx'), 'TypeScript')
        for path in ('package-lock.json', 'static/image.png', 'vendor.min.js', 'Makefile'):
            self.assertIsNone(collect.language_of_path(path))


class Rendering(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'profile.config.json').read_text(encoding='utf-8'))
        self.season = self.config['seasons']['halloween']

    def test_seasons_follow_the_calendar(self):
        self.assertEqual(render.active_season(self.config, date(2026, 10, 31)), 'halloween')
        self.assertEqual(render.active_season(self.config, date(2026, 11, 3)), 'dark')
        self.assertEqual(render.active_season(self.config, date(2026, 10, 1), 'dark'), 'dark')

    def test_a_season_can_cross_new_year(self):
        config = {'season': 'auto', 'seasons': {'x': {'from': '12-20', 'to': '01-05'}}}
        self.assertEqual(render.active_season(config, date(2026, 12, 25)), 'x')
        self.assertEqual(render.active_season(config, date(2027, 1, 3)), 'x')
        self.assertEqual(render.active_season(config, date(2027, 2, 3)), 'dark')

    def test_every_season_keeps_zero_days_readable(self):
        for season in self.config['seasons'].values():
            self.assertGreaterEqual(render.contrast(season['zero'], season['field']), 3)
            self.assertGreaterEqual(render.contrast(season['ink2'], season['field']), 4.5)
            self.assertGreaterEqual(render.contrast(season['card_ink'], season['card']), 4.5)

    def test_the_message_really_decrypts(self):
        msg = render.message(self.season, 42, '2026-10-31')
        self.assertTrue(render.decrypt(msg['cipher'], msg['pad']).startswith(msg['text']))
        self.assertEqual(len(msg['cipher']) % 5, 0)

    def test_checkerboard_round_trip(self):
        text = 'SOMETHING ANSWERED HEARD ZERO'
        self.assertEqual(render.decode_digits(render.encode_text(text)), text)

    def test_calendar_splits_on_sunday(self):
        days = [['2026-10-24', 1], ['2026-10-25', 2], ['2026-10-26', 3]]  # Saturday, Sunday, Monday
        self.assertEqual([len(w) for w in render.weeks_of(days)], [1, 2])

    def test_last_seven_days(self):
        self.assertEqual(render.last_seven([['d', 100]] + [['d', 1]] * 7), 7)

    def test_legible_lifts_dark_language_colours(self):
        self.assertGreaterEqual(render.contrast(render.legible('#000080', '#050507'), '#050507'), 4.5)


if __name__ == '__main__':
    unittest.main()
