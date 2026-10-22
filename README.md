# DRA9ON CINEMA

## AI 배우 에이전시

`/actors/`와 민서아·연화·유나·하슬의 개별 프로필을 한국어·영어·일본어·스페인어로 제공합니다. 배우별 대표 사진과 추가 룩을 합해 5장, 소유자 YouTube 채널의 실제 출연작 스틸 6장을 사용합니다. 시즌 3에서 달라진 헤어스타일을 볼 수 있는 장면을 앞에 배치합니다. 하슬은 선글라스 착용 사진만 게시합니다. 프로필 상단의 이전·목록·다음 링크는 같은 언어에서 순환하며, 추가 사진은 닫기 버튼과 Escape를 지원하는 확대창으로 열립니다. 장면 사진은 해당 회차로 연결합니다.

`actors_config.json`은 소유자가 검토한 공개 구성만 담습니다. 원본·고해상도 시안·생성 프롬프트는 PC의 비공개 작업 폴더에 남기며, 저장소에는 최대 960px 너비의 WebP만 포함합니다. 이미지의 XMP `dc:rights`는 `© DRA9ON CINEMA. All rights reserved.`입니다. 소유자가 준 대표 사진의 기존 중앙 워터마크는 보정 없이 유지합니다. 우클릭·드래그 방지는 일반 브라우저 동작을 제한하는 편의 기능이며 이미지 복제를 완전히 막지는 않습니다.

배우의 나이대·키 등은 가상 에이전시 프로필 설정으로 표시하고 작품의 확정 설정과 구분합니다. 섭외 문의는 기존 연락용 이메일 앱을 여는 폼을 사용하며, 배우 이름을 미리 선택합니다. 입력 내용은 서버에 저장하거나 자동 전송하지 않습니다. 4개 언어 권리 고지는 각 프로필·목록과 기존 이용약관에 연결됩니다.

## 소유자 전용 방문 합계

비공개 자료실의 소유자 전용 오늘·누적 유입은 Cloudflare Workers Free와 D1의 숫자 집계를 사용합니다. 외부 링크 또는 직접 방문으로 들어온 횟수를 한국 시간 기준으로 표시하며, 쿠키·로그인·브라우저 식별자 없이 집계합니다. 공개 페이지에는 숫자를 표시하지 않습니다. /private/visits 및 /daily는 검증된 소유자 Google 토큰을 요구하고 no-store로 응답합니다. 공개 /summary는 튜토리얼 조회·복사 합계만 반환합니다. 고유 방문자나 실제 사람 수, GA4 사용자 수, YouTube 조회수를 뜻하지 않습니다. 같은 사람이 다시 들어오면 추가로 집계될 수 있습니다. 비공개 자료실은 제외합니다.

2026-10-17에 실제 Cloudflare Web Analytics와 익명 집계 Worker를 연결하고 D1 스키마를 적용했습니다. Worker `/summary`가 실제 빈 데이터의 0을 반환하는 것을 확인했습니다. 집계 시작은 최초 수신 이벤트 시각이며, 과거 Firebase 합계나 임의의 수를 새 집계에 더하지 않습니다. 기존 Firebase 익명 로그인·브라우저별 방문 추적은 다시 켜지 않습니다. 무료 한도에 도달하면 수집이 중단되거나 집계가 일시적으로 표시되지 않을 수 있습니다.

집계 동작은 `node --test test-tutorial-metrics.cjs workers/tutorial-metrics/test/worker.test.mjs`, 외부 콘텐츠 선택은 `node test-consent.cjs`로 확인합니다. Cloudflare Web Analytics의 일별 방문·페이지·유입 보고서와 사이트의 유입·조회·복사 집계는 정의가 다르므로 서로 합산하지 않습니다.

FALL 707: REBOOT와 오리지널 AI 영화를 소개하는 한국어·영어 포트폴리오입니다. 공식 YouTube 영상 26편을 임베드합니다.

## 기능

### 외부 영상 재생과 동의

홈의 시즌 3 2화 무음 미리보기는 최종 영상 14:35–14:50의 사격·근접 액션 15초입니다. 웹용 H.264 파일만 제공하며 원본 화면비를 유지하고 검은 패딩을 추가하지 않습니다. 해당 배너의 자동 전환 간격은 16초로 두고, 다른 배너의 12초 간격과 기존 재생 정지·데이터 절약·동작 줄이기 설정은 유지합니다.

