"""Small, localised casting form; only public configuration reaches the browser."""
from html import escape as e
from pathlib import Path
import json
from actors_content import ACTORS, row

ROOT=Path(__file__).resolve().parent
COPY={
 'cta':row('섭외·협업 문의','Casting & collaboration','出演・コラボのお問い合わせ','Casting y colaboración'),
 'company':row('회사명','Company','会社名','Empresa'),
 'contact':row('담당자','Contact name','担当者','Persona de contacto'),
 'email':row('이메일','Email','メールアドレス','Correo electrónico'),
 'actor':row('원하는 배우','Actor','希望する俳優','Actor deseado'),
 'purpose':row('용도','Project type','用途','Tipo de proyecto'),
 'advertising':row('광고','Advertising','広告','Publicidad'),
 'music-video':row('뮤직비디오','Music video','ミュージックビデオ','Videoclip'),
 'other':row('기타','Other','その他','Otro'),
 'message':row('내용','Project details','内容','Detalles del proyecto'),
 'send':row('문의 보내기','Send inquiry','送信する','Enviar consulta'),
 'close':row('닫기','Close','閉じる','Cerrar'),
 'note':row('모든 배우는 DRA9ON CINEMA의 오리지널 AI 캐릭터이며, 무단 상업적 사용을 금지합니다.','All actors are original AI characters of DRA9ON CINEMA. Unauthorized commercial use is prohibited.','すべての俳優はDRA9ON CINEMAのオリジナルAIキャラクターです。無断での商業利用を禁止します。','Todos los actores son personajes originales de IA de DRA9ON CINEMA. Se prohíbe el uso comercial no autorizado.'),
 'privacy':row('개인정보처리방침','Privacy policy','プライバシーポリシー','Política de privacidad'),
 'consent':row('회사명·담당자·이메일·배우·용도·내용을 문의 답변을 위해 운영자 이메일로 전송하는 데 동의합니다.','I agree to send the company, contact name, email, actor, project type and details to the operator by email to answer this inquiry.','お問い合わせへの回答のため、会社名・担当者・メール・俳優・用途・内容を運営者のメールに送信することに同意します。','Acepto enviar la empresa, el contacto, el correo, el actor, el tipo de proyecto y los detalles al correo del responsable para responder a esta consulta.'),
 'processing':row('보안 확인 후 전송 중입니다…','Verifying and sending…','確認して送信しています…','Verificando y enviando…'),
 'challenge':row('아래 보안 확인을 완료한 뒤 보내 주세요.','Complete the security check below before sending.','下のセキュリティ確認を完了してから送信してください。','Completa la verificación de seguridad antes de enviar.'),
 'security-error':row('보안 확인을 불러오지 못했습니다. 콘텐츠 차단·네트워크를 확인하고 다시 시도해 주세요.','The security check could not load. Check content blockers or your connection and retry.','セキュリティ確認を読み込めません。コンテンツブロッカーと接続を確認して再試行してください。','No se pudo cargar la verificación. Revisa los bloqueadores o la conexión e inténtalo de nuevo.'),
 'retry':row('보안 확인 다시 시도','Retry security check','セキュリティ確認を再試行','Reintentar verificación'),
 'success':row('문의가 접수되었습니다. 입력하신 이메일로 답변드리겠습니다.','Your inquiry was received. We will reply to the email you provided.','お問い合わせを受け付けました。入力されたメールに返信します。','Hemos recibido tu consulta. Responderemos al correo indicado.'),
 'error':row('전송하지 못했습니다. 입력 내용은 유지됩니다. 잠시 후 다시 시도하거나 이메일로 문의해 주세요.','The inquiry could not be sent. Your entries are retained. Try again shortly or contact us by email.','送信できませんでした。入力内容は保持されています。しばらくして再試行するかメールでご連絡ください。','No se pudo enviar. Se conservan los datos introducidos. Reinténtalo más tarde o contacta por correo.'),
 'rate':row('요청이 너무 많습니다. 1분 후 다시 시도해 주세요.','Too many requests. Please try again in a minute.','リクエストが多すぎます。1分後に再試行してください。','Demasiadas solicitudes. Inténtalo en un minuto.'),
 'fallback':row('이메일로 문의','Contact by email','メールで問い合わせ','Contactar por correo'),
 'intro':row('프로젝트와 원하시는 배우를 알려주세요. 별도 회원가입은 필요하지 않습니다.','Tell us about your project and preferred actor. No account is required.','企画と希望する俳優をお知らせください。会員登録は不要です。','Cuéntanos tu proyecto y el actor que buscas. No necesitas una cuenta.'),
}

