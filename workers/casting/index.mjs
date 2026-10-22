import { EmailMessage } from 'cloudflare:email';
import { handle, DESTINATION } from './core.mjs';
export default {fetch(request,env){return handle(request,env,{
 async verify(secret,response){
  const result=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret,response}),signal:AbortSignal.timeout(10000)});
  if(!result.ok)throw new Error('Verification unavailable');
  return result.json();
 },
 send(raw){return env.CASTING_EMAIL.send(new EmailMessage('casting@dra9oncinema.com',DESTINATION,raw));}
});}};
