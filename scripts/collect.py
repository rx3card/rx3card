#!/usr/bin/env python3
"""Collects aggregate GitHub statistics into data/stats.json. Standard library only.

Privacy contract: repository records stay in memory. The only private-derived
values that leave this process are language names with percentages. Errors never
name a repository or a URL. Nothing is written unless the whole run is valid, so
a failed run leaves the last good file in place.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from http.client import HTTPException
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'stats.json'
OWNER = 'rx3card'
API = 'https://api.github.com'
PER_PAGE = 100
MAX_PAGES = 50
MAX_EXTERNAL_COMMITS = 200  # shortcut: enough for this account; raise it if the count ever gets close

# Commit changes are classified by extension so file names never leave the process.
EXTENSIONS = {
    '.ts': 'TypeScript', '.tsx': 'TypeScript', '.js': 'JavaScript', '.jsx': 'JavaScript',
    '.mjs': 'JavaScript', '.cjs': 'JavaScript', '.py': 'Python', '.c': 'C', '.h': 'C',
    '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.cs': 'C#', '.rs': 'Rust',
    '.go': 'Go', '.java': 'Java', '.kt': 'Kotlin', '.swift': 'Swift', '.dart': 'Dart',
    '.rb': 'Ruby', '.php': 'PHP', '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS',
    '.scss': 'SCSS', '.sass': 'Sass', '.vue': 'Vue', '.svelte': 'Svelte', '.astro': 'Astro',
    '.sh': 'Shell', '.bash': 'Shell', '.ps1': 'PowerShell', '.sql': 'SQL', '.lua': 'Lua',
    '.r': 'R', '.ex': 'Elixir', '.exs': 'Elixir', '.hs': 'Haskell', '.zig': 'Zig',
    '.pl': 'Perl', '.ipynb': 'Jupyter Notebook',
}
SKIPPED_FILES = ('package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'bun.lock')


class Gone(Exception):
    """A repository that vanished or lost access: excluded, never fatal."""


class Failed(Exception):
    """Generic on purpose: the message must stay safe for public logs."""


def api(path: str, token: str, body: dict | None = None, attempts: int = 4):
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'rx3card-profile'}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    for attempt in range(attempts):
        try:
            with urlopen(Request(API + path, data=data, headers=headers), timeout=30) as res:
                return json.load(res), res.headers
        except HTTPError as exc:
            if exc.code in (404, 451):
                raise Gone() from None
            limited = exc.code == 429 or (exc.code == 403 and exc.headers.get('x-ratelimit-remaining') == '0')
            if limited or exc.code >= 500:
                wait = int(exc.headers.get('retry-after') or 0) or 2 ** (attempt + 2)
                if attempt + 1 < attempts and wait <= 120:
                    time.sleep(wait)
                    continue
            if exc.code == 403:
                raise Gone() from None
            raise Failed(f'GitHub API answered HTTP {exc.code}') from None
        except (OSError, HTTPException, ValueError):
            if attempt + 1 < attempts:
                time.sleep(2 ** (attempt + 1))
                continue
            raise Failed('GitHub API unreachable') from None
    raise Failed('GitHub API retries exhausted')


def paged(path: str, token: str, key: str | None = None):
    sep = '&' if '?' in path else '?'
    for page in range(1, MAX_PAGES + 1):
        data, _ = api(f'{path}{sep}per_page={PER_PAGE}&page={page}', token)
        rows = data[key] if key else data
        if not isinstance(rows, list):
            raise Failed('Unexpected response shape')
        yield from rows
        if len(rows) < PER_PAGE:
            return
    raise Failed('Pagination bound exceeded')


def owned_repositories(token: str) -> list[dict]:
    rows = paged('/user/repos?affiliation=owner&visibility=all&sort=full_name', token)
    return [r for r in rows if str((r.get('owner') or {}).get('login', '')).lower() == OWNER]


def counts_toward_languages(repo: dict) -> bool:
    """Forks carry someone else's code; the profile repo would count its own generators."""
    return not repo.get('fork') and str(repo.get('name', '')).lower() != OWNER


def language_bytes(repos: list[dict], token: str) -> tuple[Counter, Counter, bool]:
    """Returns public bytes, private bytes and whether every repository answered."""
    public, private, complete = Counter(), Counter(), True
    for repo in repos:
        if not counts_toward_languages(repo) or not repo.get('size'):
            continue  # shortcut: a size of 0 means an empty repository, GitHub has no languages for it
        parts = str(repo.get('full_name', '')).split('/')
        if len(parts) != 2:
            continue
        try:
            data, _ = api('/repos/' + '/'.join(quote(p, safe='') for p in parts) + '/languages', token)
        except Gone:
            complete = False  # access revoked or deleted mid-run
            continue
        bucket = private if repo.get('private') else public
        bucket.update({k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, int) and v > 0})
    return public, private, complete


def ranking(values: Counter) -> list[dict]:
    """percentage = language bytes / group bytes x 100, sorted high to low."""
    total = sum(values.values())
    if total <= 0:
        return []
    rows = sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))
    return [{'rank': i, 'name': name, 'pct': round(size / total * 100, 1)}
            for i, (name, size) in enumerate(rows, 1)]


def language_of_path(path: str) -> str | None:
    name = path.lower().rsplit('/', 1)[-1]
    if name in SKIPPED_FILES or name.endswith('.min.js') or '.' not in name:
        return None
    return EXTENSIONS.get('.' + name.rsplit('.', 1)[-1])


