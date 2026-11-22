# -*- coding: utf-8 -*-
"""판 몇 장 미리보기(원본|한글) — python tools/preview_plates.py <출력이름> <상태> <colr> <판P …>  (work/gfx 의 새 판과 원본, 실제 CRAM 색)"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp, vdp2render as V
P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
SZ = {l.split('\t')[0]: (int(l.split('\t')[1]), int(l.split('\t')[2])) for l in open(os.path.join(ROOT, 'work', 'all', 'list.tsv')).read().splitlines()[1:]}
name, st, col = sys.argv[1], sys.argv[2], int(sys.argv[3], 16)
_, _, cram = V.load(st); cram = np.asarray(cram).astype(int)
def rgb(ix):
    e = cram[((col & 0x7F0) + ix) & 0x7FF]; im = np.stack([(e & 31) << 3, (e >> 5 & 31) << 3, (e >> 10 & 31) << 3], -1).astype(np.uint8); im[ix == 0] = (40, 40, 40); return im
def idx(d, w, h): a = np.frombuffer(d, np.uint8); return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)
rows = []
for a in sys.argv[4:]:
    p = int(a, 16); w, h = SZ['%06X' % p]; n = int.from_bytes(P[p:p + 2], 'big')
    o = idx(bcomp.decode_blob(P[p:p + 4 + n * 2 + 300]), w, h); f = os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p)
    nw = idx(open(f, 'rb').read(), w, h) if os.path.exists(f) else o
    rows.append(np.concatenate([rgb(o), np.full((h, 4, 3), 90, np.uint8), rgb(nw)], 1))
W = max(r.shape[1] for r in rows); S = np.full((sum(r.shape[0] + 4 for r in rows), W, 3), 60, np.uint8); y = 0
for r in rows: S[y:y + r.shape[0], :r.shape[1]] = r; y += r.shape[0] + 4
out = os.path.join(ROOT, 'work', 'check', '그림미리보기', name + '.png')
Image.fromarray(S).resize((W * 3, S.shape[0] * 3), Image.NEAREST).save(out); print(out)
