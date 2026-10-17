"""Original bilingual exercise: specify and review one local video repair."""
from html import escape
import re

PATH = '/tutorials/video-repair/'
ART = '/assets/notes/repair-cafe-target-v1.webp'
SHARE_ART = '/assets/notes/repair-cafe-share-v1.jpg'
SOURCE_ART = '/assets/notes/repair-cafe-source-v1.webp'
TITLE_KO = 'AI 영상, 고칠 부분부터 정하세요.'
TITLE_EN = 'AI video: define the repair before you regenerate.'
DATE = '2026-10-17'
EDIT_SOURCE = 'https://docs.zcre.ai/guide/video-editing'
DRAFT_SOURCE = 'https://docs.zcre.ai/guide/draft-final'
KLING_SOURCE = 'https://kling.ai/blog/kling40-kling-visual-realism-creative-control-introducing-storytelling'

PROMPT_KO = '''[첨부 연결 확인 후 사용하는 영상 부분 수정 실습]
이 문장의 @영상1과 @이미지1은 설명용 자리표시자입니다. 실제 생성 화면에서 업로드한 파일의 멘션을 선택한 표기로 바꾸고, 없는 파일의 참조는 삭제합니다.

원본: @영상1 = 내가 준비한 12초, 16:9 카페 장면 원본 영상. 이 강좌는 원본 영상을 제공하지 않으므로 직접 준비한 실제 영상을 연결합니다. 영상의 길이·오류 구간이 다르면 아래 시간과 사건도 함께 수정합니다.
목표 참고: @이미지1 = 빨간 머그컵이 있는 이 강좌의 목표 정지 이미지. 컵의 빨간색과 표면 재질만 참고합니다. 정지 이미지의 인물·손·봉투·카메라 구도로 원본 영상을 덮어쓰지 않습니다. 화면 중앙의 워터마크를 물체나 새 자막으로 만들지 않습니다.

문제 정의: 가상의 원본에서는 빨간 세라믹 머그컵이 4.0–7.0초에만 파란색으로 바뀝니다. 인물의 연기와 장면의 나머지는 사용할 수 있다고 가정합니다.
단 하나의 변경: 문제가 있는 구간의 머그컵 몸체와 손잡이 색을 같은 빨간색으로 유지합니다. 컵의 크기·형태·위치와 원본에서의 손 접촉은 유지합니다. 컵의 다른 정상 구간과 자연스럽게 이어지게 합니다.
수정 범위: 먼저 4.0–7.0초를 오류 구간으로 확인합니다. 경계 비교를 위한 예시 요청 범위는 3.6–7.4초입니다. 앞뒤 0.4초 여유는 강좌의 편집 제안이며 플랫폼 필수값이 아닙니다. 실제 화면에서 가능한 범위를 지정하고, 컷 전환을 넘거나 이미 정상인 동작을 불필요하게 다시 만들지 않도록 조정합니다.

보존 기준: 원본 성인 인물의 얼굴·머리·올리브색 재킷, 표정과 시선, 몸과 손의 움직임, 봉투의 형태·위치·이동, 카페 공간, 카메라 위치·이동·구도, 비율과 길이, 조명·색감을 유지하는 것을 목표로 합니다. 다른 소품이나 인물을 추가하지 않습니다. 컵 색 외의 장면을 새롭게 연출하지 않습니다.
오디오: 원본의 대사 유무, 실내음, 타이밍과 음량을 보존하는 것을 목표로 합니다. 새 대사·음악·효과음은 요청하지 않습니다. 오디오를 별도로 유지하거나 교체하는 설정이 있다면 실행 전 확인합니다. 문장만으로 원본 소리가 보존된다고 가정하지 않습니다.

확인 기준: 수정 전·안·후를 정상 속도와 느린 재생으로 비교합니다. 4초 직전과 7초 직후의 컵 색, 손가락과 컵 손잡이의 접촉, 얼굴·재킷·봉투, 카메라·빛의 튐, 소리의 끊김을 확인합니다. 빨간 컵이 맞아도 다른 요소가 변하면 통과시키지 않습니다.
이 요청은 보존 목표이며 프레임 단위 성공 보장이 아닙니다. 첫 결과를 확인한 뒤 같은 오류 하나만 수정합니다. 여러 컷의 인물·공간·동작이 함께 무너졌다면 장면 설계를 다시 정리하고 전체 재생성을 검토합니다.'''

