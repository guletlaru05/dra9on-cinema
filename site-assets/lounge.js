(()=>{'use strict';
 const lang=document.documentElement.lang;
 if(lang==='ja'||lang==='es'){
  const rows=[
   ['이야기','Story','物語','Historia'],['제작','Filmmaking','制作','Creación'],['캐릭터','Character','登場人物','Personaje'],['기타','Other','その他','Otros'],
   ['제작자','Creator','制作者','Creador'],['방문자','Visitor','訪問者','Visitante'],['답변 완료','Answered','回答済み','Respondido'],['새 이야기','Post','投稿','Publicación'],['운영자 답변','Creator replied','運営者からの回答','Respuesta del creador'],['제작자 답변','Creator reply','制作者の回答','Respuesta del creador'],
   ['답변 대기','Awaiting reply','回答待ち','Sin responder'],['글을 찾을 수 없습니다. 숨겨졌거나 삭제된 글일 수 있습니다.','Post unavailable. It may have been hidden or removed.','投稿が見つかりません。非表示または削除された可能性があります。','La publicación no está disponible. Puede haberse ocultado o eliminado.'],
   ['공개 답변 작성','Write a public reply','公開回答を書く','Escribir una respuesta pública'],['답변 게시','Publish reply','回答を公開','Publicar respuesta'],['글 숨기기','Hide post','投稿を非表示','Ocultar publicación'],['복원하기','Restore','復元する','Restaurar'],
   ['게시판을 불러오는 중…','Loading the board…','掲示板を読み込み中…','Cargando el tablón…'],['아직 글이 없습니다. 첫 이야기를 남겨주세요.','No posts yet. Start the first conversation.','まだ投稿がありません。最初の話題をどうぞ。','Aún no hay publicaciones. Inicia la conversación.'],
   ['불러온 글 중 이 분야의 글이 없습니다. 이전 글 더 보기를 눌러보세요.','No loaded posts match this topic. Try loading previous posts.','読み込んだ投稿に該当するテーマがありません。以前の投稿もご覧ください。','No hay publicaciones de este tema entre las cargadas. Prueba a cargar anteriores.'],
   ['처리하지 못했습니다. ','Could not complete this request. ','処理できませんでした。','No se pudo completar la solicitud. '],['연결 시간이 초과됐습니다. 다시 시도하세요.','Connection timed out. Please retry.','接続がタイムアウトしました。もう一度お試しください。','La conexión agotó el tiempo de espera. Inténtalo de nuevo.'],
   ['서버가 허용하지 않은 요청입니다. 보안 확인 또는 글쓰기 간격을 확인하고 다시 시도하세요.','The server denied this request. Check security verification or the posting interval and retry.','サーバーがリクエストを拒否しました。セキュリティ確認や投稿間隔を確認してください。','El servidor rechazó la solicitud. Comprueba la verificación de seguridad y el intervalo entre publicaciones.'],
   ['답변을 2자 이상 적어주세요.','Write at least 2 characters.','回答は2文字以上で入力してください。','Escribe al menos 2 caracteres.'],['답변을 공개 게시했습니다.','Reply published.','回答を公開しました。','Respuesta publicada.'],
   ['닉네임·제목은 2자, 내용은 10자 이상 적어주세요.','Use at least 2 characters for nickname and title, and 10 for the post.','名前と件名は2文字以上、本文は10文字以上で入力してください。','Usa al menos 2 caracteres para el apodo y el título, y 10 para el texto.'],
   ['게시하는 중… 창을 닫지 마세요.','Publishing… Keep this page open.','投稿中です。この画面を閉じないでください。','Publicando… Mantén abierta esta página.'],
   ['도배 방지를 위해 이전 글 작성 후 10분 뒤에 게시할 수 있습니다.','To prevent spam, wait 10 minutes after your previous post.','連続投稿防止のため、前の投稿から10分お待ちください。','Para evitar spam, espera 10 minutos desde tu publicación anterior.'],
   ['게시했습니다. 글과 제작자의 답변은 이 게시판에서 볼 수 있습니다.','Posted. Your post and the creator’s reply appear on this board.','投稿しました。本文と制作者の回答はこの掲示板で読めます。','Publicado. Aquí podrás leer tu texto y la respuesta del creador.'],
   ['글을 공개 게시판에서 숨길까요? 보관함에서 복원할 수 있습니다.','Hide this post from the public board? You can restore it from the archive.','公開掲示板から非表示にしますか。保管庫から復元できます。','¿Ocultar esta publicación? Puedes restaurarla desde el archivo.'],
   ['글을 숨겼습니다. 보관함에서 복원할 수 있습니다.','Post hidden. It can be restored from the archive.','投稿を非表示にしました。保管庫から復元できます。','Publicación oculta. Puede restaurarse desde el archivo.'],
   ['게시글을 복원했습니다.','Post restored.','投稿を復元しました。','Publicación restaurada.'],['보관한 글이 없습니다.','No archived posts.','保管した投稿はありません。','No hay publicaciones archivadas.'],
   ['이 계정에는 제작자 관리 권한이 없습니다. 닉네임 글쓰기는 가능합니다.','This account has no creator privileges. Nickname posting is still available.','このアカウントに管理権限はありません。ニックネームでの投稿は可能です。','Esta cuenta no tiene permisos de creador. Puede publicar con un apodo.'],
   ['게시판 불러오기','Load board','掲示板を読み込む','Cargar tablón'],['보안 연결을 준비하고 있습니다…','Preparing the secure connection…','安全な接続を準備中…','Preparando la conexión segura…'],
   ['오늘의 글 · 미답변','Today’s posts · Unanswered','今日の投稿・未回答','Publicaciones de hoy · Sin responder'],['미답변','Unanswered','未回答','Sin responder'],['기존 글 초기 동기화 미완료','Initial board sync incomplete','既存投稿の初期同期が未完了','Sincronización inicial de publicaciones incompleta'],
   ['이 기기의 운영자 전용 알림을 켰습니다. 다른 방문자에게는 보내지 않습니다.','Owner-only alerts are enabled on this device. Visitors do not receive these alerts.','この端末の運営者専用通知をオンにしました。他の訪問者には届きません。','Avisos exclusivos del creador activados en este dispositivo. No se envían a los visitantes.'],
   ['아이폰은 홈 화면에 설치한 앱에서 알림을 켜주세요.','On iPhone, enable alerts from the installed Home Screen app.','iPhoneではホーム画面に追加したアプリから通知をオンにしてください。','En iPhone, activa los avisos desde la aplicación instalada en la pantalla de inicio.'],
   ['알림 서버 배포와 기기 검증이 아직 완료되지 않았습니다.','Notification deployment and device verification are still pending.','通知サーバーの公開と端末確認がまだ完了していません。','El despliegue de notificaciones y la verificación del dispositivo siguen pendientes.'],
   ['알림을 연결하지 못했습니다. 브라우저 권한과 연결 상태를 확인해 주세요.','Could not enable alerts. Check browser permission and your connection.','通知を有効にできませんでした。ブラウザの許可と接続を確認してください。','No se pudieron activar los avisos. Comprueba los permisos y la conexión.'],
   ['이 기기의 게시판 알림을 껐습니다. 새 회차 알림 설정은 유지됩니다.','Board alerts are off on this device. Episode-alert settings are unchanged.','この端末の掲示板通知をオフにしました。エピソード通知の設定は維持されます。','Avisos del tablón desactivados en este dispositivo. Los avisos de episodios no cambian.'],
   ['해제하지 못했습니다. 다시 시도해 주세요.','Could not disable alerts. Please retry.','解除できませんでした。再試行してください。','No se pudieron desactivar. Inténtalo de nuevo.']
  ];
  const map={};for(const row of rows){map[row[0]]=map[row[1]]=row[lang==='ja'?2:3];}
  const previous=window.D9Locale?.translate;window.D9Locale={translate:(ko,en)=>map[ko]||map[en]||previous?.(ko,en)||en};
 }
 const form=document.getElementById('board-form');
 if(form){const q=new URLSearchParams(location.search);if(q.get('topic')==='character'){document.getElementById('board-topic').value='character';const name=q.get('character');const names={'min-seoa':'민서아','sergeant-han':'한 중사','sergeant-kim':'김 중사','prince-iseo':'이서','yeonhwa':'연화','yuna':'유나','hyeolmaek':'혈맥선생','villain-shaman':'빌런 무당','elder-shaman':'할머니 무당'};if(Object.hasOwn(names,name))form.dataset.character=name;}}
 if(form){
  const composer=document.getElementById('ask'),list=document.getElementById('board-list-view'),detail=document.getElementById('board-detail');
  function route(focus=false){
   const writing=location.hash==='#ask',reading=/^#post-[A-Za-z0-9_-]{1,128}$/.test(location.hash);
   composer.hidden=!writing;list.hidden=writing||reading;detail.hidden=!reading;
   if(focus&&writing)composer.querySelector('h2').focus();
  }
  window.addEventListener('hashchange',()=>route(true));route();
 }
 // Delegate to the existing same-page image viewer, keeping original ratios.
 document.querySelectorAll('a.lounge-image').forEach(a=>a.dataset.loungeImage='true');
})();
