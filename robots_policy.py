"""Generate the public crawl policy without blocking search or AI search."""

TRAINING_AGENTS = (
    'GPTBot',
    'ClaudeBot',
    'Google-Extended',
    'Applebot-Extended',
    'CCBot',
    'meta-externalagent',
    'Bytespider',
)


def render_robots(origin: str) -> str:
    """Keep the existing general rules and sitemap, then deny training agents."""
    existing = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /library/\n'
        f'Sitemap: {origin}/sitemap.xml\n'
    )
    training_groups = '\n'.join(
        f'User-agent: {agent}\nDisallow: /\n'
        for agent in TRAINING_AGENTS
    )
    return existing + '\n' + training_groups