PROMPT_EN = '''[Local video-repair exercise: connect actual attachments first]
@Video1 and @Image1 in this text are teaching placeholders. Replace them with the mentions selected for your uploaded files in the actual interface. Remove references to missing files.

Source: @Video1 = my actual 12-second, 16:9 cafe video. This lesson does not supply a source video; attach one you prepared. If its duration or defect differs, revise the times and events below too.
Target reference: @Image1 = this lesson's target still with a red mug. Use only the red color and surface material of the mug. Do not replace the source video's person, hands, envelope or framing with those in the still. Do not turn its central watermark into a scene object or new caption.

Defect: in the hypothetical source, a red ceramic mug turns blue only at 4.0–7.0 seconds. Assume the performance and the rest of the scene are usable.
One change only: keep the mug body and handle the same red throughout the defective interval. Preserve the mug's size, shape, position and original hand contact. Join naturally to the already-correct mug outside the interval.
Range: first identify 4.0–7.0 seconds as the defect. An example request range is 3.6–7.4 seconds to compare the boundaries. The 0.4-second handles on each side are this lesson's editing suggestion, not a platform requirement. Select a range the interface supports; adjust it to avoid crossing a cut or unnecessarily rebuilding correct action.

Preservation goals: retain the source adult's face, hair, olive jacket, expression, eyeline, body and hand movement; the envelope's shape, position and movement; the cafe space; camera position, movement and framing; aspect ratio, duration, light and color. Add no people or props. Do not redirect the scene beyond correcting the mug color.
Audio: aim to preserve the source's presence or absence of dialogue, room tone, timing and level. Request no new speech, music or effects. If separate audio-preservation or replacement settings exist, check them before running. Do not assume that wording alone preserves the source soundtrack.

Review: compare before, inside and after the repair at normal speed and in slow playback. Check the mug just before 4 seconds and just after 7 seconds, finger-to-handle contact, face, jacket, envelope, camera and lighting jumps, and audio discontinuities. A red mug does not pass if other elements drift.
These are preservation goals, not a frame-accurate guarantee. Review the first result, then change only the same remaining defect. If identity, space and motion fail across several shots, revisit the scene plan and consider full regeneration.'''

