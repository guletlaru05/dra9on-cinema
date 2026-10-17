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
 pdfmetrics.registerFont(TTFont('D9NotoJP',str(root/'build-assets/fonts/NotoSansJP-Regular.ttf')))
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
 from international_content import ABOUT as LOCAL_ABOUT,SEASONS as LOCAL_SEASONS,PRESS
 def tr(ko,en,lang):return ko if lang=='ko' else en if lang=='en' else PRESS.get(en,(en,en))[0 if lang=='ja' else 1]
 for lang in ('ko','en','ja','es'):
  for style in styles.values():style.fontName='D9NotoJP' if lang=='ja' else 'D9Noto'
  flow.extend([p('PRESS KIT / '+{'ko':'한국어','en':'ENGLISH','ja':'日本語','es':'ESPAÑOL'}[lang],'eyebrow'),p('DRA9ON CINEMA','title')])
  for paragraph in (ABOUT_PARAGRAPHS.get(lang) or LOCAL_ABOUT[lang]):flow.append(p(paragraph))
  flow.extend([p(tr('채널 지표','Channel figures',lang),'heading'),p('YouTube: '+str(m['youtube'] if m['youtube'] is not None else 'Pending')+' / Instagram: '+m['instagram']+' / Facebook: '+m['facebook'])])
  flow.append(p(tr('YouTube API 제공값, 갱신: ','YouTube API retrieved: ',lang)+(m['updatedAt'] or 'Pending'),'caption'))
  flow.append(p(tr('YouTube는 API 제공값 그대로 표시하며 하루 1회 갱신합니다. Instagram·Facebook은 제작자 제공 수치이며 자동 갱신하지 않습니다. 플랫폼 간 중복 이용자를 포함합니다.','YouTube figures are shown exactly as returned by the API and refreshed daily. Instagram and Facebook figures were supplied by the creator and are not updated automatically. Audiences may overlap across platforms.',lang),'caption'))
  flow.append(PageBreak())
  flow.extend([p('FALL 707: REBOOT / SEASONS 1-2','eyebrow'),p({'ko':'시즌별 이야기','en':'The story, season by season','ja':'シーズンごとの物語','es':'La historia, temporada a temporada'}[lang],'title')])
  for index,season in enumerate(SEASONS):
   logline,synopsis=LOCAL_SEASONS[lang][index] if lang in LOCAL_SEASONS else (season['logline'][0 if lang=='ko' else 1],season['synopsis'][0 if lang=='ko' else 1])
   flow.extend([p('SEASON '+str(season['season']),'heading'),p(logline),p(synopsis)])
  flow.append(PageBreak())
  flow.extend([p('SELECTED WORK / CONTACT','eyebrow'),p(tr('협업·프로그램 참여','Collaborations and creator programs',lang),'title')])
  for case in CASES:flow.extend([p(case['name'],'heading'),p(case['url'],'caption')])
  flow.append(p(tr('Dreamina·Higgsfield·OpenArt CPP 참여. OpenArt는 2026년 8월·9월 선정. 모든 사례가 유료 광고나 공식 제휴를 뜻하지는 않습니다.','Creator program participation: Dreamina, Higgsfield and OpenArt. OpenArt selections: August and September 2026. Participation does not imply that every example is a paid advertisement or an official endorsement.',lang)))
  flow.append(p(CONTACT_EMAIL,'heading'));flow.append(p('https://dra9oncinema.com/'+('' if lang=='ko' else lang+'/')+'press/','caption'));flow.append(PageBreak())
 for style in styles.values():style.fontName='D9Noto'
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

