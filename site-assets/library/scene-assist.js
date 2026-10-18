// Local suggestions, not a live model catalogue or AI generation.
export function recommendSettings(scene,kind){
 const video=kind==='영상',text=String(scene||''),tags=[];
 for(const [tag,rx] of [['카메라',/구도|카메라|클로즈업|렌즈|뒤돌|camera|lens/i],['조명',/조명|빛|어둠|밤|명암|역광|shadow|light|night/i],['캐릭터 일관성',/일관|시트|같은 인물|같은 얼굴|identity|sheet/i],['액션',/액션|추격|전투|달리|싸움|fight|chase|action/i],['분위기',/무드|분위기|시네마틱|비 오는|긴장|mood|cinematic/i]])if(rx.test(text))tags.push(tag);
 const model=video?'Seedance 2.5':/글자|문구|텍스트|타이포|text|lettering/i.test(text)?'GPT Image 2.5 (Higgsfield)':'Midjourney (ZCRE)';
 const ratio=/9\s*:\s*16|쇼츠|릴스|세로|shorts|reels|vertical/i.test(text)?'9:16':/1\s*:\s*1|정사각|square/i.test(text)?'1:1':/4\s*:\s*5/.test(text)?'4:5':'16:9';
 return{model,ratio,tags,reason:video?'영상 초안용 모델을 추천했습니다.':model.startsWith('GPT')?'텍스트가 필요한 이미지 초안용 모델을 추천했습니다.':'시네마틱 이미지 초안용 모델을 추천했습니다.'};
}
export function incompatibleModel(kind,model){return kind==='영상'?/midjourney|gpt.?image|seedream|nano.?banana/i.test(model):/^seedance|^kling/i.test(model);}