def is_external_public(repo: dict | None) -> bool:
    return bool(repo) and not repo.get('private') \
        and str((repo.get('owner') or {}).get('login', '')).lower() != OWNER


def external_work(token: str) -> tuple[Counter, dict]:
    """Lines the owner changed in other people's public repositories.

    Two verifiable sources, each counted once: files of the owner's merged pull
    requests, and commits the owner authored that landed directly. The languages
    of a host repository are never used, only the files the owner actually touched.
    """
    totals: Counter = Counter()
    repositories: set[str] = set()
    merged = 0
    query = urlencode({'q': f'author:{OWNER} is:pr is:merged is:public -user:{OWNER}'})
    for item in paged(f'/search/issues?{query}', token, 'items'):
        full_name = str(item.get('repository_url', '')).replace(API + '/repos/', '')
        try:
            files = list(paged(f"/repos/{full_name}/pulls/{item['number']}/files", token))
        except Gone:
            continue
        merged += 1
        repositories.add(full_name)
        for file in files:
            language = language_of_path(str(file.get('filename', '')))
            if language:
                totals[language] += int(file.get('changes') or 0)
    direct = 0
    query = urlencode({'q': f'author:{OWNER} is:public -user:{OWNER}', 'sort': 'committer-date'})
    for item in list(paged(f'/search/commits?{query}', token, 'items'))[:MAX_EXTERNAL_COMMITS]:
        repo = item.get('repository')
        if not is_external_public(repo) or len(item.get('parents') or []) > 1:
            continue  # merge commits repeat other people's work
        try:
            detail, _ = api(f"/repos/{repo['full_name']}/commits/{item['sha']}", token)
        except Gone:
            continue
        direct += 1
        repositories.add(repo['full_name'])
        for file in detail.get('files') or []:
            language = language_of_path(str(file.get('filename', '')))
            if language:
                totals[language] += int(file.get('changes') or 0)
    return totals, {'merged_prs': merged, 'direct_commits': direct, 'repositories': len(repositories),
                    'lines': sum(totals.values())}


def calendar(token: str) -> dict:
    query = '''query($login: String!) { user(login: $login) { contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }'''
    data, _ = api('/graphql', token, {'query': query, 'variables': {'login': OWNER}})
    try:
        cal = data['data']['user']['contributionsCollection']['contributionCalendar']
        days = [(d['date'], int(d['contributionCount'])) for w in cal['weeks'] for d in w['contributionDays']]
        return {'total': int(cal['totalContributions']), 'days': [[d, n] for d, n in days]}
    except (KeyError, TypeError, ValueError):
        raise Failed('Unexpected calendar response') from None


def public_projects(repos: list[dict], names: list[str]) -> dict:
    """Real metadata for the featured public repositories, nothing else."""
    found = {}
    for repo in repos:
        if repo.get('name') in names and not repo.get('private'):
            found[repo['name']] = {'url': repo.get('html_url'), 'language': repo.get('language'),
                                   'pushed': str(repo.get('pushed_at', ''))[:10]}
    return found


def validate(stats: dict, previous: dict | None) -> None:
    if not stats['languages']['global'] or not stats['calendar']['days']:
        raise Failed('Refusing to publish empty statistics')
    if previous and not stats['complete']:
        raise Failed('A repository did not answer; keeping the last complete run')
    # a token that lost its private access must not read as "no private code"
    if previous and previous['languages']['private'] and not stats['languages']['private']:
        raise Failed('Private scope came back empty; check the token')


def fingerprint(stats: dict) -> dict:
    """What deserves a commit. The calendar window rolls daily, so dates alone do not;
    the ISO week keeps a quiet account from going stale for more than seven days."""
    last = datetime.fromisoformat(stats['calendar']['days'][-1][0]).isocalendar()
    return {'languages': stats['languages'], 'coverage': stats['contributions_coverage'],
            'projects': stats['projects'], 'total': stats['calendar']['total'], 'week': last[:2]}


def main() -> None:
    private_token = os.getenv('PROFILE_STATS_TOKEN', '').strip()
    # Everything public comes through this token: in Actions it sees what any
    # visitor sees, so private activity can never reach the calendar by accident.
    public_token = os.getenv('GITHUB_TOKEN', '').strip()
    if not private_token or not public_token:
        raise Failed('PROFILE_STATS_TOKEN and GITHUB_TOKEN are both required')
    config = json.loads((ROOT / 'profile.config.json').read_text(encoding='utf-8'))
    repos = owned_repositories(private_token)
    public, private, complete = language_bytes(repos, private_token)
    try:
        external, coverage = external_work(public_token)
    except (Gone, Failed):
        external, coverage = Counter(), None  # shown as unavailable, never guessed
    stats = {
        'schema': 1,
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'complete': complete,
        'languages': {'global': ranking(public + private), 'public': ranking(public),
                      'private': ranking(private), 'contributions': ranking(external)},
        'contributions_coverage': coverage,
        'calendar': calendar(public_token),
        'projects': public_projects(repos, [p['repo'] for p in config['projects']]),
    }
    previous = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else None
    validate(stats, previous)
    if previous and fingerprint(previous) == fingerprint(stats):
        print('Nothing meaningful changed.')
        return
    OUT.parent.mkdir(exist_ok=True)
    tmp = OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(stats, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    tmp.replace(OUT)
    print('Statistics collected: aggregates only.')


if __name__ == '__main__':
    try:
        main()
    except (Failed, Gone) as exc:
        print(f'Refresh failed, last valid data kept: {exc}', file=sys.stderr)
        sys.exit(1)
