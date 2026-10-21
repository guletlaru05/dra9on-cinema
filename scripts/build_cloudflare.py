"""Build the same public site on Pages without moving credentials or DNS."""
from pathlib import Path
import json,os,re,subprocess,sys
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]

def configuration(env):
 stage=env.get('D9_DEPLOYMENT_STAGE','preview')
 if stage not in ('preview','production'):raise ValueError('Unknown deployment stage')
 origin=env.get('SITE_ORIGIN','').rstrip('/')
 url=urlsplit(origin)
 if url.scheme!='https' or url.username or url.password or url.port or url.path or url.query or url.fragment:
  raise ValueError('SITE_ORIGIN must be an HTTPS origin')
 if stage=='preview' and url.hostname!='dra9on-cinema.pages.dev':raise ValueError('Only the fixed preview host is allowed')
 if stage=='production' and origin!='https://dra9oncinema.com':raise ValueError('Production origin must remain the canonical domain')
 revision=env.get('CF_PAGES_COMMIT_SHA') or env.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 if not re.fullmatch('[a-f0-9]{40}',revision):raise ValueError('Missing Git commit revision')
 return stage,origin,revision

def finalize(out,stage,origin,revision):
 pages=list(out.rglob('*.html'))
 if stage=='preview':
  for page in pages:
   html=page.read_text(encoding='utf-8')
   html=re.sub(r'<meta name="robots" content="[^"]*">','<meta name="robots" content="noindex,nofollow,noarchive">',html)
   if 'name="robots"' not in html:html=html.replace('</head>','<meta name="robots" content="noindex,nofollow,noarchive"></head>',1)
   page.write_text(html,encoding='utf-8')
  (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
 # No API keys, tokens, account contact details or private-library content here.
 record={'revision':revision,'stage':stage,'origin':origin,'htmlPages':len(pages)}
 (out/'deployment.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 feed=json.loads((out/'pwa/episodes.json').read_text(encoding='utf-8'))
 if feed['revision']!=revision:raise ValueError('Episode feed revision differs from deployment')
 return record

def main():
 stage,origin,revision=configuration(os.environ)
 env={**os.environ,'GITHUB_SHA':revision,'YOUTUBE_SNAPSHOT_PATH':str(ROOT/'build-assets/youtube-public.json')}
 if stage=='preview':env.update(CF_WEB_ANALYTICS_TOKEN='',D9_METRICS_ENDPOINT='')
 subprocess.run([sys.executable,'build-portfolio.py','--origin',origin],cwd=ROOT,env=env,check=True)
 subprocess.run([sys.executable,'verify-site.py','--origin',origin],cwd=ROOT,env=env,check=True)
 print(json.dumps(finalize(ROOT/'dist',stage,origin,revision)))

if __name__=='__main__':main()