동의 전에는 사이트 내부 썸네일과 짧은 쿠키 안내만 표시합니다. 썸네일 버튼은 동의 저장과 선택한 YouTube 영상의 `autoplay=1` 연결을 한 번에 수행합니다. 다른 영상은 저장된 동의로 플레이어만 불러오며 동시에 자동 재생시키지 않습니다. YouTube 주소는 `www.youtube-nocookie.com`으로 통일합니다. Instagram은 동일한 클릭 동의·연결 방식을 사용하지만, 자체 플레이어에 재생을 강제하는 비공식 명령을 보내지는 않습니다.

기존 `d9-external-media-choice-v1` 키와 최대 180일 유효기간을 유지합니다. `localStorage`가 제한되면 같은 키의 `sessionStorage`, 그마저 제한되면 현재 페이지 메모리로 처리합니다. 저장소 읽기·쓰기·접근 오류를 처리하고 다른 탭의 철회 및 BFCache 복귀 시 선택을 다시 확인합니다. Safari의 데이터 정리, 시크릿 모드, 별도 앱 브라우저, 다른 프로필에서는 영구 보관을 보장할 수 없습니다. 동의 전에 YouTube·Instagram 이미지 서버에 요청하지 않도록 포스터도 같은 사이트 파일만 사용합니다. 개인정보처리방침 안의 철회 버튼과 기존 외부 콘텐츠 설정으로 언제든 연결을 중지할 수 있습니다. 인증·게시판 보안 연결은 영상 동의와 분리되어 있습니다.

`node test-consent.cjs`는 최초 연결 차단, 한 번 클릭한 영상만 재생 요청, 회차 간 저장, 만료·철회, 저장소 접근 거부, 세션 대체, 다른 탭 및 BFCache 복귀를 검사합니다. 인앱 브라우저나 화면 크기 검사는 실제 macOS/iOS Safari·Chrome·Edge 실기기 검증과 구분해 보고합니다.

- 한국어 홈과 영어 `/en/`, 언어별 작품 상세 페이지
- 작품 검색, 시즌별 탐색, 다음 화 이동, 링크 복사, 브라우저에 저장되는 찜 목록
- 시즌 3 첫 화와 시즌 2 몰아보기의 이어 보기, 시즌 3 첫 화의 5장 카드뉴스와 7개 언어 CC 안내
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

배포 주소는 GitHub Pages 설정에서 자동으로 읽습니다. 프로젝트 주소의 하위 경로와 사용자 지정 도메인을 지원합니다. 기본 정적 사이트 빌드는 비밀키나 유료 실행기 없이 가능하며, 운영 중인 통계 Worker의 재배포에는 암호화된 Actions 비밀 `CLOUDFLARE_API_TOKEN`을 사용합니다. 공개 beacon 값·수집 주소·계정 ID는 실제 저장소 변수로 설정되어 있고, API 토큰 값은 사이트 파일에 넣지 않습니다.

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

### 제작 순서와 초기 습작 후기

`notes-content/production-workflow/`에는 소유자가 검토·게시 승인한 한국어·영어·일본어·스페인어 본문을 보관합니다. `notes_workflow.py`가 기존 공통 화면과 결합해 `/notes/workflow/`, `/notes/fall-707-beginnings/`를 만들고 언어 전환·사이트맵·공통 이미지 확대창을 연결합니다. 초기 패치 및 복장 비교는 소유자 채널의 실제 정지 프레임이며, `site-assets/assets/notes/production-workflow/manifest.json`에 출처·시각·원래 치수와 크롭 정보를 기록했습니다. 제작자 일러스트에는 실제 작업 화면이 아니라는 안내를 유지합니다. 새 미디어 생성은 하지 않았습니다.

### Claude · MCP · Newtake 튜토리얼

`/tutorials/claude-mcp-newtake/`와 `/en/tutorials/claude-mcp-newtake/`는 `tutorial-content/`의 한·영 Markdown 원고를 사용합니다. 제목·설명·날짜·태그는 각 원고의 frontmatter에서 읽습니다. 홈페이지와 튜토리얼 목록의 첫 카드, 언어 전환 링크와 사이트맵은 기존 빌드에 연결되어 있습니다.

한국어 원고는 제공받은 문장을 그대로 보존합니다. 원고를 편집할 때만 개발 환경의 `markdown-it-py`로 `python prepare-newtake-tutorial.py`를 실행해 HTML 조각과 해시 manifest를 함께 갱신하세요. 배포 빌드는 추가 패키지 없이 원고·HTML 해시를 검사하며, 원고와 조각이 다르면 실패합니다. 본문은 `newtake_tutorial.py`, 표·코드의 모바일 표시는 `site-assets/newtake-tutorial.css`에서 처리합니다.

