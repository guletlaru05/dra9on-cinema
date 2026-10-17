"""Focused checks for the user-requested training-only crawler restriction."""

import unittest
from urllib.robotparser import RobotFileParser

from robots_policy import TRAINING_AGENTS, render_robots


class RobotsPolicyTests(unittest.TestCase):
    def setUp(self):
        self.origin = 'https://dra9oncinema.com'
        self.text = render_robots(self.origin)
        self.robots = RobotFileParser()
        self.robots.parse(self.text.splitlines())

    def test_preserves_existing_rules_and_sitemap(self):
        self.assertTrue(self.text.startswith(
            'User-agent: *\nAllow: /\nDisallow: /library/\n'
            'Sitemap: https://dra9oncinema.com/sitemap.xml\n'
        ))
        self.assertEqual(self.text.count('Sitemap:'), 1)
        self.assertEqual(self.robots.site_maps(), [self.origin + '/sitemap.xml'])

    def test_blocks_every_requested_training_agent_in_both_languages(self):
        for agent in TRAINING_AGENTS:
            self.assertIn(f'User-agent: {agent}\nDisallow: /\n', self.text)
            for path in ('/', '/tutorials/', '/en/', '/en/tutorials/'):
                with self.subTest(agent=agent, path=path):
                    self.assertFalse(self.robots.can_fetch(agent, self.origin + path))

    def test_keeps_search_and_ai_search_allowed(self):
        allowed = (
            'Googlebot', 'Bingbot', 'Yeti', 'OAI-SearchBot', 'ChatGPT-User',
            'Claude-SearchBot', 'Claude-User', 'PerplexityBot',
        )
        for agent in allowed:
            for path in ('/', '/tutorials/', '/en/', '/en/tutorials/'):
                with self.subTest(agent=agent, path=path):
                    self.assertTrue(self.robots.can_fetch(agent, self.origin + path))

    def test_supports_existing_preview_base_path(self):
        self.assertIn(
            'Sitemap: https://example.com/project/sitemap.xml\n',
            render_robots('https://example.com/project'),
        )


if __name__ == '__main__':
    unittest.main()
