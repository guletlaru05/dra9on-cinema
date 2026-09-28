"""Plain-language bilingual site terms for a free film showcase."""
from html import escape
from site_config import CONTACT_EMAIL
COPY = [
('이용약관','Terms of use'),
('시행일: 2026년 9월 28일','Effective date: September 28, 2026'),
('사이트 소개','About this site'),
('DRA9ON CINEMA는 오리지널 드라마·영화와 제작 비하인드를 소개하는 무료 사이트입니다. 현재 회원가입, 유료 구독 또는 결제 서비스를 제공하지 않습니다. 이 안내는 사이트와 콘텐츠의 이용 범위를 설명합니다.','DRA9ON CINEMA is a free showcase of original films, series and behind-the-scenes stories. We currently offer no member registration, paid subscriptions or payment services. These terms explain how the site and its content may be used.'),
('작품과 콘텐츠 이용','Using our content'),
('사이트와 공식 YouTube 링크를 통한 감상, 공식 페이지 주소의 공유는 가능합니다. DRA9ON CINEMA가 권리를 보유하는 영상·이미지·텍스트를 허락 없이 복제하여 재업로드하거나 판매·상업적으로 이용하지 말아 주세요. 인용 등 관련 법률이 허용하는 이용은 제한하지 않으며, 제3자 자료의 권리는 해당 권리자에게 있습니다.','You may watch through the site and official YouTube links and share links to official pages. Please obtain permission before reproducing, reuploading, selling or commercially using videos, images or text for which DRA9ON CINEMA holds rights. Uses permitted by applicable law, including lawful quotation, are not restricted. Third-party materials remain subject to their respective owners’ rights.'),
('이용 시 지켜 주세요','Responsible use'),
('서비스를 방해하거나 보안 기능을 우회하는 행위, 재생 수·좋아요를 자동화하여 조작하는 행위, 운영자나 권리자를 사칭하는 행위를 하지 말아 주세요.','Do not disrupt the service, bypass security controls, manipulate play or like counts through automation, or impersonate the operator or rights holders.'),
('재생 수·좋아요와 외부 서비스','Counts and external services'),
('사이트의 재생 수와 좋아요는 참고용 집계이며 정확한 방문자 수나 YouTube 조회수를 뜻하지 않습니다. YouTube 등 외부 서비스에는 해당 서비스의 약관과 정책이 적용되며, 공개 상태나 서비스 사정에 따라 영상이 재생되지 않을 수 있습니다.','Site play and like counts are indicative totals, not exact visitor numbers or YouTube views. External services such as YouTube have their own terms and policies. Videos may become unavailable because of publication settings or service conditions.'),
('개인정보와 쿠키','Privacy and cookies'),
('개인정보 처리와 선택적 방문 통계에 관한 내용은 개인정보처리방침에서 확인할 수 있습니다. 통계 동의를 거부해도 작품을 감상할 수 있으며, 페이지 하단의 쿠키 설정에서 선택을 바꿀 수 있습니다.','Our privacy policy explains data processing and optional analytics. You can watch films without consenting to analytics and change your choice using Cookie settings at the bottom of the page.'),
('서비스 및 약관 변경','Service and terms changes'),
('작품 공개 일정, 사이트 기능 또는 점검에 따라 콘텐츠와 서비스가 변경되거나 일시 중단될 수 있습니다. 약관을 변경하면 시행일과 변경 내용을 이 페이지에 알리고, 이용자에게 중요한 변경은 적용 전에 사이트에 안내합니다. 이 안내는 관련 법률에 따른 이용자의 권리나 운영자의 책임을 배제하지 않습니다.','Content or services may change or pause due to release schedules, feature changes or maintenance. Changes to these terms will be described here with an effective date; material changes will be announced on the site before they take effect. These terms do not exclude users’ rights or the operator’s responsibilities under applicable law.'),
('문의 및 권리 침해 신고','Contact and rights concerns'),
('이용 허락, 사이트 이용 또는 권리 침해 관련 문의는 아래 이메일로 보내주세요. 관련 페이지 주소와 요청 내용을 함께 알려주시면 확인하겠습니다.','For permission requests, site questions or rights concerns, email us below with the relevant page URL and details of your request.'),
]
TRANSLATIONS=dict(COPY)
def build_terms(out,origin,head,header,footer):
 title=COPY[0][0]
 body='<body class="watch-page">'+header()+'<main id="main" class="privacy-copy"><h1>'+title+'</h1><p>'+COPY[1][0]+'</p>'
 for i,(ko,en) in enumerate(COPY[2:],2):
  tag='h2' if i%2==0 else 'p'
  body+=f'<{tag}>{escape(ko)}</{tag}>'
 body+=f'<p><a href="mailto:{escape(CONTACT_EMAIL)}">{escape(CONTACT_EMAIL)}</a></p><p><a href="/privacy/">개인정보처리방침</a></p></main>'+footer()+'</body></html>'
 folder=out/'terms';folder.mkdir(exist_ok=True)
 schema={'@context':'https://schema.org','@type':'WebPage','name':title,'url':origin+'/terms/'}
 (folder/'index.html').write_text(head(title+' | DRA9ON CINEMA',title,'/terms/',schema)+body,encoding='utf-8')
