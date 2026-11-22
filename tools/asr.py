# -*- coding: utf-8 -*-
"""동영상 받아쓰기(faster_whisper large-v3, VAD 끔) — work/movie/<영상>.wav(16kHz 모노) → work/movie/<영상>_asr.tsv
   C:/claude/utils/whisper-venv/Scripts/python.exe tools/asr.py"""
import os, sys, wave
import numpy as np
from faster_whisper import WhisperModel
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')
m = WhisperModel('large-v3', device='cuda', compute_type='float16')
for n in ['BOMSS1', 'BOMSS2', 'BOMSS3']:
    w = wave.open(os.path.join(ROOT, 'work', 'movie', n + '.wav')); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, language='ja', beam_size=5, condition_on_previous_text=False, vad_filter=False)
    with open(os.path.join(ROOT, 'work', 'movie', n + '_asr.tsv'), 'w', encoding='utf-8') as f:
        f.write('시작\t끝\t원문\tno_speech\n')
        for s in segs:
            f.write('%.2f\t%.2f\t%s\t%.2f\n' % (s.start, s.end, s.text.strip(), s.no_speech_prob)); print(n, '%.2f-%.2f' % (s.start, s.end), s.text.strip())
