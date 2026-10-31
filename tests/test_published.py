"""Checks the real files that would be published. Runs in Actions before every commit."""
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / 'README.md').read_text(encoding='utf-8')
STATS = json.loads((ROOT / 'data' / 'stats.json').read_text(encoding='utf-8'))
ART = sorted((ROOT / 'assets' / 'art').glob('*.svg'))
ALLOWED_REPOS = {p['repo'] for p in json.loads((ROOT / 'profile.config.json').read_text(encoding='utf-8'))['projects']}
LIMIT_BYTES = 400_000


class Published(unittest.TestCase):
    def test_stats_holds_only_the_known_shape(self):
        self.assertEqual(set(STATS), {'schema', 'generated_at', 'complete', 'languages',
                                      'contributions_coverage', 'calendar', 'projects'})
        self.assertLessEqual(set(STATS['projects']), ALLOWED_REPOS)
        for rows in STATS['languages'].values():
            for row in rows:
                self.assertEqual(set(row), {'rank', 'name', 'pct'})

    def test_percentages_add_up(self):
        for rows in STATS['languages'].values():
            if rows:
                self.assertAlmostEqual(sum(r['pct'] for r in rows), 100, delta=1.5)
                self.assertEqual([r['pct'] for r in rows], sorted((r['pct'] for r in rows), reverse=True))

    def test_only_featured_public_repositories_are_linked(self):
        linked = set(re.findall(r'github\.com/rx3card/([^"\s/)]+)', README))
        self.assertLessEqual(linked, ALLOWED_REPOS)

    def test_no_token_shapes_anywhere(self):
        pattern = re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}')
        for path in [ROOT / 'README.md', ROOT / 'data' / 'stats.json', *ART]:
            self.assertIsNone(pattern.search(path.read_text(encoding='utf-8')), path.name)

    def test_forbidden_words_stay_out(self):
        banned = ('oscar', 'rojas', 'full-stack', 'full stack', 'software engineer', 'web developer',
                  'open to work', 'welcome to my github', 'follow me', 'thanks for visiting')
        lowered = README.lower()
        for word in banned:
            self.assertNotIn(word, lowered)

    def test_every_svg_is_valid_and_safe_for_img(self):
        self.assertGreaterEqual(len(ART), 20)
        for path in ART:
            with self.subTest(path.name):
                root = ET.parse(path).getroot()
                self.assertTrue(root.get('aria-label'))
                text = path.read_text(encoding='utf-8')
                self.assertNotRegex(text, r'<script|<foreignObject|href="https?:')
                self.assertLess(path.stat().st_size, LIMIT_BYTES)

    def test_every_motion_honours_reduced_motion(self):
        for path in ART:
            text = path.read_text(encoding='utf-8')
            if 'animation:' in text:
                self.assertIn('prefers-reduced-motion', text, path.name)

    def test_readme_images_exist_and_have_alt(self):
        for src in re.findall(r'(?:src|srcset)="\./([^"]+)"', README):
            self.assertTrue((ROOT / src).exists(), src)
        for tag in re.findall(r'<img [^>]+>', README):
            self.assertRegex(tag, r'alt="[^"]{12,}"')


if __name__ == '__main__':
    unittest.main()
