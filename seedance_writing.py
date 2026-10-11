"""Beginner-friendly briefs and questions; no claim of extra model features."""
def render(t):
    fields=[
      ('입력·고정','Input and continuity','어떤 이미지를 첨부했나요? 얼굴·옷·배경 중 유지할 것은 무엇인가요?','Which image is attached? What must stay fixed: face, costume or setting?'),
      ('동작·표정','Action and expression','눈이 먼저 오른쪽을 보고, 고개가 천천히 따라가는 식으로 관찰 가능한 행동을 적습니다.','Describe visible behavior: eyes look right first, then the head slowly follows.'),
      ('카메라','Camera','눈높이 와이드에서 허리 위 미디엄으로 직선 이동. 시작·경로·끝을 따로 적습니다.','Eye-level wide to waist-up medium on a straight dolly. State start, path and end separately.'),
      ('빛·무드','Light and mood','왼쪽 창문에서 부드러운 빛. 그림자 쪽 눈은 보이게, 채도는 낮게.','Soft light from the left window. Keep the shadow-side eye visible; use muted color.'),
      ('대사·소리','Dialogue and sound','화자와 정확한 대사를 지정합니다. 대사가 없으면 대사 없음, 음악 없음이라고 적습니다.','Identify the speaker and exact line. If silent, specify no dialogue and no music.'),
      ('끝·금지','Ending and exclusions','시선은 오른쪽에 유지하고 멈춥니다. 얼굴 변경·갑작스러운 컷·자막 추가는 제외합니다.','Hold the gaze right and stop. Exclude identity changes, sudden cuts and added subtitles.'),
    ]
    cards=''.join(f'<article class="qna-card"><p class="section-eyebrow">{i:02}</p><h3>{t(ko,en)}</h3><p>{t(bko,ben)}</p></article>' for i,(ko,en,bko,ben) in enumerate(fields,1))
    ko='''시댄스 2.5 영상 프롬프트 작성을 도와주세요. 아래는 실제 작업 조건입니다.
사용 도구와 화면에 표시된 모드: [예: Dreamina / 이미지 → 영상]
화면에서 선택 가능한 길이·비율·해상도: [직접 확인한 값]
첨부 멘션과 역할: [화면에서 삽입한 이미지 1 멘션] = 시작 씬의 공간·구도·빛 / [화면에서 삽입한 이미지 2 멘션] = 인물 얼굴·머리·의상 기준. 해당 참고 모드가 지원할 때만 사용합니다.
멘션 연결: 최종 문장을 생성 화면에 붙여넣은 뒤 위 자리표시자를 실제 업로드 멘션으로 교체합니다. 일반 글자로 “이미지 1”만 쓰지 않습니다.
우선순위: 인물 외모·의상은 시트, 공간·시작 구도는 씬. 시트의 패널과 스튜디오 배경은 제외합니다.
유지할 것: [얼굴, 헤어스타일, 의상, 공간 구조, 시간대]
보여줄 사건: [한 문장으로 사건을 작성]
인물 동작: [눈 → 고개 → 손 → 몸의 순서와 이동 방향]
표정 변화: [시작 표정 / 계기 / 끝 표정]
카메라: [시작 샷과 높이 / 이동 경로와 속도 / 끝 샷]
빛과 무드: [광원 방향과 부드러움 / 그림자 / 채도]
대사: [화자: “정확한 한국어 대사” / 없으면 대사 없음]
소리: [현장음 / 음악 유무]
마지막 상태: [다음 컷에 이어질 시선, 손 위치, 구도]
피할 것: [갑작스러운 컷, 얼굴 변경, 과장 표정, 임의 자막 등]
부족한 조건은 먼저 질문하고, 없는 기능은 추정하지 마세요. 동작과 카메라를 구분하여 해당 길이에 가능한 한 장면으로 정리해 주세요. 최종 프롬프트는 요약하지 말고 전체본으로 작성하고, 왜 그렇게 구성했는지 짧게 설명해 주세요.'''
    en='''Help me write a Seedance 2.5 video prompt using these actual production conditions.
Tool and mode shown in my interface: [e.g. Dreamina / image to video]
Available duration, aspect ratio and resolution: [values verified in my interface]
Inserted mentions and roles: [inserted image 1 mention] = opening space, framing and light; [inserted image 2 mention] = face, hair and costume, only when supported by this reference mode.
Mention connection: after pasting the final prompt into the generation interface, replace these placeholders by selecting the actual uploaded-reference mentions. Plain text saying “image 1” is not a connected reference.
Priority: sheet for identity and costume; scene for space and opening framing. Exclude sheet panels and studio background.
Keep fixed: [face, hairstyle, costume, spatial layout and time of day]
Scene event: [one sentence]
Character action: [eyes, head, hands, body, movement direction and order]
Expression change: [initial expression / trigger / final expression]
Camera: [starting shot and height / path and speed / ending shot]
Light and mood: [source direction and softness / shadows / saturation]
Dialogue: [speaker: exact line / or no dialogue]
Sound: [ambience / music or no music]
Final state: [gaze, hand position and framing that connect to the next shot]
Avoid: [sudden cuts, identity changes, exaggerated expressions and invented subtitles]
Ask about missing information first; do not invent unavailable features. Separate character action from camera movement and plan one achievable scene for the chosen duration. Write the entire final prompt without summarizing, then briefly explain the decisions.'''
    question_ko='''[시댄스 2.5 질문 예시]
도구·모드: Dreamina, 이미지 → 영상
설정: 화면에서 선택한 [길이 / 비율 / 해상도]
첨부: 창가에 선 인물의 시작 씬 한 장
원하는 결과: 인물은 제자리에 서 있고, 카메라만 눈높이 와이드에서 허리 위 미디엄으로 천천히 접근
현재 문제: 중간에 인물이 걷기 시작하고 얼굴이 달라집니다.
사용한 프롬프트: [실제로 입력한 전체 문장을 붙여넣기]
시도한 수정: “걷지 않음”을 넣었지만 같은 문제가 남았습니다.
질문: 인물 동작과 카메라 이동을 어떤 문장으로 나눠야 할까요? 유지해야 할 조건은 무엇인가요?
참고 결과: [공개 가능한 영상 주소가 있다면 추가 — 개인정보·비공개 파일은 제외]'''
    question_en='''[Example Seedance 2.5 question]
Tool and mode: Dreamina, image to video
Settings: [duration / ratio / resolution actually selected]
Input: one opening scene image of a character by a window
Goal: the character stays in place while the camera slowly approaches from eye-level wide to waist-up medium
Problem: the character starts walking and the face changes mid-shot.
Prompt used: [paste the entire prompt you actually entered]
Repair tried: I added “no walking”, but the same problem remains.
Question: How should I separate character action from camera movement? Which continuity conditions should I preserve?
Example result: [add a publicly shareable video URL if available; exclude private files and personal information]'''
    return f'''<section id="video-writing" class="tutorial-prompt"><p class="section-eyebrow">WRITE / ASK / REPAIR</p><h2>{t('무엇을 적고, 어떻게 질문하나요?','What should I write, and how should I ask?')}</h2><p>{t('“멋있게, 영화처럼”만 적으면 얼굴·동작·카메라가 각자 해석될 수 있습니다. 한 컷을 여섯 항목으로 나누고, 실제 화면에서 선택한 조건을 함께 적으세요.','“Make it cinematic” leaves identity, acting and camera movement open to interpretation. Break one shot into six parts and include the settings actually selected in your interface.')}</p><div class="tutorial-topic-grid">{cards}</div><h3>{t('막연한 지시 → 촬영 가능한 지시','Vague direction → a shootable brief')}</h3><div class="qna-card"><p>{t('막연한 지시: 예쁘게 놀라고 카메라가 멋지게 움직이는 영화 장면.','Vague: A beautiful surprised reaction with cinematic camera movement.')}</p><p>{t('구체적인 지시: 인물은 창가에 그대로 선다. 오른쪽 문에서 소리를 듣고 눈을 먼저 돌린 뒤 고개를 천천히 따른다. 입은 다문 채 눈썹만 미세하게 긴장한다. 카메라는 눈높이 와이드에서 같은 축으로 직선 접근하여 허리 위 미디엄에서 멈춘다. 왼쪽 창문의 부드러운 빛과 낮은 채도를 유지한다. 대사·음악·자막 없음. 마지막에는 오른쪽을 보는 시선과 허리 앞 손 위치를 유지한다.','Specific: The character stays by the window. Hearing a sound at the door on frame right, she moves her eyes first, then slowly turns her head. Her mouth stays closed; only her brows subtly tense. The camera dollies straight along the same axis from eye-level wide, stopping at a waist-up medium. Preserve soft light from the left window and muted color. No dialogue, music or subtitles. End with her gaze right and her hands held at her waist.')}</p></div><details class="tutorial-full-prompt"><summary>{t('GPT·Claude에 프롬프트 작성을 요청하는 전체 양식','Complete template for asking GPT or Claude to write a prompt')}</summary><pre tabindex="0"><code>{t(ko,en)}</code></pre></details><p>{t('GPT·Claude는 문장을 설계하는 도우미입니다. 실제 영상은 생성 도구에서 만듭니다. 여기의 양식은 드래곤시네마가 만든 실습용 가이드이며 모델의 공식 필수 문법이 아닙니다.','GPT and Claude help plan the wording; generate the video in your video tool. This is an original DRA9ON CINEMA practice template, not mandatory official model syntax.')}</p><details class="tutorial-full-prompt"><summary>{t('제작자에게 질문할 때 쓰는 전체 예시','Complete example for asking the creator')}</summary><pre tabindex="0"><code>{t(question_ko,question_en)}</code></pre></details><p>{t('결과가 이상하면 전체 프롬프트와 실패 구간을 알려주세요. “안돼요”보다 “8초부터 인물이 걸어요”가 수정 방향을 찾기 쉽습니다. 대사 문제라면 정확한 대사, 화자, 호흡·멈춤 위치도 적습니다.','When a result fails, include the full prompt and the failing moment. “The character starts walking at 8s” is easier to diagnose than “It does not work”. For dialogue issues, include the exact line, speaker, breaths and pauses.')}</p><a class="button button-white" href="/questions/#ask">{t('이 형식으로 질문 남기기','Ask using this format')} →</a></section>'''
