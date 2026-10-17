"""Spoiler-light series introduction based on published Seasons 1 and 2."""
from html import escape
from hashlib import sha256

ROUTE='/fall-707/world/'
# Korean / English / Japanese / Spanish. No unpublished story or Season 3 copy.
COPY=[
 ('FALL 707 세계관 | DRA9ON CINEMA','The world of FALL 707 | DRA9ON CINEMA','FALL 707の世界 | DRA9ON CINEMA','El mundo de FALL 707 | DRA9ON CINEMA'),
 ('현대의 전술과 조선의 어둠이 만나는 FALL 707. 시즌 1·2의 배경, 주요 인물과 관계, 이야기의 흐름을 만나보세요.','Modern tactics meet the darkness of Joseon. Explore the settings, central characters and story of FALL 707 Seasons 1 and 2.','現代の戦術と朝鮮王朝の闇が交差するFALL 707。シーズン1・2の舞台、登場人物、関係と物語をご紹介します。','Las tácticas modernas se encuentran con la oscuridad de Joseon. Conoce los escenarios, personajes y vínculos de las dos primeras temporadas de FALL 707.'),
 ('전술은 현대. 밤은 조선.','Modern tactics. Joseon nights.','現代の戦術。朝鮮王朝の夜。','Tácticas modernas. Noches de Joseon.'),
 ('낯선 시대에 떨어진 707 대위. 살아남기 위한 싸움은, 곁에 있는 사람들을 지키는 선택으로 이어진다.','A 707 captain is stranded in another era. Her fight to survive becomes a choice to protect the people beside her.','別の時代に落ちた707部隊の大尉。生き延びるための戦いは、そばにいる人々を守る決意へと変わっていく。','Una capitana del 707 queda atrapada en otra época. Su lucha por sobrevivir se convierte en la decisión de proteger a quienes están a su lado.'),
 ('밀리터리 액션과 판타지 사극이 만나는 오리지널 시리즈. 현대의 장비가 통하지 않는 위협 앞에서 민서아는 조선의 사람들과 함께 길을 찾는다.','An original series where military action meets historical fantasy. Faced with threats her modern equipment cannot explain, Min Seo-a finds her way alongside the people of Joseon.','ミリタリーアクションと時代劇ファンタジーが交わるオリジナルシリーズ。現代の装備だけでは立ち向かえない脅威を前に、ミン・ソアは朝鮮の人々と道を探す。','Una serie original que une acción militar y fantasía histórica. Frente a amenazas que sus armas no pueden explicar, Min Seo-a busca un camino junto a los habitantes de Joseon.'),
 ('두 시대가 만나는 곳.','Where two eras meet.','二つの時代が出会う場所。','Donde se encuentran dos épocas.'),
 ('현대 · 707 특임대','The present · Unit 707','現代・707特殊任務部隊','El presente · Unidad 707'),
 ('작전, 전술, 그리고 동료. 민서아의 출발점은 현대의 전장이다. 익숙했던 장비와 판단은 조선에 도착한 뒤 전혀 다른 의미를 갖는다.','Operations, tactics and comrades. Min Seo-a begins on a modern battlefield. In Joseon, the equipment and instincts she trusts take on an entirely different meaning.','作戦、戦術、そして仲間。ミン・ソアの出発点は現代の戦場だ。朝鮮にたどり着いたとき、頼りにしてきた装備と判断は別の意味を持ち始める。','Operaciones, tácticas y compañeros. Min Seo-a parte de un campo de batalla moderno. En Joseon, el equipo y los instintos en los que confía adquieren otro significado.'),
 ('조선 · 궁궐에서 목포진까지','Joseon · From the palace to Mokpojin','朝鮮・宮殿からモクポジンへ','Joseon · Del palacio a Mokpojin'),
 ('낯선 궁궐에서 시작한 이야기는 겨울의 목포진으로 이어진다. 밤을 깨우는 검은 방울과 보이지 않는 위협이, 서로 다른 시대의 사람들을 같은 싸움으로 이끈다.','The story begins in an unfamiliar palace and continues into winter in Mokpojin. A black bell in the night and an unseen threat draw people from different eras into the same fight.','見知らぬ宮殿から、冬のモクポジンへ。夜を破る黒い鈴と見えない脅威が、異なる時代の人々を同じ戦いへ導いていく。','La historia nace en un palacio desconocido y continúa en el invierno de Mokpojin. Una campana negra y una amenaza invisible unen a personas de épocas distintas en una misma lucha.'),
 ('이야기의 중심에 있는 사람들.','The people at the heart of the story.','物語の中心にいる人々。','Las personas en el centro de la historia.'),
 ('민서아 · 707 대위','Min Seo-a · Captain, Unit 707','ミン・ソア・707部隊大尉','Min Seo-a · Capitana de la Unidad 707'),
 ('조선에 떨어진 현대의 특수부대 장교. 낯선 위협 앞에서도 전술과 판단을 놓지 않으며, 곁의 사람들을 지키기 위해 싸운다.','A modern special forces officer stranded in Joseon. She holds on to her tactical instincts and fights to protect those beside her, even when the threat defies everything she knows.','朝鮮に迷い込んだ現代の特殊部隊将校。常識を越える脅威に直面しても判断力を失わず、そばにいる人々を守るために戦う。','Una oficial de fuerzas especiales atrapada en Joseon. Conserva su instinto táctico frente a lo inexplicable y lucha por proteger a quienes la acompañan.'),
 ('이서 · 조선의 왕자','Iseo · Prince of Joseon','イソ・朝鮮の王子','Iseo · Príncipe de Joseon'),
 ('낯선 시대에서 민서아가 만나는 왕자. 서로 다른 세계에서 온 두 사람은 궁궐을 둘러싼 위협 앞에서 함께 움직이기 시작한다.','The prince Min Seo-a encounters in an unfamiliar era. From different worlds, they begin to act together as a threat gathers around the palace.','見知らぬ時代でミン・ソアが出会う王子。異なる世界で育った二人は、宮殿に迫る脅威を前に、ともに行動を始める。','El príncipe que Min Seo-a conoce en esa época desconocida. Proceden de mundos distintos, pero empiezan a actuar juntos ante la amenaza que rodea al palacio.'),
 ('연화 · 목포진에서 만난 인연','Yeonhwa · A bond in Mokpojin','ヨンファ・モクポジンで結ばれた縁','Yeonhwa · Un vínculo en Mokpojin'),
 ('겨울의 목포진에서 민서아와 인연을 맺는 인물. 두 사람이 쌓아가는 신뢰는, 이어지는 위협 속에서 지켜야 할 소중한 것이 된다.','A woman whose path crosses Min Seo-a’s in winter-bound Mokpojin. The trust they build becomes something worth protecting as danger approaches.','冬のモクポジンでミン・ソアと出会う女性。二人が育む信頼は、迫る危機の中で守るべき大切なものになっていく。','Una mujer cuyo camino se cruza con el de Min Seo-a en el invierno de Mokpojin. La confianza que construyen se convierte en algo que merece ser protegido.'),
 ('서로 다른 시대, 이어지는 인연.','Different eras. Connected lives.','違う時代、つながる縁。','Épocas distintas. Vidas conectadas.'),
 ('함께 위협에 맞서는 동행','Allies against a shared threat','脅威に立ち向かう仲間','Aliados frente a una amenaza común'),
 ('신뢰와 보호의 인연','A bond of trust and protection','信頼と守り合う絆','Un vínculo de confianza y protección'),
 ('이서','Iseo','イソ','Iseo'),('민서아','Min Seo-a','ミン・ソア','Min Seo-a'),('연화','Yeonhwa','ヨンファ','Yeonhwa'),
 ('시즌 1 · 낯선 시대의 시작','Season 1 · Into another era','シーズン1・見知らぬ時代へ','Temporada 1 · Hacia otra época'),
 ('작전 중 사라진 민서아가 조선의 궁궐에서 눈을 뜬다. 이서와의 만남, 밤에 울리는 검은 방울. 돌아갈 길을 찾던 군인은 눈앞의 사람들과 함께 살아남아야 한다.','Min Seo-a disappears during an operation and awakens in a Joseon palace. She meets Iseo; a black bell rings through the night. Searching for a way home, she must survive alongside the people she has just met.','作戦中に消えたミン・ソアが目を覚ましたのは、朝鮮の宮殿だった。イソとの出会い、夜に響く黒い鈴。帰る道を探す大尉は、出会った人々と生き延びなければならない。','Min Seo-a desaparece durante una operación y despierta en un palacio de Joseon. Conoce a Iseo mientras una campana negra rompe la noche. En busca de un regreso, tendrá que sobrevivir junto a quienes acaba de conocer.'),
 ('시즌 2 · 겨울의 목포진','Season 2 · Winter in Mokpojin','シーズン2・冬のモクポジン','Temporada 2 · El invierno de Mokpojin'),
 ('조선에 머문 지 석 달. 민서아와 연화가 자리 잡은 목포진에 새로운 위협이 다가온다. 지켜야 할 사람들과 찾고 싶은 동료 사이에서, 대위의 싸움은 계속된다.','Three months in Joseon. A new threat approaches Mokpojin, where Min Seo-a and Yeonhwa have made a fragile home. Caught between the people she must protect and the comrades she hopes to find, the captain keeps fighting.','朝鮮に来て三か月。ミン・ソアとヨンファが身を寄せるモクポジンに、新たな危機が迫る。守りたい人々と、捜し続ける仲間の間で、大尉の戦いは続く。','Tres meses en Joseon. Una nueva amenaza se acerca a Mokpojin, el frágil hogar de Min Seo-a y Yeonhwa. Entre las personas que debe proteger y los compañeros que espera encontrar, la capitana sigue luchando.'),
 ('이야기 따라가기.','Follow the story.','物語をたどる。','Sigue la historia.'),
 ('시즌 1·2의 공개된 설정과 도입부만 소개합니다. 주요 반전과 결말은 작품에서 확인해 주세요.','An introduction to the released settings and opening premises of Seasons 1 and 2. Discover the major reveals and endings in the films.','シーズン1・2の公開設定と導入部をご紹介しています。大きな謎の答えや結末は、本編でお楽しみください。','Esta introducción recoge los escenarios y puntos de partida de las dos primeras temporadas. Descubre sus grandes revelaciones y desenlaces en las películas.'),
 ('FALL 707 세계관 살펴보기 →','Explore the world of FALL 707 →','FALL 707の世界を見る →','Explora el mundo de FALL 707 →'),
 ('시즌 1부터 보기','Watch from Season 1','シーズン1から見る','Ver desde la temporada 1'),('회차 목록으로 돌아가기','Back to the episode guide','エピソード一覧へ戻る','Volver a la guía de episodios'),
]
TRANSLATIONS={row[0]:row[1] for row in COPY}

