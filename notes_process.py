"""Creator-confirmed process and scene companion notes."""
from html import escape

TITLE=('이렇게 만들었습니다','How I made it')
INTRO=('아이디어는 제가 짜고, AI 도구들과 함께 시나리오와 이미지를 구체화했습니다. 제가 사용한 제작 흐름을 정리해 봤습니다.','I developed the ideas, then worked with AI tools to shape the screenplay and images. Here is the workflow I used.')
STEPS=[
('아이디어와 기획','Ideas and planning','이야기의 출발점과 아이디어는 제가 직접 구상했습니다. 밀리터리에서 출발해, 무당 빌런과 좀비들이 중심인 판타지 오컬트 스릴러로 세계를 넓혔습니다.','I came up with the initial concept and ideas myself, expanding a military premise into a fantasy occult thriller centered on a shaman villain and zombies.'),
('시나리오 · Claude와 GPT','Screenplay · Claude and GPT','제가 구상한 아이디어를 바탕으로 Claude와 GPT와 함께 시나리오를 작성했습니다.','I worked with Claude and GPT to write the screenplay from my own ideas.'),
('캐릭터 시트 · GPT Image 2','Character sheets · GPT Image 2','캐릭터 시트는 GPT Image 2로 제작했습니다. 시즌별 의상과 헤어스타일, 인물의 분위기를 이미지로 구체화했습니다.','I created the character sheets with GPT Image 2, defining each season’s costumes, hairstyles and character presence visually.'),
('프롬프트도, 기준부터','A framework for the prompts','프롬프트 스킬을 만들고, 그 스킬을 기준으로 프롬프트를 작성하는 방식으로 작업했습니다.','I built prompt skills and used them as the framework for writing my prompts.'),
('영상 · Seedance 2.0 → 2.5','Video · Seedance 2.0 → 2.5','영상은 Seedance 2.0으로 시작했습니다. 시즌 1의 6화부터는 Seedance 2.5로 제작했습니다.','I began making the videos with Seedance 2.0. Starting with Season 1, Episode 6, I used Seedance 2.5.'),
('제작 이야기를 HTML로','Bringing the story to HTML','이 제작 비하인드도 글과 그림으로 정리하고 HTML 페이지로 구성했습니다. 영상을 보는 것에서 한 걸음 더 들어와, 제가 어떻게 이 이야기를 만들었는지 읽을 수 있는 공간으로 만들고 싶었습니다.','I organized these behind-the-scenes stories into text and illustrations and built them as HTML pages: a place to go beyond watching the films and read how I made them.')]
SCENE_TITLE=('장면과 함께 읽는 이야기','Read alongside the scenes')
SPOILER=('아래 내용에는 공개된 에피소드의 일부 줄거리가 포함되어 있습니다.','The following notes include some plot details from released episodes.')
SCENES={
1:[('군사 작전에서 낯선 조선으로','From a military operation to an unfamiliar Joseon','시즌 1은 현대의 작전 현장에서 시작해 조선으로 무대를 옮깁니다. 민 대위에게는 함께 떨어진 대원들을 찾아야 한다는 목표가 남습니다. 처음의 짧은 타임슬립 아이디어가, 돌아가야 할 사람들과 풀어야 할 의문을 가진 이야기로 이어집니다.','Season 1 moves from a modern military operation into Joseon. Captain Min still needs to find the squad members who fell with her. The short time-slip premise becomes a story about people to bring home and questions to answer.','https://www.youtube.com/watch?v=4f6Zguf7c2M&t=192s'),
('총성과 검은 종이 만나는 순간','Where gunfire meets the black bell','시즌 1 마지막 화에서는 이서가 무당과 맞서고, 민 대위가 쓰러진 이서를 보호합니다. 총탄을 막아내는 검은 연기는 현대식 전투만으로 해결할 수 없는 위협을 보여줍니다. 무당 빌런과 좀비가 중심인 낙하 707의 오컬트 세계가 선명해지는 장면입니다.','In the Season 1 finale, Yi-seo faces the shaman and Min protects the fallen prince. Black smoke stopping bullets reveals a threat that modern combat alone cannot resolve. The scene brings the occult world of FALL 707, with its shaman villain and zombies, into focus.','https://www.youtube.com/watch?v=BY0ZT5SK8qY')],
2:[('쏠 수 없는 적','The enemy she cannot shoot','시즌 2 3화에서 민 대위는 한 중사와 김 중사를 알아보고 이름을 부릅니다. 찾아야 했던 동료들을 앞에 두고, 총을 쏘는 것만으로는 풀 수 없는 상황과 마주합니다. 더 냉정해진 외형 뒤에도 대원들을 되찾으려는 목표는 이어집니다.','In Season 2, Episode 3, Min recognizes Sergeants Han and Kim and calls their names. Facing the comrades she has been searching for, she encounters a situation gunfire cannot solve. Behind her colder appearance, the need to bring her squad back remains.','https://www.youtube.com/watch?v=vrVGZ_HMxQs&t=239s'),
('다시 빼앗긴 동료, 흔들리는 믿음','Comrades lost again, trust shaken','4화에서는 검은 연기 속으로 대원들이 다시 사라지고, 민 대위는 자신을 도왔던 할머니 무당에게 총을 겨눕니다. 5화에서는 밀려오는 악귀들 속에서 동료들을 되돌릴 방법을 찾습니다. 싸움의 규모뿐 아니라, 누구를 믿고 누구를 구해야 하는지도 이야기의 갈등이 됩니다.','In Episode 4, her squad members disappear into black smoke again, and Min aims at the elderly shaman who once helped her. In Episode 5, she searches for a way to save her comrades as the possessed horde closes in. The conflict is also about whom to trust and whom to save.','https://www.youtube.com/watch?v=bDqEJXYr2dY')]
}
WATCH=('관련 장면 보기 ↗','Watch the related scene ↗')
TRANSLATIONS=dict([TITLE,INTRO,SCENE_TITLE,SPOILER,WATCH])
for ko,en,kob,enb in STEPS: TRANSLATIONS.update({escape(ko):escape(en),escape(kob):escape(enb)})
for items in SCENES.values():
 for ko,en,kob,enb,url in items: TRANSLATIONS.update({ko:en,kob:enb})

def render(season):
 out=f'<section class="note-process"><p class="section-eyebrow">SCENE NOTES</p><h2>{SCENE_TITLE[0]}</h2><p class="note-disclosure">{SPOILER[0]}</p>'
 for ko,en,kob,enb,url in SCENES[season]:
  out+=f'<article><h3>{escape(ko)}</h3><p>{escape(kob)}</p><a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{WATCH[0]}</a></article>'
 out+=f'</section><section class="note-process"><p class="section-eyebrow">MY WORKFLOW</p><h2>{TITLE[0]}</h2><p>{INTRO[0]}</p><ol>'
 for ko,en,kob,enb in STEPS:out+=f'<li><h3>{escape(ko)}</h3><p>{escape(kob)}</p></li>'
 return out+'</ol></section>'
