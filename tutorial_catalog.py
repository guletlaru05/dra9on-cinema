"""Shared, local-only tutorial browsing for all four public list pages."""
from hashlib import sha256
from html import escape, unescape
import re

CATEGORIES = ('all', 'character', 'lighting', 'video', 'prompts', 'tools')
COPY = {
 'ko': ['장면을 만드는 튜토리얼', '전체', '캐릭터·씬', '조명·미감', '영상·편집', '프롬프트', '자동화·도구', '주제 선택', '튜토리얼 검색', '제목·기법·도구로 검색', '검색 지우기', '{count}개 튜토리얼', '조건에 맞는 글이 없습니다. 다른 주제나 검색어로 찾아보세요.'],
 'en': ['Tutorials for creating scenes', 'All', 'Characters & scenes', 'Light & aesthetics', 'Video & editing', 'Prompts', 'Automation & tools', 'Choose a topic', 'Search tutorials', 'Search titles, techniques or tools', 'Clear search', '{count} tutorials', 'No matching tutorials. Try another topic or search term.'],
 'ja': ['シーンをつくるチュートリアル', 'すべて', '人物・シーン', '照明・美感', '映像・編集', 'プロンプト', '自動化・ツール', 'テーマを選択', '記事を検索', 'タイトル・技法・ツールで検索', '検索をクリア', '{count}件の記事', '一致する記事がありません。テーマや検索語を変えてみてください。'],
 'es': ['Tutoriales para crear escenas', 'Todos', 'Personajes y escenas', 'Luz y estética', 'Vídeo y edición', 'Prompts', 'Automatización y herramientas', 'Elige un tema', 'Buscar tutoriales', 'Busca títulos, técnicas o herramientas', 'Borrar búsqueda', '{count} tutoriales', 'No hay tutoriales que coincidan. Prueba otro tema o término.'],
}
# Topic IDs describe learning goals; model/tool names remain secondary card tags.
LESSONS = {
 'lighting-contrast': (['lighting', 'prompts'], ['GPT Image 2.5', 'Seedream', 'Nano Banana 2', 'Midjourney'], '조명 명암 하이키 렘브란트 스플릿 실루엣 lighting contrast high-key Rembrandt split silhouette 照明 明暗 iluminación contraste'),
 'cinematic-aesthetics': (['lighting', 'prompts'], ['Midjourney', 'GPT Image 2.5'], '미감 여백 색 질감 aesthetics space color texture 美感 余白 色 質感 estética color textura'),
 'claude-mcp-newtake': (['tools', 'prompts'], ['Claude', 'MCP', 'Newtake'], '자동화 automation 自動化 automatización'),
 'video-repair': (['video'], ['Video editing'], '영상 부분 수정 video local repair 映像 編集 修正 vídeo edición'),
 'blender-previs': (['character', 'tools', 'video'], ['Blender'], '프리비즈 구도 previs blocking composition 構図 previsualización composición'),
 'camera-framing': (['character'], ['Camera'], '카메라 구도 샷 camera framing shot カメラ 構図 cámara encuadre'),
 'character-sheet': (['character', 'prompts'], ['Character sheet'], '캐릭터 씬 일관성 character scene consistency 人物 シーン personajes escenas'),
 'seedance-2-5': (['video', 'prompts'], ['Seedance 2.5'], '시댄스 영상화 image to video 映像 動画 vídeo'),
 'platform-start': (['tools'], ['Higgsfield', 'Kling', 'ZCRE', 'bbanana AI'], '플랫폼 도구 platform tools ツール plataforma herramientas'),
 'seedance-languages': (['prompts', 'video'], ['Seedance', 'KO · EN · 中文'], '프롬프트 언어 비교 prompt language comparison プロンプト 比較 idiomas comparación'),
}

def inject_catalog(out, base_path=''):
 assets = {}
 for extension in ('css', 'js'):
  content = (out / ('tutorial-catalog.' + extension)).read_bytes()
  name = 'tutorial-catalog.' + sha256(content).hexdigest()[:12] + '.' + extension
  (out / 'assets/build' / name).write_bytes(content)
  assets[extension] = base_path + '/assets/build/' + name
 for lang, words in COPY.items():
  page = out / ('' if lang == 'ko' else lang) / 'tutorials/index.html'
  doc = page.read_text(encoding='utf-8')
  doc = re.sub(r'<nav class="tutorial-topics"[\s\S]*?</nav>', '', doc, count=1)
  # The list needs one introduction, rather than another hero between controls and cards.
  doc = re.sub(r'(<section class="tutorial-teaser"[^>]*>)<div>[\s\S]*?</div>(?=<div class="tutorial-lesson-list")', r'\1', doc, count=1)
  doc = re.sub(r'<h1>[\s\S]*?</h1>', '<h1>' + words[0] + '</h1>', doc, count=1)
  def annotate(match):
   card = match.group(0)
   href = unescape(re.search(r'href="([^"]+)"', card).group(1))
   slug = href.rstrip('/').split('/')[-1]
   if slug not in LESSONS:
    raise ValueError('Unclassified tutorial: ' + href)
   categories, tags, keywords = LESSONS[slug]
   if lang != 'ko':
    keywords = re.sub(r'[가-힣]+', '', keywords)
   data = ' data-topics="' + ' '.join(categories) + '" data-search-keywords="' + escape(keywords + ' ' + ' '.join(tags), quote=True) + '"'
   card = card.replace('href="' + escape(href, quote=True) + '"', 'href="' + escape(href, quote=True) + '"' + data, 1)
   labels = ''.join('<span>' + escape(tag) + '</span>' for tag in tags)
   return card.replace('</h3>', '</h3><div class="tutorial-tool-tags">' + labels + '</div>', 1)
  doc = re.sub(r'<a class="tutorial-preview"[\s\S]*?</a>', annotate, doc)
  options = ''.join('<option value="' + key + '">' + escape(words[i+1]) + '</option>' for i, key in enumerate(CATEGORIES))
  tabs = ''.join('<button type="button" data-topic="' + key + '" aria-pressed="' + ('true' if key == 'all' else 'false') + '">' + escape(words[i+1]) + '</button>' for i, key in enumerate(CATEGORIES))
  controls = '<section class="tutorial-browser" data-tutorial-browser hidden aria-label="' + words[7] + '"><div class="tutorial-topic-tabs" role="group" aria-label="' + words[7] + '">' + tabs + '</div><div class="tutorial-browser-inputs"><label class="tutorial-topic-select">' + words[7] + '<select data-topic-select>' + options + '</select></label><label class="tutorial-search">' + words[8] + '<input type="search" data-tutorial-search placeholder="' + words[9] + '" autocomplete="off" maxlength="160"></label><button type="button" class="tutorial-search-clear" data-search-clear hidden>' + words[10] + '</button></div><p class="tutorial-result-count" data-tutorial-result-count role="status" aria-live="polite" data-count-template="' + words[11] + '"></p></section>'
  doc = doc.replace('<div class="tutorial-lesson-list">', controls + '<p data-tutorial-empty hidden>' + words[12] + '</p><div class="tutorial-lesson-list" data-tutorial-list>', 1)
  doc = doc.replace('<main ', '<main data-tutorial-catalog ', 1)
  resources = '<link rel="stylesheet" href="' + assets['css'] + '"><script src="' + assets['js'] + '" defer></script>'
  doc = doc.replace('</head>', resources + '</head>', 1)
  page.write_text(doc, encoding='utf-8')
