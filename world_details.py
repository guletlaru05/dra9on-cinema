"""Released-episode introductions and verified character roles; no hidden reveals."""
from html import escape
from hashlib import sha256
import json

COPY=[
 ('세계관','World','作品世界','Universo'),('주연','Lead character','主人公','Protagonista'),('조연','Supporting characters','物語を支える人々','Personajes secundarios'),
 ('시즌 1·2, 열두 편의 여정.','Twelve episodes. Two seasons.','二つのシーズン、十二の物語。','Doce episodios. Dos temporadas.'),
 ('회차마다 달라지는 공간과 싸움을 실제 영상 스틸로 살펴봅니다. 결말과 숨겨진 정체는 본편에 남겨둡니다.','Explore the changing settings and conflicts through stills from each released episode. Endings and hidden identities remain in the films.','各話の実際のスチルで、舞台と戦いの変化をたどります。結末や隠された正体は、本編でお楽しみください。','Recorre los escenarios y conflictos con imágenes de cada episodio. Los desenlaces y las identidades ocultas quedan para las películas.'),
 ('회차 보기 →','Watch episode →','この話を見る →','Ver episodio →'),('등장인물','Characters','登場人物','Personajes'),('시즌별 이야기','Season journeys','シーズンの物語','Historia por temporadas'),('관계도','Connections','人物関係','Relaciones'),
 ('사진을 누르면, 이어지는 관계가 보입니다.','Select a portrait to explore the connections.','写真を選ぶと、つながりが見えてきます。','Selecciona un retrato para descubrir sus vínculos.'),
 ('707 대원들','Unit 707','707部隊','Unidad 707'),('조선의 인연','Connections in Joseon','朝鮮で結ばれた縁','Vínculos en Joseon'),('목포진','Mokpojin','モクポジン','Mokpojin'),('검은 종','The black bell','黒い鈴','La campana negra'),
 ('처음 보는 분께. FALL 707 세계관과 인물 관계부터 살펴보세요.','New here? Explore the world and characters of FALL 707.','初めての方へ。FALL 707の世界と人物関係からどうぞ。','¿Primera visita? Descubre el mundo y los personajes de FALL 707.'),
 ('궁궐과 목포진의 사람들','People of the palace and Mokpojin','宮殿とモクポジンの人々','Las personas del palacio y Mokpojin'),
 ('유나 · 시즌 2 EP.06 액션 스틸','Yuna · Season 2 EP.06 action still','ユナ・シーズン2第6話のアクションスチル','Yuna · Imagen de acción de la temporada 2, episodio 6'),
]
CAST=[
 ('sergeant-han',('한 중사 · 707 돌격대원','Sergeant Han · 707 assault operator','ハン軍曹・707部隊突撃隊員','Sargento Han · Operador de asalto del 707'),('민서아와 함께 작전에 투입된 돌격대원. 사라진 동료들을 찾는 대위의 여정에서 빼놓을 수 없는 인물이다.','An assault operator deployed with Min Seo-a. He is central to the captain’s search for her missing teammates.','ミン・ソアと作戦に参加した突撃隊員。行方不明の仲間を捜す大尉の旅に、欠かせない存在だ。','Operador de asalto que participó en la misión de Min Seo-a. Es una figura central en la búsqueda de sus compañeros desaparecidos.')),
 ('sergeant-kim',('김 중사 · 707 의무·통신 대원','Sergeant Kim · 707 medic and communications operator','キム軍曹・707部隊衛生通信担当','Sargento Kim · Sanidad y comunicaciones del 707'),('민서아의 팀에서 의무와 통신을 맡은 여성 대원. 동료를 끝까지 포기하지 않으려는 대위의 선택과 이어져 있다.','The woman responsible for medical support and communications in Min Seo-a’s team. Her story is tied to the captain’s refusal to abandon her people.','ミン・ソアのチームで衛生と通信を担う女性隊員。仲間を見捨てない大尉の決意と、その物語は結ばれている。','Mujer encargada del apoyo médico y las comunicaciones del equipo. Su historia está ligada a la decisión de la capitana de no abandonar a los suyos.')),
 ('yuna',('유나 · 새로운 동행','Yuna · A new companion','ユナ・新たな同行者','Yuna · Una nueva compañera'),('연화와 인연이 있는 소녀. 민서아의 싸움에 합류하며, 익숙한 무기만으로 설명할 수 없던 세계를 더 넓혀 보인다.','A girl connected to Yeonhwa. Her arrival in Min Seo-a’s struggle opens another side of a world that familiar weapons cannot explain.','ヨンファと縁のある少女。ミン・ソアの戦いに加わり、現代の武器だけでは説明できない世界の一面を見せる。','Una joven vinculada a Yeonhwa. Al incorporarse a la lucha de Min Seo-a, revela otra faceta de un mundo que las armas modernas no pueden explicar.')),
 ('elder-shaman',('할머니 무당 · 오래된 인연','The elder shaman · An old connection','老巫女・古くからの縁','La anciana chamana · Un vínculo del pasado'),('조선에 떨어진 민서아를 치료했던 노년의 무당. 낯선 시대에서 살아가는 대위가 치료와 주술을 통해 만나게 되는 인물이다.','The elderly shaman who treated Min Seo-a after her arrival in Joseon. Treatment and spiritual practices connect her to the captain’s life in an unfamiliar era.','朝鮮に落ちたミン・ソアを治療した老巫女。治療と呪術を通じて、見知らぬ時代を生きる大尉と関わっていく。','La anciana chamana que atendió a Min Seo-a tras su llegada a Joseon. Los cuidados y las prácticas espirituales la vinculan con la vida de la capitana en una época desconocida.')),
 ('bell-shaman',('눈을 가린 무당 · 검은 종','The blindfolded shaman · The black bell','目隠しの巫女・黒い鈴','La chamana de los ojos vendados · La campana negra'),('검은 종과 기이한 위협의 중심에 서 있는 무당. 그녀가 무엇을 원하며, 어떤 과거를 지녔는지는 이야기 속에서 드러난다.','A shaman at the center of the black bell and its unnatural threat. What she wants, and the past she carries, unfold within the story.','黒い鈴と異様な脅威の中心にいる巫女。何を望み、どんな過去を背負っているのかは、物語の中で明らかになる。','Una chamana en el centro de la amenaza de la campana negra. Sus deseos y el pasado que arrastra se descubren dentro de la historia.')),
 ('king',('왕 · 조선의 궁궐','The king · The Joseon court','王・朝鮮の宮廷','El rey · La corte de Joseon'),('민서아와 이서가 향하는 궁궐의 군주. 조정을 둘러싼 움직임과 밤의 위협 속에서 왕실의 판단이 이야기에 영향을 미친다.','The ruler of the palace Min Seo-a and Iseo turn to. Decisions at court shape events as political pressure and a threat in the night gather around the royal household.','ミン・ソアとイソが訪れる宮殿の君主。朝廷の動きと夜の脅威の中で、王室の判断が物語を動かしていく。','El soberano del palacio al que acuden Min Seo-a e Iseo. Las decisiones de la corte influyen en los acontecimientos entre la presión política y la amenaza de la noche.')),
 ('commander',('통제사 · 목포진의 지휘관','The naval commander · Mokpojin','統制使・モクポジンの指揮官','El comandante naval · Mokpojin'),('연화의 아버지이자 수군을 이끄는 지휘관. 딸의 안위와 목포진의 사건을 통해 민서아의 검은 종 추적과 연결된다.','Yeonhwa’s father and a naval commander. Concern for his daughter and events in Mokpojin connect him to Min Seo-a’s pursuit of the black bell.','ヨンファの父で、水軍を率いる指揮官。娘の安否とモクポジンの事件を通じて、ミン・ソアの黒い鈴の追跡と関わっていく。','Padre de Yeonhwa y comandante naval. La preocupación por su hija y los sucesos de Mokpojin lo conectan con la búsqueda de la campana negra.')),
 ('commanders-wife',('통제사 부인 · 목포진의 가족','The commander’s wife · A family in Mokpojin','統制使の妻・モクポジンの家族','La esposa del comandante · Una familia en Mokpojin'),('목포진 저택에서 가족의 안위를 걱정하는 인물. 전투의 바깥에 있는 일상과 지켜야 할 사람들의 자리를 보여준다.','A woman concerned for her family in the Mokpojin household. She represents the everyday lives and people beyond the battlefield who must be protected.','モクポジンの屋敷で家族の身を案じる人物。戦場の外にある日常と、守るべき人々の暮らしを映し出す。','Una mujer preocupada por su familia en la residencia de Mokpojin. Representa la vida cotidiana y a las personas que necesitan protección lejos del combate.')),
]
EPISODES=[
 (1,1,('현대의 작전, 사라진 대위','A mission in the present','現代の作戦、消えた大尉','Una misión en el presente'),('707의 작전 현장에서 민서아와 동료들이 움직인다. 예기치 못한 폭발은 익숙했던 전장을 전혀 다른 시대로 이어 놓는다.','Min Seo-a and her teammates carry out a 707 operation. An unexpected explosion turns a familiar battlefield into the beginning of a journey across eras.','707部隊の作戦に臨むミン・ソアと仲間たち。予期せぬ爆発が、見慣れた戦場を別の時代へ続く道に変える。','Min Seo-a y sus compañeros participan en una operación del 707. Una explosión inesperada convierte el campo de batalla en el comienzo de un viaje entre épocas.')),
 (1,2,('궁궐에서 시작된 만남','An encounter at the palace','宮殿で始まる出会い','Un encuentro en el palacio'),('눈을 뜬 곳은 조선의 궁궐이다. 왕자 이서와 만난 민서아는 자신의 장비도 신분도 낯설게 받아들여지는 시대를 마주한다.','She awakens in a Joseon palace. Meeting Prince Iseo, Min Seo-a discovers an era in which both her equipment and her identity are unfamiliar.','目覚めた場所は朝鮮の宮殿だった。王子イソと出会ったミン・ソアは、装備も身分も通じない時代に向き合う。','Despierta en un palacio de Joseon. Al conocer al príncipe Iseo, Min Seo-a descubre una época en la que ni su equipo ni su identidad resultan familiares.')),
 (1,3,('시장의 추격, 설명할 수 없는 적','A pursuit through the market','市場の追跡、説明できない敵','Una persecución en el mercado'),('쉬어 가던 시장에서 두 사람은 다시 추격에 휘말린다. 사라진 동료를 떠올리는 대위 앞에, 현대의 상식으로 설명할 수 없는 위협이 나타난다.','A pause in the market gives way to another pursuit. As the captain thinks of her missing teammates, she encounters a threat beyond modern understanding.','市場での休息は、再び追跡へと変わる。行方不明の仲間を思う大尉の前に、現代の常識では説明できない脅威が現れる。','Una pausa en el mercado da paso a otra persecución. Mientras recuerda a sus compañeros desaparecidos, la capitana se enfrenta a una amenaza que desafía lo que conoce.')),
 (1,4,('검은 종을 좇아 궁으로','Following the black bell','黒い鈴を追って宮殿へ','Tras la campana negra'),('이서와 민서아는 밤의 위협이 어디에서 시작됐는지 확인하려 궁으로 향한다. 검은 종을 둘러싼 흔적은 조정과 바깥의 싸움을 하나로 잇는다.','Iseo and Min Seo-a head to the palace to trace the threat in the night. Clues surrounding the black bell connect events at court with the conflict outside.','夜の脅威の始まりを確かめるため、イソとミン・ソアは宮殿へ向かう。黒い鈴の手掛かりが、朝廷と外の戦いを結びつけていく。','Iseo y Min Seo-a se dirigen al palacio para rastrear la amenaza de la noche. Las pistas de la campana negra unen los acontecimientos de la corte con la lucha exterior.')),
 (1,5,('궁 안으로 번지는 위협','The threat enters the palace','宮殿の内側へ広がる脅威','La amenaza entra en el palacio'),('궁궐도 더는 안전한 피난처가 아니다. 잃어버린 동료를 그리워하던 민서아는 눈앞의 사람들을 지키기 위해 다시 장비를 갖춘다.','The palace is no longer a safe refuge. Missing the teammates she lost, Min Seo-a takes up her equipment again to protect the people around her.','宮殿も、もはや安全な場所ではない。失った仲間を思うミン・ソアは、目の前の人々を守るため再び装備を身につける。','El palacio deja de ser un refugio seguro. Mientras añora a sus compañeros, Min Seo-a vuelve a equiparse para proteger a quienes la rodean.')),
 (1,6,('궁궐의 마지막 밤','The palace’s last night','宮殿、最後の夜','La última noche del palacio'),('검은 종을 둘러싼 대립이 궁궐의 밤에 모인다. 이서와 민서아는 익숙한 무기와 낯선 힘이 충돌하는 싸움에 들어선다.','The conflict around the black bell converges on the palace at night. Iseo and Min Seo-a enter a battle where familiar weapons meet an unfamiliar power.','黒い鈴をめぐる対立が、夜の宮殿に集まる。イソとミン・ソアは、現代の武器と未知の力がぶつかる戦いに踏み込む。','El conflicto de la campana negra converge en el palacio al caer la noche. Iseo y Min Seo-a entran en una batalla entre armas conocidas y un poder desconocido.')),
 (2,1,('눈길에서 목포진으로','From the snowy road to Mokpojin','雪道からモクポジンへ','Del camino nevado a Mokpojin'),('조선에 머문 지 석 달, 민서아는 겨울 길에서 연화와 인연을 맺는다. 목포진의 가족과 수군을 만난 대위는 다시 검은 종의 흔적을 좇는다.','Three months into her life in Joseon, Min Seo-a meets Yeonhwa on a winter road. Encounters with a family and naval command in Mokpojin lead her back to the black bell.','朝鮮に来て三か月。冬の道でミン・ソアとヨンファの縁が結ばれる。モクポジンの家族と水軍との出会いから、大尉は再び黒い鈴を追う。','Tras tres meses en Joseon, Min Seo-a conoce a Yeonhwa en un camino invernal. Una familia y el mando naval de Mokpojin la conducen de nuevo a la campana negra.')),
 (2,2,('목포진 습격의 밤','The night of the Mokpojin assault','モクポジン襲撃の夜','La noche del asalto a Mokpojin'),('성벽을 넘는 침입자들이 목포진의 밤을 흔든다. 낯선 군인의 장비와 통제사의 가족을 둘러싼 움직임 속에서 위협의 범위가 드러난다.','Intruders crossing the walls shatter the night in Mokpojin. Moves against the unfamiliar soldier’s equipment and the commander’s household reveal the reach of the threat.','城壁を越える侵入者が、モクポジンの夜を揺るがす。異邦の軍人の装備と統制使の家族をめぐる動きが、脅威の広がりを示していく。','Los intrusos cruzan las murallas y sacuden la noche de Mokpojin. Las maniobras en torno al equipo de la soldado y a la familia del comandante revelan el alcance de la amenaza.')),
 (2,3,('구해야 할 사람들','The people she must save','救うべき人々','Las personas que debe rescatar'),('민서아는 연화를 찾기 위해 위험한 장소로 향한다. 제한된 장비와 낯선 지형 속에서 대위는 구출을 위한 길을 살핀다.','Min Seo-a enters dangerous territory in search of Yeonhwa. With limited equipment and unfamiliar terrain, she looks for a way to carry out the rescue.','ヨンファを捜すため、ミン・ソアは危険な場所へ向かう。限られた装備と未知の地形の中で、救出への道を探る。','Min Seo-a entra en territorio peligroso en busca de Yeonhwa. Con equipo limitado y un terreno desconocido, busca una vía para el rescate.')),
 (2,4,('검과 총, 엇갈리는 선택','Blades, rifles and difficult choices','剣と銃、交差する選択','Espadas, rifles y decisiones difíciles'),('구출 현장에 또 다른 칼날이 들어온다. 민서아는 동료와 연화를 지켜야 하는 상황에서 자신이 믿을 수 있는 사람과 방법을 다시 묻게 된다.','Another blade enters the rescue. Trying to protect her teammates and Yeonhwa, Min Seo-a must reconsider whom she can trust and how she can fight.','救出の場に、もう一つの剣が加わる。仲間とヨンファを守るため、ミン・ソアは信じられる相手と戦い方を問い直す。','Una nueva espada entra en el rescate. Para proteger a su equipo y a Yeonhwa, Min Seo-a deberá reconsiderar en quién confiar y cómo luchar.')),
 (2,5,('겨울 숲의 전투','A battle in the winter woods','冬の森の戦い','La batalla del bosque invernal'),('눈 덮인 숲에서 민서아의 전투가 이어진다. 시야와 이동이 제한된 공간에서 주변을 읽고 다음 움직임을 결정해야 한다.','Min Seo-a’s battle continues in the snowy woods. With visibility and movement restricted, she must read her surroundings and choose her next move.','雪に覆われた森で、ミン・ソアの戦いが続く。視界も移動も限られる場所で、周囲を読み次の行動を決めなければならない。','La batalla de Min Seo-a continúa en el bosque nevado. Con visibilidad y movimientos limitados, debe interpretar su entorno y decidir su siguiente paso.')),
 (2,6,('멈추지 않는 구출 작전','The rescue continues','続く救出作戦','El rescate continúa'),('민서아는 대원들에게 다가갈 길을 찾는다. 지휘관으로서 사람들을 지키려는 대위의 선택이 시즌 2의 마지막 싸움으로 이어진다.','Min Seo-a searches for a path to her teammates. Her determination to protect her people leads into the final battle of Season 2.','ミン・ソアは隊員たちへ至る道を探す。人々を守ろうとする指揮官の決意が、シーズン2最後の戦いへつながっていく。','Min Seo-a busca un camino hasta su equipo. Su decisión de proteger a los suyos la conduce a la última batalla de la segunda temporada.')),
]
for _,name,description in CAST:COPY.extend([name,description,tuple(v.split(' · ')[0] for v in name)])
for _,_,name,description in EPISODES:COPY.extend([name,description])
EDGES=[
 ('captain-min','sergeant-han',('팀장 ↔ 돌격대원','Captain ↔ Assault operator','隊長 ↔ 突撃隊員','Capitana ↔ Operador de asalto')),
 ('captain-min','sergeant-kim',('팀장 ↔ 의무·통신 대원','Captain ↔ Medic and communications operator','隊長 ↔ 衛生通信担当','Capitana ↔ Sanidad y comunicaciones')),
 ('captain-min','prince-iseo',('위협에 함께 맞서는 동행','Allies against a shared threat','脅威に立ち向かう仲間','Aliados frente a una amenaza común')),
 ('captain-min','yeonhwa',('신뢰와 보호의 인연','A bond of trust and protection','信頼と守り合う絆','Un vínculo de confianza y protección')),
 ('yeonhwa','yuna',('어린 시절부터 이어진 인연','A connection from childhood','幼い頃から続く縁','Un vínculo desde la infancia')),
 ('captain-min','elder-shaman',('조선에서 치료로 맺어진 인연','A connection through treatment in Joseon','朝鮮で治療を通じて結ばれた縁','Un encuentro ligado a su tratamiento en Joseon')),
 ('captain-min','bell-shaman',('검은 종을 둘러싼 대립','Opposing sides of the black bell','黒い鈴をめぐる対立','Enfrentadas por la campana negra')),
 ('yeonhwa','commander',('딸 ↔ 아버지','Daughter ↔ Father','娘 ↔ 父','Hija ↔ Padre')),
 ('commander','commanders-wife',('목포진의 가족','A family in Mokpojin','モクポジンの家族','Una familia en Mokpojin')),
 ('prince-iseo','king',('조선의 왕실','The Joseon royal family','朝鮮の王室','La familia real de Joseon')),
]
COPY.extend(edge[2] for edge in EDGES)
TRANSLATIONS={row[0]:row[1] for row in COPY}