결과 릴스는 지정된 Instagram URL을 임베드 대상으로 유지하되, 최초 HTML에서는 `data-external-src`로 보관하고 외부 콘텐츠 허용 후에만 연결합니다. 해당 두 페이지에만 CSP 프레임 허용을 추가합니다. 하단 Newtake 링크는 `target="_blank" rel="sponsored noopener"`를 유지합니다. 목록·공유 이미지는 실제 생성 영상 캡처로 오인하지 않도록 제작 흐름 도식으로 구분합니다.

### 협업 문의

홈의 `/#collaboration`과 영어 `/en/#collaboration`에 제작 분야, 공개 제작 사례, 이메일 의뢰 항목을 안내합니다. 모든 공개 페이지의 메뉴·푸터와 프로필용 `/links/`에서 연결됩니다. `collaboration.py`의 `STATS`, `CASES`, `UPDATED_AT`와 `site-assets/collaboration.css`를 관리하세요.

Instagram 팔로워 9.4만은 2026-10-17 공개 프로필의 수동 스냅샷이며 자동 갱신 수치나 중복이 제거된 사람 수가 아닙니다. 기존 YouTube 1.38만 스냅샷을 API 제공값으로 표시하지 않습니다. YouTube API 연결 전에는 구독자 수를 연결 대기 상태로 표시하며, 연결 후에는 API의 정수 문자열과 실제 갱신 시각을 표시하도록 구현했습니다. Facebook은 올바른 공식 페이지와 수치 확인 전까지 표시하지 않습니다. 뉴테이크 광고, Dreamina CPP, 빠나나 AI 도구 활용 사례를 구분하며 유료 협찬·공식 제휴 관계를 일괄 주장하지 않습니다.

제작자가 확인한 CPP 참여 프로그램은 Dreamina·Higgsfield·OpenArt입니다. 프로그램 목록과 각 공개 제작 사례를 함께 표시합니다. CPP 참여를 모든 게시물의 유료 협찬 관계나 프로그램 운영사의 보증으로 표현하지 않습니다.

OpenArt CPP 선정 이력은 제작자가 알려준 2026년 8월·9월로 표시합니다. 이 시기는 OpenArt 항목에만 적용하며 다른 프로그램의 선정 시기나 10월 선정 여부를 추정하지 않습니다.

공개 영상 26편의 한·영 시청 페이지에는 기존 `VideoObject`가 있으며, 빌드 검사는 영상 ID·썸네일·게시 시각·길이·임베드 주소가 원본 데이터와 일치하는지 확인합니다. 빈 이미지 주소도 빌드 오류로 처리합니다. 검색 결과의 썸네일 노출은 검색엔진이 결정합니다.

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
| 시즌 3 첫 화의 카드뉴스·CC 안내 | `episode_extras.py`, `site-assets/assets/fall707-s3-ep1/` |
| 디자인 | `site-assets/styles.css`, `site-assets/portfolio.css` |
| 검색·재생·찜 동작 | `site-assets/portfolio.js` |
| 썸네일·메인 이미지 | `site-assets/assets/portfolio/` |

`dist/`는 빌드 결과이며 직접 수정하거나 커밋하지 않습니다. 2026-10-17 YouTube Data API v3를 활성화하고 API 전용 제한 키를 GitHub Actions의 암호화된 비밀값에 연결했습니다. 키는 소스와 공개 사이트에 포함하지 않습니다. 하루 1회 공개 영상·통계를 갱신하며, 수동 제목·소개·썸네일을 우선 보존하고 영상 ID로 중복을 제거합니다. 조회수·구독자 수는 API 문자열 그대로 표시합니다. 영상 자막·더빙은 생성하지 않으며 자막 선택은 YouTube 플레이어의 CC와 설정에서 제공합니다.

검색 노출과 순위는 검색엔진이 결정합니다. 실제 공개 후 Search Console에서 소유권을 확인하고 `sitemap.xml`을 제출할 수 있습니다.

## 출처와 권리

공식 채널: <https://www.youtube.com/@dra9oncinema>

영상 정보, 썸네일, 소개 및 협업 이메일은 공식 채널의 공개 정보를 사용했습니다. 영문 제목이 없는 항목과 소개는 포트폴리오용으로 번역했습니다. 작품과 브랜드의 권리는 DRA9ON CINEMA에 귀속됩니다. YouTube 및 Google과 제휴한 사이트가 아닙니다. 저장소 공개 자체가 작품의 재사용 허가를 뜻하지 않습니다.


