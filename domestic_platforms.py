"""Source-linked Korean services, grouped by production task."""
ENTRIES=[
 ('Vrew / 브루','Vrew', '자막·컷 편집·텍스트 영상','Subtitles, editing and text-led video',
 '보이저엑스의 서비스입니다. 공식 안내에서 자동 자막, 문서처럼 하는 컷 편집, 텍스트로 영상 만들기를 확인했습니다. 낙하 707의 제작 설명 영상이나 자막 작업에 연결하는 실습을 제안합니다.',
 'A VoyagerX service. Official documentation covers automatic subtitles, text-based editing and text-to-video workflows. Our proposed exercise connects it to production explainers or subtitle work.',
 '짧은 영상 한 컷으로 자막을 만들고, 실제 대사의 시작·끝과 호흡을 대조하세요. 새로 만들기 → 텍스트로 비디오 만들기는 별도 실습으로, 직접 쓴 제작 소개 세 문장을 넣고 이미지·목소리를 확인합니다.',
 'Generate subtitles for one short clip and check speech onset, ending and pauses against the audio. Separately, try New → Text to Video with three original production-introduction sentences and review images and voice.',
 'https://vrew.ai/ko/feature/text-to-video/','https://vrew.ai/ko/'),
 ('VCAT / 브이캣','VCAT','홍보 영상·템플릿 편집','Promotional video and template editing',
 '파이온코퍼레이션의 한국어 도움말에서 영상 시작하기, 기본·고급 편집, 장면 길이와 이미지 변경 안내를 확인했습니다. 영화 장면 생성 모델과 역할을 구분하고 홍보 소재 조립에 활용하는 방법부터 살펴보세요.',
 'Pion Corporation’s Korean help center covers getting started, basic/advanced editing, scene duration and image replacement. Distinguish this production workflow from a cinematic scene-generation model; begin with assembling promotional assets.',
 '직접 만든 썸네일과 장면 이미지 세 장으로 작품 소개를 구성합니다. 컷 길이·텍스트 위치·모바일 가독성을 확인하세요. 도움말의 사용자 가이드 → 영상 시작하기 → 기본편 순서로 읽습니다.',
 'Assemble a film introduction from three original thumbnail/scene images. Check shot length, text placement and mobile readability. Read User Guide → Getting Started with Video → Basics.',
 'https://vcat.ai/help/ko/','https://vcat.ai/'),
 ('GenWave Studio / 젠웨이브','GenWave Studio','가상인간 발표 영상','Virtual-presenter video',
 '현재 홈페이지 제목은 젠웨이브 스튜디오이며 본문에는 플루닛 명칭도 남아 있습니다. 국내 운영 정보와 가상인간 스크립트·배경·타임라인 편집 안내를 확인했습니다. 자유로운 액션 장면 생성과는 다른 용도로 구분합니다.',
 'The current page title says GenWave Studio while its body also uses Ploonet branding. The site lists a Korean operator and a virtual-presenter workflow using scripts, backgrounds and a timeline. Treat it as a different task from free-form action-scene generation.',
 '제작 후기 두 문장으로 발표형 소개를 계획합니다. 공식 안내의 프로젝트 생성 → 스크립트·배경 편집 → 미리보기·내보내기 순서를 확인하세요. 가입이나 생성은 이 가이드에서 진행하지 않았습니다.',
 'Plan a presenter introduction using two original production-note sentences. Follow the documented Create Project → Edit Script/Background → Preview/Export sequence. No account creation or generation was performed for this guide.',
 'https://studio.ploonet.com/main/tutorial','https://studio.ploonet.com/main/')]

def render(t):
    cards=[]
    for name,tool,ko,en,a,b,c,d,guide,home in ENTRIES:
        cards.append(f'''<section class="tutorial-step"><span class="tutorial-number">KR</span><div><p class="section-eyebrow">{tool}</p><h3>{t(name,tool)}</h3><p><strong>{t(ko,en)}</strong></p><p>{t(a,b)}</p><details class="tutorial-explain"><summary>{t('처음 해볼 실습','A first exercise')}</summary><p>{t(c,d)}</p></details><div class="tutorial-actions"><a class="button secondary" href="{guide}" target="_blank" rel="noopener noreferrer">{t('공식 사용법','Official guide')} ↗</a><a href="{home}" target="_blank" rel="noopener noreferrer">{t('공식 사이트','Official website')} ↗</a></div></div></section>''')
    return f'''<section id="korean-platforms"><p class="section-eyebrow">KOREAN SERVICES / 2026.10.11</p><h2>{t('국내 플랫폼도, 작업에 맞게.','Korean services, chosen by task.')}</h2><p>{t('한국어 화면이 있다고 국내 서비스인 것은 아닙니다. 운영 정보와 공식 도움말을 확인한 서비스부터, 장면 생성·편집·발표 영상의 역할을 나누었습니다. 소개는 공식 자료 기반이고 아래 실습은 직접 제안한 계획입니다.','A Korean interface does not establish a Korean operator. These entries use published operator information and official help, and distinguish scene generation, editing and presenter video. Descriptions reference official sources; exercises are our original proposals.')}</p>{''.join(cards)}<p class="tutorial-notice">{t('국내 서비스라고 모든 모델이 자체 개발 모델인 것은 아닙니다. 이 조사에서는 내부 모델 출처나 영화 연기 품질을 검증하지 않았습니다. 무료 체험과 실제 생성·내보내기 비용, 워터마크 조건은 현재 요금 화면을 확인하세요. 가입·결제·영상 생성은 진행하지 않았습니다.','A Korean-operated service does not imply that every model is developed in-house. This research did not verify internal model provenance or film-acting quality. Check current pricing, generation/export costs and watermark conditions. No signup, payment or generation was performed.')}</p></section>'''
