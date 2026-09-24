# DRA9ON CINEMA

FALL 707: REBOOT와 오리지널 AI 영화를 소개하는 한국어·영어 포트폴리오입니다. 공식 YouTube 영상 22편을 임베드합니다.

## 기능

- 한국어 홈과 영어 `/en/`, 언어별 작품 상세 페이지
- 작품 검색, 시즌별 탐색, 다음 화 이동, 링크 복사, 브라우저에 저장되는 찜 목록
- 모바일 화면 지원, 키보드 탐색, 언어별 검색 메타데이터와 사이트맵
- 설치할 패키지나 API 키 없이 Python 3.10 이상으로 빌드
- 영상 파일은 YouTube에서 제공하며, 이 사이트에는 OpenAI API 호출이 없습니다.

## GitHub Pages 게시

이 저장소에는 자동 게시 설정이 포함되어 있습니다. 기본값은 비공개 보관이며, 게시 작업은 `PUBLISH_SITE` 변수를 `true`로 설정하기 전에는 실행되지 않습니다. 설정 파일만으로는 사이트가 게시되지 않습니다.

1. 저장소의 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 설정합니다.
2. 외부 공개를 결정한 후 **Settings → Secrets and variables → Actions → Variables**에서 저장소 변수 `PUBLISH_SITE`를 `true`로 추가합니다.
3. **Actions → Publish portfolio to GitHub Pages → Run workflow**를 실행합니다.
4. 게시가 완료되면 **Settings → Pages**에서 실제 사이트 주소를 확인합니다.
5. 이후 `main` 브랜치에 수정 사항을 올리면 검사 후 자동으로 다시 게시됩니다.

GitHub Free에서 Pages를 사용하려면 공개 저장소가 필요합니다. 공개 저장소에는 사이트 코드, 썸네일, 공개 영상 정보가 함께 공개됩니다. 비공개 보관만 원하는 경우 Pages를 활성화하지 마세요. **비공개 저장소가 곧 비공개 웹사이트를 뜻하지는 않습니다.**

배포 주소는 GitHub Pages 설정에서 자동으로 읽습니다. 프로젝트 주소의 하위 경로와 추후 연결한 사용자 지정 도메인을 모두 지원합니다. 비밀키나 별도의 유료 실행기는 필요하지 않습니다.

- [GitHub Pages 소개](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub Pages 이용 한도](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

## 내 컴퓨터에서 보기

```powershell
python build-portfolio.py --origin http://127.0.0.1:4173
python verify-site.py --origin http://127.0.0.1:4173
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

브라우저에서 `http://127.0.0.1:4173`을 엽니다. 이 실행 방식은 해당 컴퓨터에서만 접속할 수 있습니다.

GitHub 프로젝트 주소용 빌드 예시:

```powershell
python build-portfolio.py --origin https://guletlaru05.github.io --base-path /dra9on-cinema
python verify-site.py --origin https://guletlaru05.github.io --base-path /dra9on-cinema
```

## 수정할 파일

### 채널 소개·연락처 설정

`site_config.py`에서 연락처(`CONTACT_EMAIL`), SNS(`SOCIAL_LINKS`), 한국어·영어 소개(`ABOUT_PARAGRAPHS`)를 관리합니다.

- 현재 수신 가능한 기존 이메일을 유지합니다. `contact@dra9oncinema.com` 포워딩과 실제 수신을 확인한 후 `CONTACT_EMAIL`을 `PENDING_CONTACT_EMAIL` 값으로 바꾸세요. 이메일 표시와 복사 기능도 같은 값을 사용합니다.
- SNS는 YouTube와 Instagram(@dra9oncinema)만 연결합니다. `SOCIAL_LINKS`의 주소를 수정하면 한국어·영어 헤더와 푸터에 함께 반영됩니다.
- 공유 이미지: `site-assets/assets/og/og-ko.jpg`, `og-en.jpg`를 1200×630 JPEG, 300KB 이하로 교체하세요. 현재 이미지는 hero.jpg를 중앙 기준으로 자른 임시본입니다. 별도 이미지 라이브러리 없이 빌드됩니다.
- 첫 화 링크는 항상 시즌 1의 1화로 이동합니다. 옆의 배너 작품 링크만 롤링에 따라 변경됩니다.

| 내용 | 파일 |
| --- | --- |
| 영상 정보 | `portfolio-data.json` |
| 페이지 구성·한국어 문구 | `build-portfolio.py` |
| 영어 작품명·소개·문구 | `localization.py` |
| 디자인 | `site-assets/styles.css`, `site-assets/portfolio.css` |
| 검색·재생·찜 동작 | `site-assets/portfolio.js` |
| 썸네일·메인 이미지 | `site-assets/assets/portfolio/` |

`dist/`는 빌드 결과이며 직접 수정하거나 커밋하지 않습니다. 공식 채널 콘텐츠를 2026-09-22에 시즌 2 5화까지 확인한 스냅샷이며 새 영상은 자동으로 추가되지 않습니다. 새 영상을 추가할 때 데이터·공식 썸네일·영어 번역을 함께 갱신하세요. 영상 자막·더빙을 생성하지 않으며 자막 선택은 YouTube에서 제공하는 범위에 따릅니다.

검색 노출과 순위는 검색엔진이 결정합니다. 실제 공개 후 Search Console에서 소유권을 확인하고 `sitemap.xml`을 제출할 수 있습니다.

## 출처와 권리

공식 채널: <https://www.youtube.com/@dra9oncinema>

영상 정보, 썸네일, 소개 및 협업 이메일은 공식 채널의 공개 정보를 사용했습니다. 영문 제목이 없는 항목과 소개는 포트폴리오용으로 번역했습니다. 작품과 브랜드의 권리는 DRA9ON CINEMA에 귀속됩니다. YouTube 및 Google과 제휴한 사이트가 아닙니다. 저장소 공개 자체가 작품의 재사용 허가를 뜻하지 않습니다.


## Optional GA4 analytics

`site-assets/consent.js` uses existing property `G-TF7X8WSNGW`. Basic Consent Mode v2 blocks loading the Google tag until analytics opt-in; all three advertising signals stay denied. It runs only on the production domain. Local previews never send analytics. Preferences expire after 180 days. Footer cookie settings allow withdrawal; the opt-out flag is set immediately, consent is updated, GA cookies are cleared, and the page reloads. Other tabs reload when consent changes.

The custom `youtube_subscribe_click` event measures button clicks, not completed YouTube subscriptions. Parameters: `button_location` (hero/player/watch), `page_language`, and `link_url`. Review these in GA4 Reports > Engagement > Events or Realtime; custom parameter breakdowns require GA4 custom dimensions. Event and user retention: 2 months, activity reset disabled. Enhanced measurement is off, so query strings and form data are not automatically measured.

Privacy pages: `/privacy/` and `/en/privacy/`. Update `privacy_page.py` when collection changes. Existing YouTube embeds and Google Fonts operate separately from this site's GA4 consent.

Validation: `node test-consent.cjs`, then the existing build and `verify-site.py` commands.
