"""Prepare audited Markdown fragments; needed only when the source body changes.

Development dependency: markdown-it-py. GitHub Pages builds use only stdlib and
the committed fragments, whose source and output hashes are checked at build.
"""
from hashlib import sha256
from html import escape
import json
from urllib.parse import urlsplit
from markdown_it import MarkdownIt
from newtake_tutorial import CONTENT, read_source

manifest = {}
for lang in ('ko','en'):
    metadata, body = read_source(lang)
    renderer = MarkdownIt('commonmark', {'html':False}).enable('table')
    counts = {'table':0,'code':0}

    def link_open(tokens,index,options,env):
        token = tokens[index]
        if urlsplit(token.attrGet('href') or '').hostname in ('newtake.com','www.newtake.com'):
            token.attrSet('target','_blank')
            token.attrSet('rel','sponsored noopener')
        elif urlsplit(token.attrGet('href') or '').scheme in ('https','http'):
            token.attrSet('target','_blank')
            token.attrSet('rel','noopener noreferrer')
        return renderer.renderer.renderToken(tokens,index,options,env)

    def table_open(tokens,index,options,env):
        counts['table'] += 1
        label = ('표 ' if lang=='ko' else 'Table ')+str(counts['table'])
        return '<div class="newtake-table-wrap" role="region" tabindex="0" aria-label="'+label+'"><table>\n'

    original_fence = renderer.renderer.rules['fence']
    def fence(tokens,index,options,env):
        counts['code'] += 1
        label = ('프롬프트 ' if lang=='ko' else 'Prompt ')+str(counts['code'])
        return original_fence(tokens,index,options,env).replace('<pre>','<pre class="newtake-code" tabindex="0" aria-label="'+label+'">',1)

    renderer.renderer.rules['link_open'] = link_open
    renderer.renderer.rules['table_open'] = table_open
    renderer.renderer.rules['table_close'] = lambda *args:'</table></div>\n'
    renderer.renderer.rules['fence'] = fence
    fragment = renderer.render(body)
    (CONTENT/f'claude-mcp-newtake.{lang}.html').write_text(fragment,encoding='utf-8',newline='\n')
    manifest[lang] = {'body_sha256':sha256(body.encode('utf-8')).hexdigest(),
                      'html_sha256':sha256(fragment.encode('utf-8')).hexdigest(),
                      'tables':counts['table'],'code_blocks':counts['code']}
    assert counts == {'table':2,'code':2}, counts
(CONTENT/'claude-mcp-newtake.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Prepared complete Korean and English articles; 2 tables and 2 code blocks each.')