STYLE = '''<style>
.repair-main{--repair-line:#38383f;--repair-muted:#b8b8c2;--repair-accent:#ef7784}
.repair-main h1{max-width:23ch}.repair-main .repair-lead{font-size:clamp(1rem,1.3vw,1.25rem);line-height:1.85;max-width:68ch;color:#d0d0d8}
.repair-main .repair-toc{display:flex;gap:.65rem;flex-wrap:wrap;margin:1.8rem 0 2.4rem}.repair-main .repair-toc a{display:inline-flex;align-items:center;min-height:44px;border:1px solid var(--repair-line);border-radius:24px;padding:.6rem 1rem;font-size:.9rem}
.repair-main .repair-section{border-top:1px solid var(--repair-line);padding:clamp(2rem,4vw,4rem) 0;scroll-margin-top:7rem}.repair-main .repair-section h2{font-size:clamp(1.5rem,2.5vw,2.65rem);line-height:1.4;margin:.45rem 0 1rem}.repair-main .repair-section h3{font-size:1.1rem;line-height:1.6;margin:.4rem 0 .8rem}.repair-main .repair-section p,.repair-main .repair-section li{line-height:1.85;color:#c7c7d0}.repair-main .repair-section>p{max-width:82ch}
.repair-main .repair-concepts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(1rem,2vw,2rem);margin:1.8rem 0}.repair-main .repair-figure{margin:0;min-width:0}.repair-main .repair-figure img{width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;border:1px solid var(--repair-line);border-radius:7px;background:#17171b}.repair-main .repair-figure figcaption{font-size:.85rem;line-height:1.8;color:var(--repair-muted);margin-top:.8rem}.repair-main .repair-image-label{display:block;font-size:.72rem;letter-spacing:.1em;color:var(--repair-accent);margin-bottom:.3rem}.repair-main .repair-notice{border-left:2px solid var(--repair-accent);padding:.25rem 0 .25rem 1.1rem;font-size:.9rem;line-height:1.85;color:#c7c7d0;max-width:100ch}
.repair-main .repair-timeline{margin:1.8rem 0;border:1px solid var(--repair-line);border-radius:7px;padding:clamp(1rem,2.5vw,2rem);background:#17171b}.repair-main .repair-time-scale{display:grid;grid-template-columns:4fr 3fr 5fr;margin:0 0 .7rem;font-size:.85rem;color:#d8d8df}.repair-main .repair-time-scale span:last-child{grid-column:3;text-align:right}.repair-main .repair-time-scale span:nth-child(3){grid-row:1;grid-column:3}.repair-main .repair-time-scale span:nth-child(4){grid-row:1}
.repair-main .repair-time-bar{display:grid;grid-template-columns:4fr 3fr 5fr;position:relative;min-height:70px}.repair-main .repair-time-bar>span{padding:1rem .55rem;background:#25252c;display:flex;align-items:center;justify-content:center;text-align:center;font-size:.8rem;line-height:1.6;border-right:1px solid #17171b}.repair-main .repair-time-bar>span:nth-child(2){color:#fff;background:#7e2939;border:1px solid var(--repair-accent)}.repair-main .repair-time-bar::after{content:'';position:absolute;inset:-7px auto -7px 30%;width:31.6667%;border:1px dashed #f0c48b;pointer-events:none}.repair-main .repair-timeline figcaption{margin-top:1.2rem;font-size:.85rem;line-height:1.85;color:var(--repair-muted)}.repair-main .repair-legend{display:flex;gap:1rem;flex-wrap:wrap;margin-top:1rem;font-size:.8rem;color:#d0d0d8}.repair-main .repair-legend span::before{content:'';display:inline-block;width:.8rem;height:.65rem;background:#7e2939;border:1px solid var(--repair-accent);margin-right:.45rem}.repair-main .repair-legend span:last-child::before{background:transparent;border:1px dashed #f0c48b}
.repair-main .repair-steps{list-style:none;padding:0;margin:2rem 0;counter-reset:repair-step}.repair-main .repair-step{counter-increment:repair-step;display:grid;grid-template-columns:3rem minmax(0,1fr);gap:1.2rem;padding:1.8rem 0;border-top:1px solid var(--repair-line);min-width:0}.repair-main .repair-step::before{content:counter(repair-step,decimal-leading-zero);font:600 2rem 'Barlow Condensed',sans-serif;color:var(--repair-accent)}.repair-main .repair-step h3{margin-top:0}.repair-main .repair-step p{margin:.5rem 0}.repair-main .repair-detail{border:1px solid var(--repair-line);border-radius:6px;padding:0 1rem;margin:1rem 0;background:#17171b}.repair-main .repair-detail summary{cursor:pointer;padding:.9rem 0;min-height:44px;font-size:.95rem;line-height:1.7;font-weight:600}.repair-main .repair-detail[open] summary{border-bottom:1px solid var(--repair-line);margin-bottom:1rem}.repair-main .repair-detail p,.repair-main .repair-detail li{font-size:.92rem}.repair-main .repair-detail ol,.repair-main .repair-detail ul{padding-left:1.3rem}.repair-main .repair-detail li+li{margin-top:.6rem}
.repair-main .repair-table-wrap{overflow-x:auto;border:1px solid var(--repair-line);border-radius:6px;margin:1.3rem 0}.repair-main .repair-table{border-collapse:collapse;width:100%;min-width:560px;text-align:left}.repair-main .repair-table th,.repair-main .repair-table td{padding:.9rem 1rem;border-bottom:1px solid var(--repair-line);font-size:.9rem;line-height:1.85;vertical-align:top}.repair-main .repair-table th{background:#1c1c22}.repair-main .repair-table td{color:#c7c7d0}.repair-main .repair-table tr:last-child td{border-bottom:0}
.repair-main .repair-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1.5rem 0}.repair-main .repair-pair>div{padding:1.3rem;border:1px solid var(--repair-line);border-radius:6px;background:#17171b;min-width:0}.repair-main .repair-pair>div:last-child{border-color:#8d4a55}.repair-main .repair-pair p{font-size:.95rem;margin:.4rem 0}.repair-main .repair-small{font-size:.85rem;color:var(--repair-muted)}
.repair-main .repair-prompt{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;max-height:32rem;overflow:auto;background:#101013;border:1px solid var(--repair-line);border-radius:5px;padding:1rem;color:#dddde4;font:400 .9rem/1.9 var(--font);tab-size:2}.repair-main .repair-prompt code{font:inherit}.repair-main .repair-actions{display:flex;gap:.8rem;flex-wrap:wrap;align-items:center;margin:1.2rem 0}.repair-main .repair-download{display:inline-flex;min-height:44px;align-items:center;gap:.5rem;border:1px solid #60606c;border-radius:5px;padding:.75rem 1rem;font-size:.9rem}.repair-main .repair-download:hover{background:#24242a}.repair-main .repair-review{padding-left:1.3rem}.repair-main .repair-review li{padding:.35rem 0}.repair-main .repair-review strong{color:#eeeef3}
.repair-main .repair-trends{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin-top:1.5rem}.repair-main .repair-trend{border:1px solid var(--repair-line);border-radius:6px;padding:1.35rem;min-width:0;background:#17171b}.repair-main .repair-trend p{font-size:.9rem}.repair-main .repair-trend .repair-source-date{font-size:.75rem;color:var(--repair-muted);line-height:1.8}.repair-main .repair-source{display:inline-flex;align-items:center;min-height:44px;text-decoration:underline;text-underline-offset:.25em;font-size:.85rem;color:#dedee5}.repair-main a:focus-visible,.repair-main summary:focus-visible,.repair-main pre:focus-visible,.repair-main .repair-table-wrap:focus-visible{outline:2px solid #f0c48b;outline-offset:4px}
@media(max-width:1000px){.repair-main .repair-trends{grid-template-columns:1fr}.repair-main .repair-trend{padding:1.2rem}.repair-main .repair-trend p{max-width:80ch}}
@media(max-width:800px){.repair-main .repair-concepts,.repair-main .repair-pair{grid-template-columns:1fr}.repair-main .repair-step{grid-template-columns:2rem minmax(0,1fr);gap:.65rem}.repair-main .repair-toc{gap:.5rem}.repair-main .repair-toc a{font-size:.85rem;padding:.5rem .8rem}.repair-main .repair-time-bar>span{font-size:.72rem;padding:.75rem .25rem}.repair-main .repair-prompt{font-size:.82rem;max-height:28rem}.repair-main .repair-lead{font-size:1rem}}
</style>'''


def teaser(t):
    return f'''<a class="tutorial-preview" href="{PATH}"><img src="{ART}" width="1600" height="900" loading="lazy" decoding="async" alt="{t('올리브색 재킷 인물과 빨간 머그컵으로 구성한 카페 스릴러 수정 목표 AI 정지 예시','AI target still for a cafe-thriller repair: an adult in an olive jacket with a red mug')}"><div><p class="section-eyebrow">VIDEO REPAIR / ONE CHANGE AT A TIME</p><h3>{t(TITLE_KO,TITLE_EN)}</h3><p class="tutorial-card-date"><time datetime="{DATE}">2026.10.17</time> · {t('현대 카페 스릴러 · 부분 수정 · 검수','Contemporary cafe thriller · Local repair · Review')}</p><span>{t('구간·변경·보존을 정하는 실습 · 강좌 열기','Practice defining range, change and preservation · Open lesson')} →</span></div></a>'''


