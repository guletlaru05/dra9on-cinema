"""Official-source Korean creative platforms; exercises are original proposals."""
ENTRIES=[
 ('지크 / ZCRE','ZCRE','캐릭터 시트·씬 이미지·영상 제작','Character sheets, scene images and video',
 '지크 공식 가이드는 참조 자료 업로드, 캐릭터 시트 만들기와 재사용, 첫 이미지·영상 제작, 영상 부분 수정, 캔버스 작업을 안내합니다. 캐릭터에서 씬 이미지, 영상으로 이어지는 제작 흐름부터 살펴보세요.',
 'ZCRE’s official guide covers reference uploads, character-sheet creation and reuse, first images and videos, local video edits and canvas workflows. Begin with the sequence from character to scene to video.',
 '공식 가이드에서 참조 자료 업로드 → 캐릭터 시트 만들기와 재사용 → 첫 이미지 → 첫 영상 순서로 읽습니다. 직접 만든 캐릭터 시트와 배경을 준비하고 각각 외모·의상 기준과 공간·조명 기준으로 구분하세요. 짧은 한 컷에서 얼굴 유지와 이동 방향을 확인한 뒤 부분 수정과 최종 영상 제작을 살펴봅니다.',
 'Read Reference Uploads → Character Sheet Creation and Reuse → First Image → First Video. Prepare an original character sheet and environment image; separate appearance/costume from space/lighting references. Plan one short shot, check identity and movement, then study local editing and final-video workflows.',
 'https://docs.zcre.ai/','https://www.zcre.co.kr/'),
 ('빠나나AI / BBANANA','BBANANA','캐릭터·3D 앵글·조명·시네마 스튜디오','Characters, 3D angles, lighting and Cinema Studio',
 '공식 화면에서 이미지·영상·음성 통합생성, 캐릭터, 캔버스, 3D 앵글과 시네마 스튜디오를 확인했습니다. 3D 앵글은 마네킹으로 포즈·조명·앵글을 잡아 참조 이미지를 만드는 기능입니다. 빠나나AI 플랫폼과 나노바나나 모델은 구분해서 읽으세요.',
 'The official interface lists unified image/video/audio generation, Characters, Canvas, 3D Angles and Cinema Studio. 3D Angles uses a mannequin to plan pose, lighting and camera angle for a reference image. Distinguish BBANANA the platform from Nano Banana models.',
 '캐릭터 메뉴에서 동일 인물의 여러 장면을 계획하고 3D 앵글에서 포즈·조명·카메라 위치를 먼저 정합니다. 같은 의상·배경을 유지한 눈높이 정면과 낮은 측면 구도를 비교하세요. 참조 이미지를 준비한 뒤 통합생성에서 선택한 영상 모델의 지원 입력을 확인하고 짧은 한 컷으로 테스트하는 순서입니다. 현재 화면 옵션을 기준으로 진행하세요.',
 'Plan scenes of the same person in Characters, then establish pose, lighting and camera position in 3D Angles. Compare eye-level frontal and low side-angle compositions with the same costume and environment. Prepare references, inspect supported inputs in Unified Generation, and plan one short test shot using the current interface options.',
 'https://www.bbanana.ai/','https://www.bbanana.ai/')]

def render(t):
    cards=[]
    for name,tool,ko,en,a,b,c,d,guide,home in ENTRIES:
        cards.append(f'''<section class="tutorial-step"><span class="tutorial-number">KR</span><div><p class="section-eyebrow">{tool}</p><h3>{t(name,tool)}</h3><p><strong>{t(ko,en)}</strong></p><p>{t(a,b)}</p><details class="tutorial-explain"><summary>{t('처음 해볼 실습','A first exercise')}</summary><p>{t(c,d)}</p></details><div class="tutorial-actions"><a class="button secondary" href="{guide}" target="_blank" rel="noopener noreferrer">{t('공식 가이드·기능 안내','Official guide / features')} ↗</a><a href="{home}" target="_blank" rel="noopener noreferrer">{t('공식 사이트','Official website')} ↗</a></div></div></section>''')
    return f'''<section id="korean-platforms"><p class="section-eyebrow">KOREAN SERVICES / 2026.10.11</p><h2>{t('국내 플랫폼도, 작업에 맞게.','Korean services, chosen by task.')}</h2><p>{t('지크와 빠나나AI의 캐릭터·씬 이미지·영상 제작 흐름을 살펴봅니다. 설명은 공식 자료와 공개 화면을 기반으로 하며, 아래 실습은 직접 제안한 학습 계획입니다.','Explore character, scene-image and video workflows in ZCRE and BBANANA. Descriptions use official sources and the public interface; exercises are our original study plans.')}</p>{''.join(cards)}<p class="tutorial-notice">{t('국내 서비스라고 모든 모델이 자체 개발 모델인 것은 아닙니다. 이 조사에서는 내부 모델 출처나 영화 연기 품질을 검증하지 않았습니다. 무료 체험과 실제 생성·내보내기 비용, 워터마크 조건은 현재 요금 화면을 확인하세요. 가입·결제·영상 생성은 진행하지 않았습니다.','A Korean-operated service does not imply that every model is developed in-house. This research did not verify internal model provenance or film-acting quality. Check current pricing, generation/export costs and watermark conditions. No signup, payment or generation was performed.')}</p></section>'''
