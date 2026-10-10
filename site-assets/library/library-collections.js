export function threadsSource(item){
 for(const link of item.links||[]){try{const url=new URL(link.url);if(['threads.com','www.threads.com','threads.net','www.threads.net'].includes(url.hostname))return {url:link.url,author:url.pathname.split('/').find(x=>x.startsWith('@'))||'작성자 확인 필요'};}catch{}}
 return null;
}
export function collectionOf(item){if(item.title.startsWith('야장시단 · '))return 'guidebook';if(threadsSource(item))return 'threads';return 'tutorial';}
