# -*- coding: utf-8 -*-
r"""메뉴 단추 글자판 한글(2026-11-22 시험) — 원본 4비트 단추(판 테두리 15·바탕 5·글자 속 a·외곽선 2·모서리 4) 규칙으로 다시 그림
  python tools/gfx_button.py → work/gfx/<자료 P>.bin(풀린 바이트) + 미리보기 work/check/그림미리보기/<이름>_원본_한글.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp, vdp2render as V

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
FONT = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Bold.ttf'
JOBS = [(0x4A4340, 56, 24, 'セーブする', '저장하기', 0x1310, 's3')]   # 자료 P, 폭, 높이, 원문, 한글, 색 뱅크, 색 스테이트


def idx_of(data, w, h):
    a = np.frombuffer(data, np.uint8)
    return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


def pack(idx):
    f = idx.ravel()
    return bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def dil8(m):
    p = np.pad(m, 1); o = np.zeros_like(m)
    for dy in range(3):
        for dx in range(3): o |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
    return o


def dil4(m):
    p = np.pad(m, 1)
    return m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def draw(orig, text, dx=0, dy=0, use4=False):
    idx = orig.copy()
    h, w = idx.shape
    # 판 안쪽(바탕 5 구역) 찾기: 글자 자리 = 테두리 15 안, 원래 글자(5 아닌 칸) 지우기
    inner = np.zeros_like(idx, bool)
    rows = [y for y in range(h) if (idx[y] == 15).sum() < w // 2 and idx[y, 0] == 15]
    y0, y1 = rows[0], rows[-1]
    inner[y0:y1 + 1, 1:w - 1] = True
    idx[inner] = 5
    F = ImageFont.truetype(FONT, 12)
    im = Image.new('L', (w * 2, 30), 0); d = ImageDraw.Draw(im)
    d.text((2, 2), text, font=F, fill=255)
    m = np.array(im) > 127
    ys, xs = np.where(m); m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    mh, mw = m.shape
    cy = y0 + ((y1 - y0 + 1) - mh) // 2 + dy; cx = (w - mw) // 2 + dx
    if cx < 2 or cx + mw > w - 2 or cy < y0 + 1 or cy + mh > y1: return None
    M = np.zeros_like(idx, bool); M[cy:cy + mh, cx:cx + mw] = m
    out8 = dil8(M) & ~M; out4 = dil4(M) & ~M
    idx[out8 & ~out4] = 4 if use4 else 2        # 원본은 대각 칸 = 모서리 색 4, 압축 크기가 넘치면 2(굵은 외곽선)
    idx[out4] = 2
    idx[M] = 0xA
    assert ((idx != orig) & ~inner).sum() == 0, '판 밖 화소가 바뀜'
    return idx


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    pv = os.path.join(ROOT, 'work', 'check', '그림미리보기'); os.makedirs(pv, exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'work', 'gfx'), exist_ok=True)
    for bl, w, h, ja, ko, col, st in JOBS:
        n = int.from_bytes(P[bl:bl + 2], 'big')
        orig = idx_of(bcomp.decode_blob(P[bl:bl + 4 + n * 2 + 300]), w, h)
        room = bcomp.decode(P[bl + 4:bl + 4 + n * 2 + 300], n)[1]
        nxt = bl + 4 + room
        while nxt % 4: nxt += 1                          # 다음 자료는 4 바이트 정렬 — 그 사이 여유까지 씀
        room = nxt - (bl + 4)
        cands = []
        for use4 in (True, False):
            for dx in (0, 1, -1, 2, -2):
                for dy in (0, -1, 1):
                    t = draw(orig, ko, dx, dy, use4)
                    if t is not None: cands.append((len(bcomp.encode(pack(t), 0)), not use4, abs(dx) + abs(dy), dx, dy, use4, t))
        fit = [c for c in cands if c[0] <= room]
        assert fit, ('원래 자리에 안 들어감', ko, min(cands)[0], room)
        sz, _, _, dx, dy, use4, new = min(fit, key=lambda c: (c[1], c[2], c[0]))
        print('  압축 %d / 자리 %d · 가로 %+d 세로 %+d · 모서리색4 %s' % (sz, room, dx, dy, use4))
        open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl), 'wb').write(pack(new))
        _, _, cram = V.load(st); cram = np.asarray(cram).astype(int)
        def rgb(ix):
            e = cram[((col & 0x7F0) + ix) & 0x7FF]
            img = np.stack([(e & 31) << 3, (e >> 5 & 31) << 3, (e >> 10 & 31) << 3], -1).astype(np.uint8)
            img[ix == 0] = (40, 40, 40); return img
        S = np.concatenate([rgb(orig), np.full((h, 4, 3), 90, np.uint8), rgb(new)], 1)
        Image.fromarray(S).resize((S.shape[1] * 6, h * 6), Image.NEAREST).save(os.path.join(pv, '%s_원본_한글.png' % ko))
        print(ja, '→', ko, '바뀐 칸', int((new != orig).sum()))


if __name__ == '__main__':
    main()