def configuration():
 config=json.loads((ROOT/'casting_config.json').read_text(encoding='utf-8'))
 if config['endpoint']!='https://dra9on-casting.tutorial-metrics.workers.dev/inquiry':raise ValueError('Unexpected casting endpoint')
 if config['enabled'] and (not config['sitekey'] or config['sitekey'].startswith('1x')):raise ValueError('Production Turnstile key required')
 return config

def render(actor,lang,base_path=''):
 config=configuration();t=lambda key:e(COPY[key][lang]);pre=base_path+('' if lang=='ko' else '/en')
 href='#casting-inquiry'
 button='<a class="actor-inquire" data-casting-open href="'+href+'">'+t('cta')+' <span aria-hidden="true">↗</span></a>'
 note='<p class="actor-casting-note">'+t('note')+'</p>'
 fields=''
 for key,typ,limit,autocomplete in [('company','text',120,'organization'),('contact','text',80,'name'),('email','email',254,'email')]:
  fields+='<label>'+t(key)+'<input name="'+key+'" type="'+typ+'" maxlength="'+str(limit)+'" autocomplete="'+autocomplete+'" required></label>'
 options=''.join('<option value="'+a['slug']+'"'+(' selected' if a==actor else '')+'>'+e(a['name'][lang])+'</option>' for a in ACTORS)
 fields+='<label>'+t('actor')+'<select name="actor" required>'+options+'</select></label>'
 purposes=''.join('<option value="'+key+'">'+t(key)+'</option>' for key in ('advertising','music-video','other'))
 fields+='<label>'+t('purpose')+'<select name="purpose" required>'+purposes+'</select></label>'
 labels={key:COPY[key][lang] for key in ('processing','challenge','security-error','success','error','rate')}
 data=' data-endpoint="'+e(config['endpoint'],quote=True)+'" data-sitekey="'+e(config['sitekey'],quote=True)+'" data-labels="'+e(json.dumps(labels,ensure_ascii=False),quote=True)+'"'
 form='<form data-casting-form'+data+'><div class="casting-fields">'+fields+'</div><label>'+t('message')+'<textarea name="message" rows="5" minlength="10" maxlength="4000" required></textarea></label><div class="casting-trap" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div><label class="casting-consent"><input name="consent" type="checkbox" required><span>'+t('consent')+' <a href="'+pre+'/privacy/" target="_blank" rel="noopener">'+t('privacy')+' ↗</a></span></label><div data-casting-turnstile></div><p data-casting-status role="status" aria-live="polite"></p><button type="button" class="casting-retry" data-casting-retry hidden>'+t('retry')+'</button><button class="actor-inquire casting-submit" type="submit">'+t('send')+' <span aria-hidden="true">↗</span></button></form>'
 fallback='<a class="casting-email" href="mailto:guletlaru05@gmail.com?subject='+e('DRA9ON CINEMA Casting — '+actor['name'][lang],quote=True)+'">'+t('fallback')+' ↗</a>'
 # The form remains unavailable until the live backend and real widget are configured.
 if not config['enabled']:form='<p>'+t('error')+'</p>'
 section='<section id="casting-inquiry" class="actor-casting"><p class="section-eyebrow">CASTING / COLLABORATION</p>'+button+note+'</section>'
 dialog='<dialog id="casting-dialog" aria-labelledby="casting-title"><div class="casting-dialog-head"><h2 id="casting-title">'+t('cta')+'</h2><button type="button" data-casting-close aria-label="'+t('close')+'">×</button></div><p class="casting-intro">'+t('intro')+'</p>'+form+fallback+'</dialog>'
 return button+note,section+dialog
