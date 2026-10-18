/* Browsing stays in this page: no queries sent, no cookies or saved search history. */
(() => {
 'use strict';
 const root=document.querySelector('[data-tutorial-catalog]');
 if(!root)return;
 const browser=root.querySelector('[data-tutorial-browser]'),list=root.querySelector('[data-tutorial-list]');
 if(!browser||!list)return;
 const cards=[...list.querySelectorAll('.tutorial-preview')];
 const search=browser.querySelector('[data-tutorial-search]'),select=browser.querySelector('[data-topic-select]');
 const clear=browser.querySelector('[data-search-clear]'),status=browser.querySelector('[data-tutorial-result-count]');
 const empty=root.querySelector('[data-tutorial-empty]'),buttons=[...browser.querySelectorAll('[data-topic]')];
 const normalize=value=>value.normalize('NFKC').toLocaleLowerCase().replace(/\s+/g,' ').trim();
 const texts=new Map(cards.map(card=>[card,normalize(card.textContent+' '+card.dataset.searchKeywords)]));
 let topic='all';
 function update(){
  const terms=normalize(search.value).split(' ').filter(Boolean);
  let count=0;
  for(const card of cards){
   const matches=(topic==='all'||card.dataset.topics.split(' ').includes(topic))&&terms.every(term=>texts.get(card).includes(term));
   card.hidden=!matches;if(matches)count++;
  }
  select.value=topic;
  for(const button of buttons)button.setAttribute('aria-pressed',String(button.dataset.topic===topic));
  clear.hidden=!search.value;empty.hidden=count!==0;
  status.textContent=status.dataset.countTemplate.replace('{count}',String(count));
 }
 for(const button of buttons)button.addEventListener('click',()=>{topic=button.dataset.topic;update();});
 select.addEventListener('change',()=>{topic=select.value;update();});
 search.addEventListener('input',update);
 clear.addEventListener('click',()=>{search.value='';update();search.focus();});
 browser.hidden=false;update();
})();