def photo(out,name,alt):
 metadata=json.loads((out/'assets/world/manifest.json').read_text(encoding='utf-8'))
 folder='world' if name in metadata else 'press'
 path='/assets/'+folder+'/'+name+'.webp';version=sha256((out/path.lstrip('/')).read_bytes()).hexdigest()[:12]
 width,height=(metadata[name]['width'],metadata[name]['height']) if name in metadata else (540,720)
 return f'<img src="{path}?v={version}" width="{width}" height="{height}" alt="{escape(alt,quote=True)}" loading="lazy">'

def cast_html(out):
 result=''
 for name,label,description in CAST:
  result+='<article id="person-'+name+'"'+(' class="world-yuna-feature"' if name=='yuna' else '')+'>'+photo(out,name,label[0])+'<h3>'+label[0]+'</h3><p>'+description[0]+'</p>'
  if name=='yuna':result+='<figure class="world-yuna-action">'+photo(out,'yuna-action','유나 · 시즌 2 EP.06 액션 스틸')+'<figcaption>유나 · 시즌 2 EP.06 액션 스틸</figcaption></figure>'
  result+='</article>'
 return result

def episodes_html(out):
 result='<section class="editorial-section" id="world-episodes"><p class="section-eyebrow">05 / TWELVE EPISODES</p><h2>시즌 1·2, 열두 편의 여정.</h2><p>'+COPY[4][0]+'</p>'
 for season in (1,2):
  result+='<section class="world-season" id="world-season-'+str(season)+'"><h3>SEASON '+str(season)+'</h3><div class="world-episode-grid">'
  for s,episode,name,description in EPISODES:
   if s!=season:continue
   path=f'/watch/fall-707-s{s}-ep{episode}/'
   result+='<article data-world-episode="s'+str(s)+'e'+str(episode)+'">'+photo(out,f's{s}-ep{episode:02}',f'FALL 707 · S{s} EP.{episode:02} · '+name[0])+f'<p class="section-eyebrow">S{s} · EP.{episode:02}</p><h4>'+name[0]+'</h4><p>'+description[0]+'</p><a class="text-button" href="'+path+'">회차 보기 →</a></article>'
  result+='</div></section>'
 return result+'</section>'

def connections_html(out):
 names={'captain-min':'민서아','prince-iseo':'이서','yeonhwa':'연화',**{name:label[0].split(' · ')[0] for name,label,_ in CAST}}
 groups=[('707 대원들',['captain-min','sergeant-han','sergeant-kim']),('조선의 인연',['prince-iseo','yeonhwa','yuna','king','elder-shaman']),('목포진',['commander','commanders-wife']),('검은 종',['bell-shaman'])]
 result='<p class="world-relations-help">사진을 누르면, 이어지는 관계가 보입니다.</p><div class="world-relationship-map">'
 for title,members in groups:
  result+='<section class="world-relation-group"><h3>'+title+'</h3><div class="world-relation-people">'
  for person in members:
   result+='<details class="world-person-connections"'+(' open' if person=='captain-min' else '')+'><summary>'+photo(out,person,names[person])+'<strong>'+names[person]+'</strong><span aria-hidden="true">⌄</span></summary><ul>'
   for first,second,label in EDGES:
    if person not in (first,second):continue
    target=second if first==person else first
    result+='<li><a href="#person-'+target+'">'+names[target]+'</a><span>'+label[0]+'</span></li>'
   result+='</ul></details>'
  result+='</div></section>'
 return result+'</div>'