## Cookie-free analytics and optional external media

GA4 and the old Firebase per-browser visit/player ledger are no longer loaded. Historical site-play/like totals are not relabelled as official YouTube values or new anonymous visits. `analytics-config.json` (or GitHub variables `CF_WEB_ANALYTICS_TOKEN`, `D9_METRICS_ENDPOINT`) must contain real configured provider values before the new services load. Blank configuration deliberately remains inactive; no fabricated counts or demo tokens are supplied.

Cloudflare Web Analytics is the selected free, cookie-free provider. On 2026-10-17 its real public beacon was configured, and the separate Workers Free + D1 collector was deployed at `https://dra9on-tutorial-metrics.tutorial-metrics.workers.dev`, with migrations applied and a successful live `/summary` response. The collector stores day/page aggregate numbers only: page views, entry events, prompt copies, and coarse referring-platform buckets. It does not store IP addresses, browser identities, raw URLs, query strings, user agents or prompt contents. Entry counts are not unique people. DNT/GPC and local previews do not send collector events. No past Firebase totals are transferred into this new series. See `workers/tutorial-metrics/README.md` for its free-plan daily write cap and deployment requirements.

Tutorial lists default to newest, with an optional actual-view ranking. The homepage shows up to three tutorials that have recorded views; before real collection begins no popularity is invented. Every public tutorial prompt block gains a copy button; only a successful clipboard write records a copy. The same canonical tutorial combines Korean and English totals. `/summary`, `/daily` and `/weekly` expose numeric public aggregates; new public pages are registered from each build. The private library is excluded.

External YouTube/Instagram frames arrive without a `src`. Home episode cards use click-only facades: a local thumbnail and play button, with no YouTube iframe requests on load or scroll. Each card connects its own nocookie iframe only after its play button is clicked, even with remembered media permission. The selected video may play in response to that click; no other home player autoloads. Home-only title/category filtering removes compilations, OSTs and other non-episode videos without changing the full catalogs or season pages. `site-assets/consent.js` shows per-video load controls. The slim settings bar opens only when the visitor chooses the footer settings button; it does not open automatically. All YouTube frames use `youtube-nocookie.com`; this does not promise third parties use no cookies after interaction. Media choices expire after 180 days and can be withdrawn using the footer. Firebase authentication and reCAPTCHA remain protected behind explicit board/library activation, independent of analytics or media permission. Privacy pages: `/privacy/` and `/en/privacy/`. Detailed operational records are kept in the owner's private backup.

## Daily YouTube metadata

Live YouTube API synchronization is active as of 2026-10-17. The API-restricted key is stored only in the encrypted `YOUTUBE_API_KEY` Actions secret. `youtube_sync.py` refreshes public uploads and statistics at build time, reusing a 24-hour snapshot and a bounded call budget. Videos merge by ID; manual copy and existing thumbnails retain priority. Explicit season/episode titles create matching season shelves and latest-episode cards. No `search.list` polling or browser API key is used. Exact API integer strings, including zero, are preserved; YouTube itself rounds its subscriber API value, which is disclosed beside that figure. No guessed count appears when unavailable.

## Public film pages and press resources

The home, FALL 707 episode guide, season video pages and press kit have Korean, English, Japanese and Spanish routes. Tutorials remain Korean/English; untranslated destinations link to actual English pages. Language switches preserve the matching route when available, with canonical URLs, hreflang and sitemap alternates. New API episodes use a local-language introductory fallback until their editorial translations are added.

`/press/` includes eight actual production stills without encoded black bars, two background variants of the wordmark, exact YouTube API figures, owner-provided Instagram/Facebook figures, collaboration links and one self-contained four-language PDF. Stills retain their native image dimensions. The press kit is linked in ABOUT and the footer rather than the main menu.

`/fall-707/world/` introduces the published settings and character relationships through Seasons 1 and 2 only. Portraits are crops of actual released footage, with no AI generation or invented reveals. Detailed production records remain in the private backup.

Continue watching stores only the last video ID and completed episode IDs in this browser. It hides itself when storage is blocked. Ended playback or the explicit completed button advances the recommendation; all completed episodes in a season lead to the next available season. No viewing history is sent to the server.

## Validation

Run `python -m unittest test_robots_policy test_youtube_sync test_youtube_site`, `node test-consent.cjs`, and `node --test test-tutorial-metrics.cjs workers/tutorial-metrics/test/worker.test.mjs`, then the existing build and `verify-site.py` commands. The YouTube fixture verifies a new episode, a new season and its full movie in both languages without storing its artificial snapshot in the real cache.


