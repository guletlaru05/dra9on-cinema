"""One downloadable, self-contained press PDF, refreshed with the site build."""
from pathlib import Path
from html import escape

def build_pdf(out,data,stills):
 from reportlab.pdfgen import canvas
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,KeepTogether
 from reportlab.lib.styles import ParagraphStyle
 from reportlab.lib import colors
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from reportlab.lib.pagesizes import A4
 from presskit import SEASONS,metrics
 from collaboration import CASES
 from site_config import ABOUT_PARAGRAPHS,CONTACT_EMAIL
 root=Path(__file__).resolve().parent
 pdfmetrics.registerFont(TTFont('D9Noto',str(root/'build-assets/fonts/NotoSansKR-Regular.ttf')))
 target=out/'assets/press/dra9on-cinema-press-kit.pdf'
 doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=65,bottomMargin=48,title='DRA9ON CINEMA | Press Kit',author='DRA9ON CINEMA')
 styles={
 'eyebrow':ParagraphStyle('eyebrow',fontName='D9Noto',fontSize=8,leading=13,textColor=colors.HexColor('#ef3851'),spaceAfter=16),
 'title':ParagraphStyle('title',fontName='D9Noto',fontSize=26,leading=36,textColor=colors.white,spaceAfter=22,wordWrap='CJK'),
 'heading':ParagraphStyle('heading',fontName='D9Noto',fontSize=17,leading=25,textColor=colors.white,spaceBefore=16,spaceAfter=12,wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName='D9Noto',fontSize=10,leading=18,textColor=colors.HexColor('#d0d0d9'),spaceAfter=13,wordWrap='CJK'),
 'caption':ParagraphStyle('caption',fontName='D9Noto',fontSize=8,leading=13,textColor=colors.HexColor('#aaaab7'),spaceAfter=14,wordWrap='CJK')}
 flow=[]
 def p(text,style='body'):
  return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
 m=metrics(data)
 def bg(c,document):
  w,h=A4;c.saveState();c.setFillColor(colors.HexColor('#101011'));c.rect(0,0,w,h,fill=1,stroke=0)
  c.setFillColor(colors.HexColor('#ed233a'));c.setFont('D9Noto',9);c.drawString(42,h-32,'DRA9ON CINEMA')
  c.setFillColor(colors.HexColor('#9999a6'));c.setFont('D9Noto',7);c.drawString(42,25,'PRESS KIT / FALL 707: REBOOT');c.drawRightString(w-42,25,str(document.page));c.restoreState()
 for lang in ('ko','en'):
  flow.extend([p('PRESS KIT / '+('한국어' if lang=='ko' else 'ENGLISH'),'eyebrow'),p('DRA9ON CINEMA','title')])
  for paragraph in ABOUT_PARAGRAPHS[lang]:flow.append(p(paragraph))
  flow.extend([p('채널 지표' if lang=='ko' else 'Channel figures','heading'),p('YouTube: '+str(m['youtube'] if m['youtube'] is not None else 'Pending')+' / Instagram: '+m['instagram']+' / Facebook: '+m['facebook'])])
  flow.append(p(('YouTube API 제공값, 갱신: ' if lang=='ko' else 'YouTube API value, retrieved: ')+(m['updatedAt'] or 'Pending'),'caption'))
  flow.append(p('Instagram·Facebook은 제작자 제공 수치이며 자동 갱신하지 않습니다. 플랫폼 간 중복 이용자를 포함합니다.' if lang=='ko' else 'Instagram and Facebook figures are creator-supplied, not automatic. Audiences can overlap.','caption'))
  flow.append(PageBreak())
  flow.extend([p('FALL 707: REBOOT / SEASONS 1-2','eyebrow'),p('시즌별 이야기' if lang=='ko' else 'The story, season by season','title')])
  for season in SEASONS:
   flow.extend([p('SEASON '+str(season['season']),'heading'),p(season['logline'][0 if lang=='ko' else 1]),p(season['synopsis'][0 if lang=='ko' else 1])])
  flow.append(PageBreak())
  flow.extend([p('SELECTED WORK / CONTACT','eyebrow'),p('협업·프로그램 참여' if lang=='ko' else 'Collaborations and programs','title')])
  for case in CASES:flow.extend([p(case['name'],'heading'),p(case['url'],'caption')])
  flow.append(p('Dreamina·Higgsfield·OpenArt CPP 참여. OpenArt는 2026년 8월·9월 선정. 모든 사례가 유료 광고나 공식 제휴를 뜻하지는 않습니다.' if lang=='ko' else 'Dreamina, Higgsfield and OpenArt creator program participation. OpenArt selections: August and September 2026. Not every case is a paid advertisement or endorsement.'))
  flow.append(p(CONTACT_EMAIL,'heading'));flow.append(p('https://dra9oncinema.com/press/','caption'));flow.append(PageBreak())
 for offset in range(0,len(stills),2):
  flow.append(p('PRODUCTION STILLS / '+str(offset+1)+'-'+str(min(offset+2,len(stills))),'eyebrow'))
  for s in stills[offset:offset+2]:
   flow.append(Image(str(out/'assets/press'/(s['id']+'.jpg')),width=511,height=511*s['height']/s['width']))
   flow.append(p(s['caption']['ko']+' / '+s['caption']['en']+' · '+str(s['width'])+' x '+str(s['height']),'caption'))
  flow.append(PageBreak())
 flow.extend([p('WORDMARK / USAGE','eyebrow'),p('DRA9ON CINEMA','title')])
 for variant in ('dark-background','light-background'):
  flow.append(Image(str(out/'assets/press'/f'dra9on-logo-{variant}.png'),width=430,height=188,mask='auto'))
  flow.append(p('https://dra9oncinema.com/assets/press/dra9on-logo-'+variant+'.png','caption'))
 flow.append(p('작품 소개·보도·협업 검토용 자료입니다. 저작권은 DRA9ON CINEMA에 있습니다. 재편집·상업적 사용은 사전 문의해 주세요.\nMaterials for editorial coverage and collaboration review. Copyright DRA9ON CINEMA. Please contact us before re-editing or commercial use.'))
 doc.build(flow,onFirstPage=bg,onLaterPages=bg)

