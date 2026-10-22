"""Build/verify future API episodes without network, secrets, or public fake data."""
from datetime import datetime, timezone
import io
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import youtube_site
from youtube_sync import timestamp

ROOT=Path(__file__).resolve().parent
TEST_ROOT=ROOT/'.cache'/'integration-tests'


class YouTubeSiteTests(unittest.TestCase):
    def test_thumbnail_materialization_uses_bounded_valid_jpeg_and_fallback(self):
        sample=(ROOT/'site-assets/assets/portfolio/0I75_YXhMSM.jpg').read_bytes()
        TEST_ROOT.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='d9-thumbnail-test-',dir=TEST_ROOT) as temp:
            output=Path(temp)
            self.assertTrue(output.resolve().is_relative_to(ROOT.resolve()))
            work={'id':'syncTest401','image':'/assets/portfolio/syncTest401.jpg',
                  'thumbnail':'https://i.ytimg.com/vi/syncTest401/hqdefault.jpg'}
            with patch.object(youtube_site,'urlopen',return_value=io.BytesIO(sample)):
                youtube_site.prepare_images([work],output,ROOT)
            self.assertTrue((output/work['image'].lstrip('/')).is_file())
            bad={'id':'syncTest402','image':'/assets/portfolio/syncTest402.jpg',
                 'thumbnail':'https://i.ytimg.com/vi/syncTest402/hqdefault.jpg'}
            with patch.object(youtube_site,'urlopen',return_value=io.BytesIO(b'\xff\xd8not a valid JPEG')):
                youtube_site.prepare_images([bad],output,ROOT)
            self.assertEqual(bad['image'],'/assets/og/og-ko.jpg')
            self.assertFalse(list(output.rglob('*.download')))

    def test_future_season_episode_and_full_movie_build_and_verify(self):
        TEST_ROOT.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='d9-api-build-test-',dir=TEST_ROOT) as temp:
            temp=Path(temp);out=temp/'dist';cache=temp/'youtube-api.json'
            self.assertTrue(temp.resolve().is_relative_to(ROOT.resolve()))
            fetched=timestamp(datetime.now(timezone.utc))
            manual=json.loads((ROOT/'portfolio-data.json').read_text(encoding='utf-8'))
            records={video['id']:{'id':video['id'],'apiViewCount':'12345'} for video in manual['videos']}
            def future(video_id,season,episode,day,category=None):
                return {'id':video_id,'title':f'FALL 707: REBOOT S{season} EP.{episode} | A Test Signal | 테스트 신호 {season}',
                    'description':f'공개되지 않는 빌드 테스트용 설명 {season}.',
                    'uploadDate':f'2026-12-{day:02}T00:00:00Z','seconds':723,'duration':'12:03',
                    'thumbnail':f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg','isEmbeddable':True,
                    'season':season,'episode':episode,'category':category or f's{season}',
                    'nameEn':f'A Test Signal {season}','summaryEn':'A private automated build fixture.',
                    'apiViewCount':'0' if season==4 else '123456789012345'}
            # Keep this synthetic future release beyond authored Season 3 entries.
            next_episode=max([video.get('episode',0) for video in manual['videos'] if video.get('season')==3]+[2])+1
            records['syncTest302']=future('syncTest302',3,next_episode,1)
            records['syncTest401']=future('syncTest401',4,1,2)
            records['syncTest4FL']=future('syncTest4FL',4,0,3,category='full')
            snapshot={'schemaVersion':1,'status':'ready','fetchedAt':fetched,
                      'channel':{'id':'UC'+'a'*22,'subscriberCount':'13800'},'videos':records}
            cache.write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf-8')
            image_dir=out/'assets/portfolio';image_dir.mkdir(parents=True)
            for video_id in ['syncTest302','syncTest401','syncTest4FL']:
                shutil.copyfile(ROOT/'site-assets/assets/portfolio/0I75_YXhMSM.jpg',image_dir/(video_id+'.jpg'))
            env=dict(os.environ,YOUTUBE_SNAPSHOT_PATH=str(cache),D9_TEST_REGISTRY_ROOT=str(temp/'registry-root'),PYTHONUTF8='1')
            env.pop('CF_WEB_ANALYTICS_TOKEN',None);env.pop('D9_METRICS_ENDPOINT',None)
            wrapper=('import os,pathlib,runpy,sys,tutorial_metrics; '
                     'tutorial_metrics.ROOT=pathlib.Path(os.environ["D9_TEST_REGISTRY_ROOT"]); '
                     'sys.argv=["build-portfolio.py","--origin","https://dra9oncinema.com","--output",sys.argv[1]]; '
                     'runpy.run_path("build-portfolio.py",run_name="__main__")')
            result=subprocess.run([sys.executable,'-c',wrapper,str(out)],cwd=ROOT,env=env,
                                  capture_output=True,text=True,encoding='utf-8',timeout=180)
            self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
            checked=subprocess.run([sys.executable,'verify-site.py','--origin','https://dra9oncinema.com','--directory',str(out)],
                                   cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
            self.assertEqual(checked.returncode,0,checked.stdout+'\n'+checked.stderr)
            home=(out/'index.html').read_text(encoding='utf-8')
            # New releases lead the episode shelf; the approved hero reel stays
            # tied to its own footage rather than relabeling an old clip as S4.
            latest=re.search(r'<section[^>]*id="latest-episodes"[^>]*>([\s\S]*?)</section>',home)[1]
            self.assertEqual(re.search(r'data-home-episode="([^"]+)"',latest)[1],'syncTest401')
            self.assertIn('S4 · EP.01',latest)
            self.assertIn('data-category="s4"',home)
            self.assertIn('/watch/fall-707-s4-ep1/',home)
            self.assertIn('<strong>13800</strong>',home)
            self.assertNotIn('<strong>1.38만</strong>',home)
            self.assertIn(f'<time datetime="{fetched}">{fetched}</time>',home)
            self.assertIn('<strong>0</strong>',home)
            self.assertNotIn('data-home-episode="syncTest4FL"',home)
            self.assertIn('syncTest4FL',(out/'fall-707/index.html').read_text(encoding='utf-8'))
            english=(out/'en/index.html').read_text(encoding='utf-8')
            self.assertIn('Season 4',english)
            self.assertIn('A Test Signal 4',english)
            self.assertIn('<dd><strong>13800</strong><span>subscribers</span></dd>',english)
            watch=(out/'en/watch/fall-707-s4-ep1/index.html').read_text(encoding='utf-8')
            self.assertIn('YouTube views <strong>0</strong>',watch)
            self.assertNotIn('AIza',json.dumps(snapshot))


if __name__=='__main__':
    unittest.main()