## Restrained public-page interactions (2026-10-22)

`cinema_interactions.py` injects content-addressed `cinema-motion.css/js` into
all generated pages. Sections/headings and cards reveal once at 18px/0.6s;
home-title opacity runs once per document. Fine-pointer hover uses scale(1.02)
and subtle edges, with left-to-right text-link underlines. The film grain is
one static background tile, never a layer over players. Reduced-motion disables
animations and transitions, and touch devices do not receive hover scaling.
Without JavaScript or IntersectionObserver, content remains visible. Protected
library content is excluded from reveal hiding. Newly filtered cards are
prepared explicitly; there is no page-wide animation MutationObserver.

Run `python -m unittest test_home_players test_home_layout` and
`node test-consent.cjs` alongside the existing build/verification checks. Keep
preview changes local until the owner has reviewed them; a main-branch push
would trigger Cloudflare production deployment.


## Responsive assets and local fonts (2026-10-22)

`performance.py` creates aspect-preserving AVIF/WebP srcsets for actor photos,
production stills and video posters. Original files stay in place; central
watermarks are never removed, moved or cropped. Actor AVIF derivatives include
copyright EXIF, and WebP derivatives include copyright XMP. Dynamic lightbox
images retain their original web-sized source so changing a photo cannot leave
an old picture source selected.

The same Noto Sans and Barlow Condensed families are served locally as WOFF2,
subset from visible public text with font-display:swap. Font sources, licences
and upstream blob identities are in build-assets/fonts. Compiled derivatives
in build-assets/performance-cache avoid repeating image encoding on each build;
new content or source changes regenerate only the necessary variants. Install
requirements-build.txt for the build-only font tools. No paid image service is used.

Mobile hero clips are separate 360p MP4 files. Mobile starts with the poster;
explicit playback selects the small clip. Reduced motion, Save-Data and slow
2G/3G keep the poster until a deliberate play request. The original clips stay.
Cloudflare headers cache hashed CSS/JS, optimized images and subset fonts for
one year; original media for a week. Library shells are no-store and PWA feeds
and the service worker revalidate. Dynamic catalog/auth/API paths are not given
an immutable cache policy.


## Search metadata and fictional AI actors (2026-10-22)

Existing public routes, sitemap, robots and episode VideoObject metadata are
preserved. seo.py gives indexable pages unique titles/descriptions, corrects
tutorial-index summaries, synchronizes changed social/VideoObject descriptions,
and excludes 404 pages from indexing. Actor profiles use CreativeWork; the
listing uses CollectionPage and ItemList with explicitly fictional AI works.
No actor is represented as Person, and no protected story identity is added.
Run test_seo after building. Existing English URLs are updated in place.

Search ownership is completed by the owner. For Google Search Console, use the
URL-prefix property's HTML-tag or HTML-file verification screen; a domain
property uses its DNS TXT method. For Naver Search Advisor, register the root
URL in Webmaster Tools and choose HTML tag or file verification. A supplied
meta tag belongs in the generated homepage head (permanent source: head() in
build-portfolio.py), not in client JavaScript. A supplied verification file
must be served unchanged at its exact root filename. Do not put tokens from
another account in the site or invent verification values. After verification,
submit https://dra9oncinema.com/sitemap.xml. Existing verification records stay.


Actor casting inquiries
----------------------
The sixteen existing actor profiles (four actors, four languages) use casting.py
and the deferred, interaction-only casting.js. Both the upper and lower CTA open
a native dialog with the selected actor. Company, contact, email, actor, purpose,
message and explicit transmission agreement are required. Turnstile loads only
when the visitor opens the form; visible errors retain entries. The existing
Japanese/Spanish profiles link to the existing English privacy policy.

casting_config.json contains only the public widget key and endpoint. Never put
TURNSTILE_SECRET in that file, generated HTML, logs or GitHub. The encrypted
Cloudflare Worker secret is maintained in the dashboard. The separate free
Worker at workers/casting uses server-side Siteverify, exact hostname/action,
canonical-origin CORS, a five-per-minute per-location rate limiter, strict input
limits, and a Send Email binding restricted to the verified owner Gmail. No
request bodies or IPs are logged or persisted; no Firestore rules are changed.
The existing GitHub Cloudflare deployment token deploys this Worker through
casting-worker.yml without creating another account credential. Secrets are
preserved by normal Wrangler deployment. Run node --test test-casting.cjs
workers/casting/test.mjs and python -m unittest test_casting after building.
