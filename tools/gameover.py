# -*- coding: utf-8 -*-
r"""«ゲームオーバー» 애니메이션(2026-11-22) → «게임 오버»
  프레임 목록 12개(51C80‥524E0, s_init, D 0x1F8000), 글자 조각 3벌(어두움·중간·밝음) × ゲ·ー·ム·オ·バ = 15개.
  ゲ→게 · ム→임 · オ→오 · バ→버 로 다시 그림(원본 글자의 줄별 몸통 색을 세로 비율로 옮김 + 바깥선 1), ー 조각은 투명.
  기록은 조각별로 x 만 새 자리(게 −26 · 임 6 · 오 46 · 버 78), y·순서·번호 그대로.
  python tools/gameover.py → work/gfx/<조각>.bin · work/raw/<목록>.bin · 미리보기 work/check/그림미리보기/게임오버_원본_한글.png"""
import os, struct, sys
from collections import Counter
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp
from gfx_custom_menu import big_mask, dil8, room, pack

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
D = 0x1F8000
LISTS = [0x51C80, 0x51D10, 0x51DA0, 0x51E30, 0x51EC0, 0x51FDC, 0x520E4, 0x521D8, 0x522B8, 0x52384, 0x52450, 0x524E0]
SETS = [dict(ゲ=0x41B28, ー=0x41C44, ム=0x41C88, オ=0x41D88, バ=0x41E58),
        dict(ゲ=0x41F38, ー=0x4204C, ム=0x42090, オ=0x4219C, バ=0x42288),
        dict(ゲ=0x42388, ー=0x424A8, ム=0x424F0, オ=0x4260C, バ=0x4270C)]
KO = dict(ゲ='게', ム='임', オ='오', バ='버')
HK = 22
NEWX = dict(ゲ=-26, ム=6, オ=46, バ=78)


def records(o):
    R = []
    while P[o:o + 4] != b'\x80\x00\x00\x09':
        q = P[o:o + 20]; R.append(dict(off=o, p=struct.unpack_from('>I', q, 16)[0] - D, w=q[8] * 8, h=q[9])); o += 20
    return R


def load(p, w, h):
    n = int.from_bytes(P[p:p + 2], 'big'); a = np.frombuffer(bcomp.decode_blob(P[p:p + 4 + n * 2 + 300]), np.uint8)
    return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


def redraw(o, ko):
    h, w = o.shape; ink = o != 0; ys = np.where(ink.any(1))[0]; xs = np.where(ink.any(0))[0]
    rowc = {}
    for y in ys:                                                     # 줄 몸통 색 = 바깥선(1) 뺀 최빈
        v = [c for c in o[y] if c not in (0, 1)]
        if v: rowc[y] = Counter(v).most_common(1)[0][0]
    m = big_mask(ko, HK)                                             # 모든 조각 같은 높이(같은 무리 같은 크기)
    out = np.zeros_like(o); H, W = m.shape
    y0 = h - 2 - H; x0 = (w - W) // 2                                # 원본처럼 조각 바닥(아래 1줄 여백)에 맞춤
    M = np.zeros_like(ink); M[y0:y0 + H, x0:x0 + W] = m
    out[dil8(M) & ~M] = 1
    ks = sorted(rowc)
    for y in range(y0, y0 + H):                                      # 원본 글자 세로 비율대로 색 옮김
        t = (y - y0) / max(1, H - 1); src = ks[0] + t * (ks[-1] - ks[0]); c = rowc[min(ks, key=lambda k: abs(k - src))]
        out[y][M[y]] = c
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    size = {}
    for o in LISTS:
        for r in records(o): size[r['p']] = (r['w'], r['h'])
    kana_of = {p: k for S in SETS for k, p in S.items()}
    pv = []
    for p, k in kana_of.items():
        w, h = size[p]; o = load(p, w, h)
        new = np.zeros_like(o) if k == 'ー' else redraw(o, KO[k])
        enc = min(len(bcomp.encode(pack(new), b)) for b in range(5))
        assert enc <= room(p), ('자리 넘침', k, hex(p), enc, room(p))
        open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p), 'wb').write(pack(new))
        print('%06X %s→%s 압축 %d / 자리 %d' % (p, k, KO.get(k, '(빈칸)'), enc, room(p)))
        pv.append((o, new))
    for o in LISTS:
        R = records(o); buf = bytearray(P[R[0]['off']:R[-1]['off'] + 20])
        for i, r in enumerate(R):
            k = kana_of[r['p']]
            if k in NEWX: struct.pack_into('>h', buf, i * 20 + 10, NEWX[k])
        open(os.path.join(ROOT, 'work', 'raw', '%06X.bin' % R[0]['off']), 'wb').write(bytes(buf))
    # 미리보기(회색조): 조각 원본 | 한글
    rows = []
    for o, n in pv:
        a = np.zeros((32, 70), np.uint8); a[:o.shape[0], :32] = o * 17; a[:n.shape[0], 36:68] = n * 17; rows.append(a)
    S = np.hstack([np.vstack(rows[i:i + 5]) for i in range(0, 15, 5)])
    Image.fromarray(S).resize((S.shape[1] * 3, S.shape[0] * 3), Image.NEAREST).save(os.path.join(ROOT, 'work', 'check', '그림미리보기', '게임오버_원본_한글.png'))


if __name__ == '__main__':
    main()
