"""Transcription par segments (sherpa-onnx whisper-small, modèle téléchargé depuis les releases GitHub k2-fsa/sherpa-onnx, Hugging Face étant bloqué) :
python3 transcrire.py voice.wav voix/segments.json"""
import sys, wave, numpy as np, sherpa_onnx, json
M='/home/claude/models/sherpa-onnx-whisper-small/small-'
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+'encoder.int8.onnx',decoder=M+'decoder.int8.onnx',tokens=M+'tokens.txt',language='fr',task='transcribe',num_threads=2)
w=wave.open(sys.argv[1]);sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
h=sr//100;n=len(x)//h;e=np.sqrt((x[:n*h].reshape(n,h)**2).mean(1));db=20*np.log10(e+1e-6);sp=db>np.percentile(db,95)-35
segs=[];i=0
while i<n:
    if sp[i]:
        j=i
        while j<n and sp[j]: j+=1
        segs.append([i/100,j/100]);i=j
    else:i+=1
m=[]
for s in segs:
    if m and s[0]-m[-1][1]<0.14: m[-1][1]=s[1]
    else: m.append(s)
m=[s for s in m if s[1]-s[0]>0.06]
out=[]
for a,b in m:
    y=x[int(max(0,a-.08)*sr):int((b+.08)*sr)]
    y16=np.interp(np.arange(0,len(y),sr/16000),np.arange(len(y)),y).astype(np.float32)
    s=rec.create_stream();s.accept_waveform(16000,y16);rec.decode_stream(s)
    out.append((a,b,s.result.text.strip()));print(f"{a:6.2f} {b:6.2f} {s.result.text.strip()}",flush=True)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
