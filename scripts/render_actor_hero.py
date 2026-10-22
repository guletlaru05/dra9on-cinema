"""Reframe the four approved, already-watermarked daily photos; no generation.

The sharp foreground is downscaled from the top 800x840 of each 800x1062
public photo, retaining its existing centre watermark. The same photo fills
the sides with blur. Full-resolution private originals are never published.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageOps, ImageFilter
import json, subprocess, argparse

ROOT=Path(__file__).resolve().parents[1]

def render(work):
 work.mkdir(parents=True,exist_ok=True)
 records=[]
 for i,slug in enumerate(('min-seoa','yeonhwa','yuna','haseul')):
  source=ROOT/'site-assets/assets/actors'/f'{slug}-behind-2.webp'
  with Image.open(source) as photo:
   image=photo.convert('RGB')
   background=ImageOps.fit(image,(1280,720),centering=(.5,.2)).filter(ImageFilter.GaussianBlur(24))
   foreground=image.crop((0,0,800,840));foreground.thumbnail((1280,720),Image.Resampling.LANCZOS)
   background.paste(foreground,((1280-foreground.width)//2,0))
   background.save(work/f'{i:02}.png')
   records.append({'actor':slug,'source':source.relative_to(ROOT).as_posix(),'sourceSize':list(image.size),'foregroundCrop':[0,0,800,840],'output':[1280,720],'existingWatermarkRetained':True})
 common=['ffmpeg','-v','error','-framerate','0.5','-i',str(work/'%02d.png'),'-t','8','-an']
 subprocess.run(common+['-vf','fps=24,format=yuv420p','-c:v','libx264','-preset','slow','-tune','stillimage','-crf','20','-movflags','+faststart','-y',str(work/'05-actors.mp4')],check=True)
 subprocess.run(common+['-vf','fps=24,format=yuv420p','-c:v','libvpx-vp9','-b:v','0','-crf','26','-row-mt','1','-cpu-used','4','-y',str(work/'05-actors.webm')],check=True)
 subprocess.run(common+['-vf','scale=640:360:flags=lanczos,fps=24,format=yuv420p','-c:v','libx264','-preset','slow','-tune','stillimage','-crf','22','-movflags','+faststart','-y',str(work/'05-actors-mobile.mp4')],check=True)
 with Image.open(work/'00.png') as image:image.save(work/'05-actors.jpg',quality=92,optimize=True)
 config=json.loads((ROOT/'hero_rotation_config.json').read_text(encoding='utf-8'));clip=config['clips'][4]
 for key,name in {'mp4':'05-actors.mp4','webm':'05-actors.webm','mobile':'05-actors-mobile.mp4','poster':'05-actors.jpg'}.items():
  data=(work/name).read_bytes();assert len(data)<1_000_000,(name,len(data))
  p=Path(name);filename=p.stem+'.'+sha256(data).hexdigest()[:12]+p.suffix
  (ROOT/'site-assets/assets/hero'/filename).write_bytes(data)
  clip['files'][key]=filename;clip['bytes'][key]=len(data)
 clip['dimensions']={'desktop':[1280,720],'mobile':[640,360]}
 clip['composition']='Approved daily photos, upper-body landscape framing with same-photo blurred sides; existing watermarks retained.'
 for item in config['clips']:
  item['focus']={'desktop':'50% 0%' if item['id']=='05-actors' else '50% 15%','mobile':'50% 0%' if item['id']=='05-actors' else '50% 15%'}
  item['fit']='cover' if item['id']=='05-actors' else 'contain'
 (ROOT/'hero_rotation_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (work/'render-provenance.json').write_text(json.dumps({'frames':records,'clip':clip},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(clip,ensure_ascii=False,indent=2))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('work',type=Path);render(parser.parse_args().work.resolve())
