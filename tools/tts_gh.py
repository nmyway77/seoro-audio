# -*- coding: utf-8 -*-
"""깃허브 Actions 에서 실행: _tts_jobs/*.json 의 녹음 작업을 ElevenLabs 로 처리해 _tts_out/ 에 저장한다.
작업 파일 형식(JSON):
  {"voices": true}                                   → _tts_out/voices.json (내 목소리 목록)
  {"items":[{"out":"이름", "voice":"VOICE_ID", "text":"...", "model":"eleven_multilingual_v2",
             "settings":{...선택}}, ...]}
  → _tts_out/<이름>.mp3  +  _tts_out/<이름>.json (글자별 시작·끝 시각 = alignment)
처리한 작업 파일은 _tts_jobs/done/ 으로 옮긴다. 이미 결과가 있는 항목은 건너뛴다(크레딧 절약).
키: 환경 변수 ELEVENLABS_API_KEY (저장소 Secrets)."""
import os,sys,json,glob,base64,shutil,time,urllib.request,urllib.error
KEY=os.environ['ELEVENLABS_API_KEY']; API='https://api.elevenlabs.io/v1'
OUT='_tts_out'; os.makedirs(OUT,exist_ok=True); os.makedirs('_tts_jobs/done',exist_ok=True)

def call(path,body=None):
    req=urllib.request.Request(API+path,data=json.dumps(body).encode() if body is not None else None,
        headers={'xi-api-key':KEY,'Content-Type':'application/json','Accept':'application/json'},method='POST' if body is not None else 'GET')
    for k in range(4):
        try:
            with urllib.request.urlopen(req,timeout=300) as r:
                d=json.load(r); d['_headers']={k.lower():v for k,v in r.headers.items() if 'char' in k.lower() or 'request-id' in k.lower()}; return d
        except urllib.error.HTTPError as e:
            msg=e.read().decode(errors='replace')[:400]
            if e.code in (429,500,502,503) and k<3: print('  retry',e.code); time.sleep(10*(k+1)); continue
            raise SystemExit(f'HTTP {e.code}: {msg}')

for jf in sorted(glob.glob('_tts_jobs/*.json')):
    J=json.load(open(jf,encoding='utf-8')); print('job',jf)
    if J.get('voices'):
        V=call('/voices'); V.pop('_headers',None); json.dump([dict(id=v['voice_id'],name=v['name'],cat=v.get('category'),labels=v.get('labels')) for v in V['voices']],
                                     open(f'{OUT}/voices.json','w',encoding='utf-8'),ensure_ascii=False,indent=1); print('  voices',len(V['voices']))
    for it in J.get('items',[]):
        mp3=f"{OUT}/{it['out']}.mp3"
        if os.path.exists(mp3): print('  skip',it['out']); continue
        body=dict(text=it['text'],model_id=it.get('model','eleven_multilingual_v2'))
        if it.get('settings'): body['voice_settings']=it['settings']
        R=call(f"/text-to-speech/{it['voice']}/with-timestamps?output_format=mp3_44100_128",body)
        open(mp3,'wb').write(base64.b64decode(R['audio_base64']))
        json.dump(dict(text=it['text'],alignment=R.get('alignment'),normalized=R.get('normalized_alignment'),headers=R.get('_headers')),open(f"{OUT}/{it['out']}.json",'w',encoding='utf-8'),ensure_ascii=False)
        print('  ok',it['out'],len(it['text']),'chars')
    shutil.move(jf,'_tts_jobs/done/'+os.path.basename(jf))