def build(out, origin, head, header, footer, t):
    title = t(TITLE_KO, TITLE_EN)
    desc = t('AI 영상의 오류 구간과 바꿀 것 하나, 보존할 것을 나누는 초보 실습. 카페 머그컵 예시, 12초 타임라인, 전체 프롬프트와 검수표, 공식 제작 도구 소식을 제공합니다.', 'A beginner exercise in defining a video defect, one change and preservation goals. Includes cafe-mug concepts, a 12-second timeline, complete prompts, a review checklist and official workflow notes.')

    def figure(asset, label, alt, caption, eager=False):
        return f'''<figure class="repair-figure"><a href="{asset}" target="_blank" rel="noopener"><img src="{asset}" width="1600" height="900" alt="{t(*alt)}" decoding="async" {'fetchpriority="high"' if eager else 'loading="lazy"'}></a><figcaption><span class="repair-image-label">{t(*label)}</span>{t(*caption)}</figcaption></figure>'''

    concepts = figure(SOURCE_ART, ('A / 오류를 설명하는 정지 예시','A / DEFECT CONCEPT STILL'),
        ('비 오는 카페에서 올리브색 재킷 인물 앞 머그컵이 파란색인 AI 오류 설명 이미지','AI defect concept: a blue mug before an adult in an olive jacket inside a rainy cafe'),
        ('가상의 4–7초 오류: 원래 빨간 컵이 파란색으로 변했다고 가정합니다. 이 파란 컵은 문제를 설명하기 위한 정지 예시입니다.','Hypothetical defect at 4–7 seconds: assume a red mug turned blue. This still illustrates that problem.'), True)
    concepts += figure(ART, ('B / 수정 목표를 설명하는 정지 예시','B / REPAIR TARGET STILL'),
        ('같은 카페 장면에서 머그컵을 빨간색으로 제시한 AI 수정 목표 이미지','AI repair target showing a red mug in the same cafe scene'),
        ('목표: 같은 컵의 빨간색을 유지합니다. 이 그림만 보고 영상의 인물·동작·소리가 보존됐다고 판단할 수는 없습니다.','Goal: keep the same mug red. This image cannot establish that video identity, motion or audio was preserved.'))
    example = f'''<section class="repair-section" id="repair-example"><p class="section-eyebrow">THE EXERCISE / A CUP CHANGES COLOR</p><h2>{t('좋은 장면에서, 컵 하나가 바뀌었다면.','A good scene. One mug changes color.')}</h2><p>{t('비 오는 밤의 카페. 성인 인물이 봉투를 앞에 두고 앉아 있는 12초짜리 스릴러 장면을 가정합니다. 얼굴과 연기는 쓸 만한데, 4–7초에만 빨간 머그컵이 파란색으로 바뀌었습니다. 이번 목표는 컵 색 하나를 고치고 나머지 장면을 비교하는 것입니다.','Imagine a 12-second thriller scene in a cafe on a rainy night. An adult sits with an envelope in front of them. The face and performance are usable, but a red mug turns blue only at 4–7 seconds. Correct one mug color, then compare the rest of the scene.')}</p><div class="repair-concepts">{concepts}</div><p class="repair-notice">{t('두 장 모두 이 강좌를 위해 새로 만든 AI 정지 콘셉트입니다. 실제 영상 편집기의 화면·수정 전후 결과·성능 검증 자료가 아닙니다. 원본이나 수정 영상은 생성·제공하지 않습니다. 모든 예시의 중앙에는 연한 DRA9ON CINEMA 워터마크가 있으며, 이미지를 누르면 크게 열립니다.','Both images are new AI still concepts made for this lesson. They are not editor screenshots, actual before/after video results or performance evidence. No source or repaired video was generated or supplied. Each example has a faint central DRA9ON CINEMA watermark; select an image to view it larger.')}</p></section>'''

    timeline_label = t('가상의 12초 영상. 0–4초 정상, 4–7초 컵 색 오류, 7–12초 정상. 점선은 검토용 예시 범위 3.6–7.4초를 나타냅니다.','Hypothetical 12-second video: correct at 0–4 seconds, mug-color defect at 4–7, correct at 7–12. Dashed outline: example review range, 3.6–7.4 seconds.')
    timeline = f'''<figure class="repair-timeline" aria-labelledby="repair-time-caption"><div role="img" aria-label="{timeline_label}"><div class="repair-time-scale" aria-hidden="true"><span>0 s</span><span>4 s</span><span>7 s</span><span>12 s</span></div><div class="repair-time-bar" aria-hidden="true"><span>{t('정상 구간','Correct')}</span><span>{t('컵 색 오류','Mug-color defect')}</span><span>{t('정상 구간','Correct')}</span></div></div><div class="repair-legend"><span>{t('오류 4.0–7.0초','Defect: 4.0–7.0 s')}</span><span>{t('예시 요청 범위 3.6–7.4초','Example request range: 3.6–7.4 s')}</span></div><figcaption id="repair-time-caption">{t('시간 관계를 설명하는 강좌용 도식입니다. 실제 앱 화면이나 재생 가능한 영상이 아닙니다. 먼저 4–7초의 오류를 확인하고, 경계에 여유를 줄지 결정하세요.','A lesson diagram of time relationships, not an app interface or playable video. Identify the 4–7-second defect first, then decide whether its boundaries need handles.')}</figcaption></figure>'''

    keep_rows = [
        ('바꿀 것 하나','One change','4–7초 머그컵 몸체·손잡이의 파란색 → 빨간색','Blue → red on the mug body and handle at 4–7 s'),
        ('인물·연기','Person and performance','얼굴·머리·올리브색 재킷·시선·몸과 손의 동작','Face, hair, olive jacket, eyeline, body and hand action'),
        ('소품·접촉','Props and contact','컵 형태·위치·손 접촉, 봉투의 형태·위치·이동','Mug shape, position and hand contact; envelope shape, position and movement'),
        ('촬영·소리','Picture and sound','카메라·구도·길이·비율·빛·색감, 원본 오디오와 타이밍','Camera, framing, duration, ratio, light, color, source audio and timing'),
    ]
    rows = ''.join(f'<tr><th scope="row">{t(a,b)}</th><td>{t(c,d)}</td></tr>' for a,b,c,d in keep_rows)
    preservation = f'''<div class="repair-table-wrap" tabindex="0" role="region" aria-label="{t('이번 실습의 변경과 보존 기준','Change and preservation goals for this exercise')}"><table class="repair-table"><thead><tr><th scope="col">{t('구분','Category')}</th><th scope="col">{t('작성할 내용','What to specify')}</th></tr></thead><tbody>{rows}</tbody></table></div>'''

    steps = [
        ('오류를 시간과 사건으로 적습니다.','Name the defect and its time.',
         '“컵이 이상해요” 대신 “4–7초에 빨간 컵이 파랗게 바뀐다”로 적습니다. 앞뒤 정상 구간도 재생해 실제 오류의 시작과 끝을 기록하세요.','Replace “the cup looks wrong” with “the red mug turns blue at 4–7 seconds.” Play the correct sections on either side too and record where the defect actually begins and ends.',
         f'''{timeline}<details class="repair-detail"><summary>{t('경계 앞뒤에 0.3–0.5초를 더 보는 이유','Why inspect 0.3–0.5 seconds on each side?')}</summary><p>{t('여기서는 각 0.4초를 더해 3.6–7.4초를 예시 요청 범위로 잡았습니다. 이는 연결 상태를 살피기 위한 드래곤시네마의 편집 제안이며 ZCRE 등 플랫폼의 필수 규칙이 아닙니다. 동작과 컷 위치, 실제 선택 가능한 단위에 맞춰 좁히거나 넓히고, 다른 컷을 무작정 포함하지 마세요.','Here the example range is 3.6–7.4 seconds, adding 0.4 seconds per side. This is a DRA9ON CINEMA editing suggestion for checking the join, not a ZCRE or other platform requirement. Adjust it to the action, cut positions and available selection precision; avoid casually including another shot.')}</p></details>'''),
        ('하나를 바꾸고, 지킬 것을 적습니다.','Specify one change and what must stay.',
         '컵의 색과 인물의 표정, 카메라까지 한꺼번에 고치면 원인을 비교하기 어렵습니다. 이번에는 색만 변경합니다. 보존 목록은 성공 보장이 아니라 결과를 판단할 기준입니다.','Changing the mug color, expression and camera together makes the cause hard to assess. Change only the color this time. The preservation list is a review standard, not a guarantee.', preservation),
        ('원본과 목표 참고에 역할을 줍니다.','Assign jobs to source and reference.',
         '실제 원본 영상은 시간·동작·공간의 기준, 빨간 컵 정지 이미지는 컵 색·재질만의 기준입니다. 아래 예시 태그는 업로드를 대신하지 않습니다.','The actual source video defines time, motion and space. The red-mug still defines only mug color and material. The sample tags below do not upload or connect anything.',
         f'''<details class="repair-detail"><summary>{t('@영상1 · @이미지1은 어떻게 연결하나요?','How do @Video1 and @Image1 connect?')}</summary><p>{t('자료를 업로드한 뒤 실제 화면의 멘션 선택 기능으로 파일을 지정하고, 프롬프트의 자리표시자를 그 표기로 바꾸세요. 이름과 문법은 도구마다 다릅니다. 태그를 직접 타이핑하는 것만으로 연결됐다고 가정하지 마세요. 원본 영상이 없으면 이번 부분 수정 요청은 실행할 수 없으며, 정지 이미지만으로 원본 영상을 대신할 수 없습니다.','Upload the files, select their actual mentions in the interface and replace the prompt placeholders with those labels. Names and syntax vary by tool. Typing a tag alone does not prove a link. Without an actual source video, this local repair cannot be run; a still does not replace that source.')}</p></details>'''),
        ('지원 도구에서 범위와 비용을 확인합니다.','Check the range and cost in a supported tool.',
         'ZCRE 공식 안내의 절차는 원본과 구간을 선택하고, 구간별 설명·참고 자료를 지정한 뒤 범위·예상 크레딧을 확인하는 순서입니다. 실행 화면의 지원 조건을 확인한 뒤 요청하세요.','ZCRE documents selecting a source and range, assigning a description and references per segment, then checking the scope and estimated credits before running. Check the current interface before requesting.',
         f'''<a class="repair-source" href="{EDIT_SOURCE}" target="_blank" rel="noopener noreferrer">{t('ZCRE 공식 · 영상 일부 수정하기','ZCRE official · Local video editing')} ↗</a><p class="repair-small">{t('문서 업데이트 2026.10.16 · 확인 2026.10.17. 부분 수정도 새 생성이며, 나머지가 완전히 같게 남는다는 보장은 없습니다.','Documentation updated 2026.10.16 · Checked 2026.10.17. A local edit is a new generation; unchanged areas are not guaranteed identical.')}</p>'''),
        ('수정 전·안·후를 이어서 검수합니다.','Review before, inside and after the repair.',
         '선택 구간만 보지 말고 0–12초 전체를 정상 속도와 느린 재생으로 확인합니다. 컵이 빨개져도 손이 깨지거나 얼굴·소리가 바뀌면 다시 검토하세요.','Watch the complete 0–12 seconds at normal speed and in slow playback, not just the selection. Even with a red mug, inspect broken hand contact, face drift or audio changes.',
         f'''<details class="repair-detail"><summary>{t('부분 수정보다 전체 재생성을 검토할 때','When to consider full regeneration')}</summary><p>{t('한 소품의 짧은 오류는 부분 수정 후보입니다. 여러 컷에서 얼굴·공간·동작이 동시에 무너졌다면 수정 요청을 계속 겹치기보다 기준 이미지와 장면 계획을 다시 정리하고 전체 재생성을 비교하세요. 이는 이 강좌의 판단 제안이며 결과나 비용 우위를 보장하지 않습니다.','A brief prop defect is a candidate for local repair. If identity, geography and action fail across multiple shots, revisit the references and scene plan and compare full regeneration before stacking more repairs. This is an editorial decision guide, not a promise about results or cost.')}</p></details>'''),
    ]
    step_html = ''.join(f'<li class="repair-step"><div><h3>{t(a,b)}</h3><p>{t(c,d)}</p>{extra}</div></li>' for a,b,c,d,extra in steps)
    workflow = f'''<section class="repair-section" id="repair-workflow"><p class="section-eyebrow">01–05 / DEFINE · REPAIR · REVIEW</p><h2>{t('실행 전에, 다섯 칸만 정리하세요.','Set out five decisions before running.')}</h2><ol class="repair-steps">{step_html}</ol></section>'''

    bad_good = f'''<div class="repair-pair"><div><p class="section-eyebrow">TOO VAGUE</p><h3>{t('“어색한 부분을 자연스럽게 고쳐 줘.”','“Fix the awkward parts naturally.”')}</h3><p>{t('오류의 위치·대상·보존 기준이 없어 무엇을 바꿨는지 비교하기 어렵습니다.','No time, object or preservation standard: it is hard to compare what changed.')}</p></div><div><p class="section-eyebrow">ONE OBSERVABLE CHANGE</p><h3>{t('“4–7초 컵의 파란색만 빨간색으로.”','“At 4–7 seconds, change only the blue mug to red.”')}</h3><p>{t('인물·봉투·손 접촉·카메라·빛·원본 소리를 유지하도록 요청하고 실제 결과를 비교합니다.','Request preservation of the person, envelope, hand contact, camera, light and source sound; compare the actual result.')}</p></div></div>'''
    prompt = f'''<section class="repair-section" id="repair-prompt"><p class="section-eyebrow">ORIGINAL / COMPLETE PRACTICE PROMPT</p><h2>{t('“자연스럽게”를 검수 가능한 문장으로.','Turn “natural” into something you can review.')}</h2>{bad_good}<p>{t('아래는 이 강좌를 위해 작성한 전체 요청서입니다. 먼저 자신의 실제 영상과 멘션, 길이와 오류 구간을 맞추세요. 이 페이지의 콘셉트 두 장은 영상 원본이 아닙니다.','The complete brief below is original to this lesson. First adapt it to your actual video, file mentions, duration and defect. The two concepts on this page are not a source video.')}</p><div class="repair-actions"><a class="repair-download" href="/assets/tutorials/video-repair-prompt-ko.txt" download>{t('한국어 전체 프롬프트 TXT','Complete Korean prompt TXT')} ↓</a><a class="repair-download" href="/assets/tutorials/video-repair-prompt-en.txt" download>{t('영어 전체 프롬프트 TXT','Complete English prompt TXT')} ↓</a></div><details class="repair-detail"><summary>{t('전체 프롬프트 펼치기 · 생략 없음','Read the complete prompt · Unabridged')}</summary><pre class="repair-prompt" tabindex="0"><code>{t(PROMPT_KO,PROMPT_EN)}</code></pre></details><details class="repair-detail"><summary>{t('내 제작 메모로 바꿔 적기','Adapt this into your production notes')}</summary><p>{t('원본 파일 / 오류 시작·끝 / 바꿀 것 하나 / 보존할 것 / 참고 파일의 역할 / 요청 범위 / 비용 확인 / 결과 판정. 이 순서로 메모하면 다음 수정에서 무엇을 바꿨는지 추적하기 쉽습니다.','Source file / defect start and end / one change / preservation goals / reference roles / request range / cost check / review decision. This order helps track what changed on the next attempt.')}</p></details></section>'''

    reviews = [
        ('경계','Boundaries','4초 직전·구간 안·7초 직후에 컵 색이나 위치가 튀지 않나요?','Does mug color or position jump just before 4 s, inside the repair or just after 7 s?'),
        ('손과 물체','Hands and objects','손가락이 손잡이에 붙고 떨어지는 접촉, 컵 형태, 봉투 위치가 자연스러운가요?','Are finger-to-handle contact, mug shape and envelope placement coherent?'),
        ('인물과 연기','Identity and performance','얼굴·머리·올리브색 재킷·시선과 동작이 원본에 맞나요?','Do the face, hair, olive jacket, eyeline and action match the source?'),
        ('촬영과 빛','Picture and light','카메라·구도·길이·비율·반사와 조명에 새 변화가 생기지 않았나요?','Did camera, framing, duration, ratio, reflections or light change unexpectedly?'),
        ('소리와 최종 판단','Sound and the decision','원본 소리의 타이밍·음량·연결을 듣고, 통과·부분 재시도·전체 재설계 중 하나를 기록했나요?','After listening for timing, level and continuity, did you record pass, local retry or scene redesign?'),
    ]
    checklist = ''.join(f'<li><strong>{t(a,b)}</strong> — {t(c,d)}</li>' for a,b,c,d in reviews)
    review = f'''<section class="repair-section" id="repair-review"><p class="section-eyebrow">FIVE CHECKS / KEEP THE SCENE INTACT</p><h2>{t('컵 색이 맞아도, 아직 끝은 아닙니다.','A red mug is only the first check.')}</h2><ol class="repair-review">{checklist}</ol><p class="repair-notice">{t('통과 기준은 “더 예쁜 한 프레임”이 아니라 원본 장면에 필요한 연결입니다. 정지 예시 두 장으로는 시간에 따른 일관성이나 오디오를 검증할 수 없으므로 실제 결과 영상으로 판단하세요.','The standard is continuity needed by the source scene, beyond an attractive frame. Two stills cannot verify consistency over time or audio; assess the actual result video.')}</p></section>'''

    trends = [
        ('01 / LOCAL EDITING','ZCRE · 구간을 지정하는 수정','ZCRE · Specify the interval',
         '구간·설명·참고 자료를 정하고 예상 크레딧을 확인하는 절차를 안내합니다. 수정도 새 생성이므로 보존 결과는 직접 검수해야 합니다.','The guide describes ranges, instructions, references and estimated credits. Edits are new generations, so inspect what was preserved.',
         '문서 업데이트 2026.10.16','Documentation updated 2026.10.16',EDIT_SOURCE,'영상 일부 수정하기','Local video editing'),
        ('02 / DRAFT → FINAL','ZCRE · 초안을 고른 뒤 최종본','ZCRE · Choose a draft, then finalize',
         'Seedance 2.5의 480p 초안과 1080p 최종본은 별도 과금이며 자동 전환되지 않습니다. 최종 요청 기간은 초안 요청 생성부터 7일로 안내합니다. 실행 직전 가능 여부를 확인하세요.','Seedance 2.5 uses separately charged 480p drafts and 1080p finals, without automatic finalization. The guide allows final requests for seven days from draft-request creation; recheck eligibility before running.',
         '문서 업데이트 2026.10.16','Documentation updated 2026.10.16',DRAFT_SOURCE,'초안과 최종본 안내','Draft and final guide'),
        ('03 / MORE CONTROL','Kling 4.0 · 제어점이 늘어나는 방향','Kling 4.0 · More control points',
         '9월 30일 조기 접근 발표는 최대 30초 생성·10개 키프레임·15개 참고 자료를 소개했습니다. 10-bit HDR과 2분 확장은 예고 항목입니다. 실제 계정의 사용 가능 범위는 별도로 확인하세요.','The September 30 early-access announcement describes up to 30 seconds, 10 keyframes and 15 references. It labels 10-bit HDR and two-minute extension as coming soon. Check availability in your account.',
         '발표 게시 2026.09.30','Announcement published 2026.09.30',KLING_SOURCE,'Kling 4.0 공식 발표','Official Kling 4.0 announcement'),
    ]
    trend_cards = ''.join(f'''<article class="repair-trend"><p class="section-eyebrow">{eyebrow}</p><h3>{t(ko,en)}</h3><p>{t(body_ko,body_en)}</p><p class="repair-source-date">{t(date_ko,date_en)}<br>{t('마지막 확인 2026.10.17','Last checked 2026.10.17')}</p><a class="repair-source" href="{url}" target="_blank" rel="noopener noreferrer">{t(link_ko,link_en)} ↗</a></article>''' for eyebrow,ko,en,body_ko,body_en,date_ko,date_en,url,link_ko,link_en in trends)
    news = f'''<section class="repair-section" id="repair-trends"><p class="section-eyebrow">FIELD NOTES / CHECKED 2026.10.17</p><h2>{t('요즘 제작 도구에서 읽을 세 가지 변화.','Three workflow signals in current tools.')}</h2><p>{t('아래는 공식 자료 세 건에서 읽은 제작 방식의 변화입니다. 도구의 인기 순위나 시장 점유율을 뜻하지 않습니다. 구간과 참고의 역할을 나누고, 초안을 검토한 뒤 다음 비용을 결정하는 습관에 연결해 보세요.','These are workflow signals from three official sources, not popularity rankings or market-share findings. Use them to separate ranges and reference roles, review drafts and decide the next expense.')}</p><div class="repair-trends">{trend_cards}</div><p class="repair-small">{t('자료별 게시·업데이트 날짜와 이 글의 확인 날짜를 나누어 표시했습니다. 기능·대상 계정·비용은 달라질 수 있으므로 실제 생성 화면에서 다시 확인하세요. 본문 실습과 프롬프트는 드래곤시네마가 직접 구성했습니다.','Publication or update dates are distinct from this article’s check date. Features, eligible accounts and costs can change; recheck the actual generation interface. The exercise and prompts are original DRA9ON CINEMA work.')}</p></section>'''

    ending = f'''<aside class="tutorial-ending"><p class="section-eyebrow">NEXT / FIX THE PLAN, THEN THE FRAME</p><h2>{t('수정할수록 장면이 흔들린다면, 기준부터.','If repairs unsettle the scene, revisit its reference.')}</h2><div class="tutorial-actions"><a class="button button-white" href="/tutorials/blender-previs/">{t('공간과 동선부터 설계하기','Plan space and blocking')} →</a><a class="button button-glass" href="/tutorials/seedance-2-5/">{t('한 장을 영상으로 만드는 실습','Animate one scene image')} →</a><a class="button button-glass" href="/questions/">{t('부분 수정에 대해 질문하기','Ask about local repair')} →</a></div></aside>'''
    toc = '<nav class="repair-toc" aria-label="'+t('이 강좌의 목차','Lesson contents')+'">'+''.join(f'<a href="#{anchor}">{t(ko,en)}</a>' for anchor,ko,en in [('repair-example','실습 예시','Exercise'),('repair-workflow','수정 순서','Workflow'),('repair-prompt','전체 프롬프트','Complete prompt'),('repair-review','검수표','Review'),('repair-trends','도구 소식','Workflow notes')])+'</nav>'
    body = f'''<body class="watch-page">{header()}<main class="tutorial-main repair-main" id="main"><a class="note-back" href="/tutorials/">← {t('튜토리얼 목록','All tutorials')}</a><p class="section-eyebrow">VIDEO REPAIR / ONE CHANGE AT A TIME</p><h1>{title}</h1><p class="repair-lead">{t('장면 전체를 다시 만들기 전에, 언제 무엇이 틀렸는지 적어 보세요. 짧은 구간의 소품 오류로 변경·보존·검수를 나누는 첫 실습입니다.','Before regenerating a scene, name what went wrong and when. A short prop defect is our first exercise in separating change, preservation and review.')}</p><p class="tutorial-date"><time datetime="{DATE}">2026.10.17</time> · {t('입문 · 정지 콘셉트 2장 · 전체 프롬프트 제공','Beginner · Two still concepts · Complete prompts')}</p>{toc}{example}{workflow}{prompt}{review}{news}{ending}</main>{footer()}</body></html>'''
    schema = {'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'url':origin+PATH,'image':[origin+ART,origin+SOURCE_ART],'inLanguage':'ko','datePublished':DATE,'dateModified':DATE,'author':{'@type':'Organization','name':'DRA9ON CINEMA'}}
    t(TITLE_KO+' | DRA9ON CINEMA', TITLE_EN+' | DRA9ON CINEMA')
    document_head = head(title+' | DRA9ON CINEMA',desc,PATH,schema).replace('property="og:type" content="video.episode"','property="og:type" content="article"')
    share_alt = t('비 오는 카페의 인물과 빨간 머그컵을 보여주는 AI 영상 수정 목표 정지 콘셉트', 'AI still concept for a video-repair target: an adult and a red mug in a rainy cafe')
    social_values = {'og:image':origin+SHARE_ART, 'twitter:image':origin+SHARE_ART,
                     'og:image:width':'1600', 'og:image:height':'900',
                     'og:image:alt':share_alt, 'twitter:image:alt':share_alt}

    def replace_social_meta(match):
        tag = match.group(0)
        key = re.search(r'\b(?:property|name)="([^"]+)"', tag)
        if not key or key.group(1) not in social_values:
            return tag
        value = escape(social_values[key.group(1)], quote=True)
        return re.sub(r'\bcontent="[^"]*"', lambda _: 'content="'+value+'"', tag, count=1)

    document_head = re.sub(r'<meta\b[^>]*>', replace_social_meta, document_head)
    target = out/PATH.strip('/')
    target.mkdir(parents=True,exist_ok=True)
    (target/'index.html').write_text(document_head.replace('</head>',STYLE+'</head>')+body,encoding='utf-8')
    downloads = out/'assets'/'tutorials'
    downloads.mkdir(parents=True,exist_ok=True)
    (downloads/'video-repair-prompt-ko.txt').write_text(PROMPT_KO+'\n',encoding='utf-8')
    (downloads/'video-repair-prompt-en.txt').write_text(PROMPT_EN+'\n',encoding='utf-8')