def build_world(out,origin,head,header,footer):
 def t(ko):return escape(ko)
 def img(name,alt,width,height,loading='lazy'):
  path='/assets/press/'+name;version=sha256((out/path.lstrip('/')).read_bytes()).hexdigest()[:12]
  return f'<img src="{path}?v={version}" width="{width}" height="{height}" alt="{escape(alt,quote=True)}" loading="{loading}">'
 title,description=COPY[0][0],COPY[1][0]
 body='<main id="main" class="editorial-main world-main"><a class="editorial-back" href="/fall-707/">회차 목록으로 돌아가기</a><header class="world-hero"><div><p class="section-eyebrow">FALL 707: REBOOT / THE WORLD</p><h1>전술은 현대. 밤은 조선.</h1><p class="world-logline">'+COPY[3][0]+'</p><p>'+COPY[4][0]+'</p><a class="button button-white" href="/watch/fall-707-s1-ep1/">시즌 1부터 보기</a></div>'+img('fall707-still-04.webp','FALL 707 · 조선 궁궐에서의 만남',1440,657,'eager')+'</header>'
 body+='<section class="editorial-section" aria-labelledby="world-eras"><p class="section-eyebrow">01 / TWO ERAS</p><h2 id="world-eras">두 시대가 만나는 곳.</h2><div class="world-eras">'
 for image,heading,paragraph in [('fall707-still-02.webp',6,7),('fall707-still-06.webp',8,9)]:body+='<article>'+img(image,COPY[heading][0],1440,678 if heading==6 else 672)+'<h3>'+COPY[heading][0]+'</h3><p>'+COPY[paragraph][0]+'</p></article>'
 body+='</div></section><section class="editorial-section" aria-labelledby="world-people"><p class="section-eyebrow">02 / THE PEOPLE</p><h2 id="world-people">이야기의 중심에 있는 사람들.</h2><div class="world-people">'
 for name,heading,paragraph in [('captain-min',11,12),('prince-iseo',13,14),('yeonhwa',15,16)]:body+='<article>'+img(name+'.webp',COPY[heading][0],540,720)+'<h3>'+COPY[heading][0]+'</h3><p>'+COPY[paragraph][0]+'</p></article>'
 body+='</div></section><section class="editorial-section" aria-labelledby="world-relations"><p class="section-eyebrow">03 / CONNECTIONS</p><h2 id="world-relations">서로 다른 시대, 이어지는 인연.</h2><div class="world-connections"><div class="connection-person">이서</div><div class="connection-line"><span>함께 위협에 맞서는 동행</span></div><div class="connection-person connection-center">민서아</div><div class="connection-line"><span>신뢰와 보호의 인연</span></div><div class="connection-person">연화</div></div></section>'
 body+='<section class="editorial-section" aria-labelledby="world-seasons"><p class="section-eyebrow">04 / THE JOURNEY</p><h2 id="world-seasons">이야기 따라가기.</h2><div class="season-synopses">'
 for heading,paragraph,path in [(23,24,'/watch/fall-707-season-1-full/'),(25,26,'/watch/fall-707-season-2-full/')]:body+='<article><h3>'+COPY[heading][0]+'</h3><p>'+COPY[paragraph][0]+'</p><a class="text-button" href="'+path+'">FALL 707 →</a></article>'
 body+='</div><p class="editorial-note">'+COPY[28][0]+'</p></section></main>'
 schema={'@context':'https://schema.org','@type':'AboutPage','name':title,'description':description,'url':origin+ROUTE,'about':{'@type':'CreativeWorkSeries','name':'FALL 707: REBOOT'}}
 page=head(title,description,ROUTE,schema).replace('property="og:type" content="video.episode"','property="og:type" content="website"').replace('</head>','<link rel="stylesheet" href="/editorial.css"></head>')+'<body class="watch-page">'+header()+body+footer()+'</body></html>'
 target=out/ROUTE.strip('/');target.mkdir(parents=True,exist_ok=True);(target/'index.html').write_text(page,encoding='utf-8')
