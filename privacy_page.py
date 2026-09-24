"""Bilingual disclosure for the site's actual consent-gated analytics."""
from html import escape
from site_config import CONTACT_EMAIL
COPY = [
('개인정보처리방침', 'Privacy policy'),
('시행일: 2026년 9월 24일', 'Effective date: September 24, 2026'),
('운영자와 문의', 'Operator and contact'),
('DRA9ON CINEMA는 이 사이트를 운영합니다. 개인정보 관련 문의, 열람·삭제·동의 철회 요청은 아래 이메일로 보내주세요.', 'DRA9ON CINEMA operates this site. Contact the email below with privacy questions or requests for access, deletion or withdrawal of consent.'),
('선택적 방문 통계', 'Optional analytics'),
('통계 수집에 동의한 경우에만 Google Analytics 4가 실행됩니다. 거부하거나 선택하지 않으면 이 사이트의 GA4 태그를 불러오지 않으며 GA4 분석 요청을 보내지 않습니다. 거부해도 작품 감상은 가능합니다.', 'Google Analytics 4 runs only after you allow analytics. If you decline or make no choice, this site does not load its GA4 tag or send GA4 analytics requests. You can still watch the films.'),
('수집 목적과 항목', 'Purpose and data'),
('사이트 개선을 위해 방문·페이지 조회·접속 시간, 브라우저·기기 정보, 대략적인 지역, 유입 사이트와 YouTube 구독 버튼 클릭을 집계합니다. GA4는 쿠키 기반 식별자를 사용할 수 있습니다. IP 주소는 전송 과정에서 Google에 제공되지만 GA4에 개별 IP 주소로 기록·저장되지 않습니다. 이름·이메일·정확한 위치를 분석 데이터로 직접 보내지 않습니다. URL의 쿼리와 해시를 제외하고 유입 주소는 도메인만 전달합니다.', 'To improve the site, we measure visits, page views, timestamps, browser and device information, approximate region, referring sites and YouTube subscribe-button clicks. GA4 may use cookie identifiers. Google receives an IP address during transmission, but GA4 does not log or store individual IP addresses. We do not intentionally send names, email addresses or precise location as analytics data. Page URLs exclude query strings and fragments; referrers are limited to their origin.'),
('구독 버튼 클릭은 실제 YouTube 구독 완료를 의미하지 않습니다. 광고 저장, 광고 사용자 데이터 및 맞춤 광고는 허용하지 않으며 Google Signals 사용도 코드에서 비활성화합니다.', 'A subscribe-button click does not mean a completed YouTube subscription. Advertising storage, advertising user data and ad personalization remain denied, and Google Signals is disabled in the site code.'),
('쿠키와 보관', 'Cookies and retention'),
('동의 선택은 브라우저의 로컬 저장소에 180일간 기억합니다. 분석 쿠키(_ga 및 _ga_로 시작하는 쿠키)는 최대 180일로 설정합니다. GA4의 개별 이벤트·사용자 데이터 보관 설정은 2개월이며, 집계 보고서는 더 오래 남을 수 있습니다. 이미 수집된 데이터는 동의 철회만으로 자동 삭제되지 않습니다.', 'Your choice is remembered in browser local storage for 180 days. Analytics cookies (_ga and cookies beginning with _ga_) are configured to expire within 180 days. GA4 event and user data retention is set to 2 months; aggregated reports may remain longer. Withdrawing consent does not automatically erase data already collected.'),
('언제든 페이지 하단의 쿠키 설정에서 선택을 바꿀 수 있습니다. 철회하면 추가 분석을 차단하고 이 도메인의 분석 쿠키를 삭제한 뒤 페이지를 새로고침합니다. 브라우저 저장소를 지우거나 선택 기간이 만료되면 다시 묻습니다. 찜한 작품과 언어 설정은 통계와 별개의 사이트 기능용 저장소입니다.', 'Change your choice at any time using Cookie settings at the bottom of a page. Withdrawal blocks further analytics, removes analytics cookies for this domain and reloads the page. Clearing browser storage or expiry prompts a new choice. Saved films and language preferences use separate functional storage.'),
('외부 서비스와 국외 처리', 'External services and international processing'),
('동의한 분석 데이터는 사이트 이용 시 네트워크를 통해 Google LLC의 Google Analytics 서비스로 전송되며 미국 등 국외에서 처리될 수 있습니다. 목적은 위 방문 통계 분석이고 보관은 위 설정을 따릅니다. 동의를 거부하거나 철회하여 이후 전송을 중지할 수 있습니다. Google의 데이터 처리 및 개인정보 정책도 적용됩니다.', 'When you consent, analytics data is transmitted over the network to Google LLC for Google Analytics and may be processed outside your country, including in the United States. The purpose is the analytics described above, with retention as described above. Declining or withdrawing stops subsequent analytics transmission. Google data-processing terms and privacy policies also apply.'),
('이 사이트는 GitHub Pages로 제공되며 호스팅 제공자는 보안·서비스 운영을 위한 접속 정보를 처리할 수 있습니다. Google Fonts와 YouTube 임베드도 사용합니다. 이 동의 배너는 사이트의 GA4 방문 통계에 관한 것으로, 영상 플레이어나 외부 사이트의 별도 처리를 제어하지 않습니다. YouTube는 개인정보 보호 강화 모드로 삽입되며 재생·접속 시 자체 정책에 따라 정보를 처리할 수 있습니다.', 'This site is hosted on GitHub Pages, whose provider may process access information for security and service operation. We also use Google Fonts and embedded YouTube videos. This banner controls this site’s GA4 analytics; it does not control independent processing by video players or external sites. Videos use YouTube privacy-enhanced embeds, which may process information on access or playback under YouTube policies.'),
('정책 변경', 'Changes'),
('처리 방식이 바뀌면 이 페이지와 시행일을 갱신하며, 동의 범위가 바뀌면 다시 동의를 요청합니다.', 'We update this page and its effective date when processing changes, and request consent again if the scope of consent changes.'),
]
TRANSLATIONS = dict(COPY)
def build_privacy(out, origin, head, header, footer):
 title=COPY[0][0]
 body='<body class="watch-page"><div>'+header()+'</div><main id="main" class="privacy-copy"><h1>'+title+'</h1><p>'+COPY[1][0]+'</p>'
 headings={2,4,6,9,12,15}
 for i,(ko,en) in enumerate(COPY[2:],2):
  tag='h2' if i in headings else 'p'
  body+=f'<{tag}>{escape(ko)}</{tag}>'
  if i==3:body+=f'<p><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>'
 body+='<p><a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google Privacy Policy</a> · <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener noreferrer">GitHub Privacy Statement</a></p></main>'+footer()+'</body></html>'
 path=out/'privacy';path.mkdir(exist_ok=True)
 schema={'@context':'https://schema.org','@type':'WebPage','name':title,'url':origin+'/privacy/'}
 (path/'index.html').write_text(head(title+' | DRA9ON CINEMA',title,'/privacy/',schema)+body,encoding='utf-8')
