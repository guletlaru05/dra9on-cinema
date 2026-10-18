import {publicUrl} from './workspace-core.js';
// Session memory only. A late response must never restore a logged-out preview.
export function createLinkPreview({read,onUpdate}){
 let version=0,current='',pending=null,result=null;
 const emit=value=>onUpdate({...value,url:current});
 function select(value){
  let url='';try{url=value.trim()?publicUrl(value.trim()):'';}catch{}
  if(url===current)return url;
  version++;current=url;pending=null;result=null;emit({phase:'idle'});return url;
 }
 async function load(value,{force=false}={}){
  const url=select(value);
  if(!url){emit({phase:'invalid',reason:'공개 HTTPS 링크를 확인하세요.'});return null;}
  if(pending)return pending;
  if(!force&&result)return result;
  const ticket=version;emit({phase:'loading'});
  const task=Promise.resolve().then(()=>read(url)).then(response=>{
   if(ticket!==version||url!==current)return null;
   if(!response||!response.deferred&&!['saved','failed'].includes(response.status)||response.status==='saved'&&(!response.record||typeof response.record.body!=='string'))throw Error('원문 응답 형식을 확인할 수 없습니다.');
   result=response;emit({...response,phase:response.deferred?'deferred':response.status==='saved'?'ready':'failed'});return response;
  }).catch(error=>{
   if(ticket!==version)return null;
   result={deferred:true,reason:'원문 연결을 확인하지 못했습니다. '+error.message};emit({...result,phase:'deferred'});return result;
  }).finally(()=>{if(ticket===version)pending=null;});
  pending=task;return task;
 }
 function clear(){version++;current='';pending=null;result=null;emit({phase:'idle'});}
 return{select,load,clear};
}
