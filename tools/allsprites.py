# -*- coding: utf-8 -*-
r"""PROGRAM.BIN 전체 스프라이트 자료 목록 (2026-11-22)
  레코드(20 B: +0 깃발 <0x8000 · +8 크기 코드 · +16 LowRAM 포인터)를 파일 전체에서 찾고,
  주소 대응 후보 D(LowRAM = P + D: 모듈 9개는 «모듈 시작 + 0x8000 = LowRAM 0x200000», 묶음 9개는 «묶음 시작 = 0x254540»)마다
  포인터 − D 의 자료가 풀리고 크기(폭×높이/2 또는 폭×높이)가 맞으면 채택.
  → work/all/list.tsv (자료 P·풀린 크기·방식·압축 크기·폭·높이·bpp·가리킨 레코드 수·D) + work/all/sheet_N.png(글자판 모양만, --all 이면 전부)
  python tools/allsprites.py [--all]"""
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
MODULES = [0x0, 0x580000, 0x5E8000, 0x650000, 0x6B8000, 0x720000, 0x788000, 0x814000, 0x87C000]
PACKS = [0x0B0540, 0x13C540, 0x1C8540, 0x254540, 0x300540, 0x38C540, 0x438540, 0x4D4540, 0x560540]
DS = sorted({0x200000 - (m + 0x8000) for m in MODULES} | {0x254540 - p for p in PACKS} | {0x254000 - m for m in MODULES[1:]})   # 모듈 s_open‥ = 시작이 0x254000
r32 = lambda o: struct.unpack_from('>I', P, o)[0]
r16 = lambda o: struct.unpack_from('>H', P, o)[0]


def scan():
    found = {}
    cache = {}
    for o in range(0, len(P) - 20, 2):
        fl = r16(o)
        if fl >= 0x8000: continue
        sz = r16(o + 8); w, h = (sz >> 8) * 8, sz & 0xFF
        if not (8 <= w <= 320 and 1 <= h <= 240): continue
        p = r32(o + 16)
        if not 0x200000 <= p < 0x2F0540: continue
        for D in DS:
            bl = p - D
            if not 0 <= bl < len(P) - 8: continue
            key = (bl, w, h)
            if key in found:
                found[key][1] += 1; break
            if bl in cache and cache[bl] is None: continue
            n = r16(bl); ty = r16(bl + 2)
            if n not in (w * h // 2, w * h) or ty > 5: continue
            if bl not in cache:
                try:
                    if ty == 5: cache[bl] = (bytes(P[bl + 4:bl + 4 + n]), n)
                    else: cache[bl] = bcomp.decode(P[bl + 4:bl + 4 + n * 2 + 300], n)
                except Exception:
                    cache[bl] = None; continue
            if cache[bl] is None or len(cache[bl][0]) != n: continue
            found[key] = [D, 1, n, ty, cache[bl][1]]
            break
    return found, cache


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    found, cache = scan()
    out = os.path.join(ROOT, 'work', 'all'); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'list.tsv'), 'w', encoding='utf-8') as f:
        f.write('P\tw\th\tbpp\tbytes\ttype\tcomp\trefs\tD\n')
        for (bl, w, h), (D, refs, n, ty, comp) in sorted(found.items()):
            f.write('%06X\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%X\n' % (bl, w, h, 8 if n == w * h else 4, n, ty, comp, refs, D & 0xFFFFFFFF))
    print('자료', len(found), '→', out)
    textish = '--all' not in sys.argv
    tiles = []
    for (bl, w, h), (D, refs, n, ty, comp) in sorted(found.items()):
        if textish and not (8 <= h <= 48 and w >= 24 and w >= h * 1.5): continue
        d = cache[bl][0]; a = np.frombuffer(d, np.uint8)
        px = np.stack([a >> 4, a & 15], -1).reshape(-1) * 17 if n * 2 == w * h else a
        tiles.append(('%06X' % bl, Image.fromarray(px[:w * h].reshape(h, w).astype(np.uint8))))
    W = 1400; x = y = rh = 0; page = 0; S = Image.new('L', (W, 1800), 40); Dd = ImageDraw.Draw(S)
    for t, im in tiles:
        if x + im.width > W: x = 0; y += rh + 12; rh = 0
        if y + im.height + 12 > 1800:
            S.save(os.path.join(out, 'sheet_%d.png' % page)); page += 1
            S = Image.new('L', (W, 1800), 40); Dd = ImageDraw.Draw(S); x = y = rh = 0
        Dd.text((x, y), t, fill=255); S.paste(im, (x, y + 10)); x += max(im.width, 44) + 4; rh = max(rh, im.height)
    S.crop((0, 0, W, y + rh + 12)).save(os.path.join(out, 'sheet_%d.png' % page))
    print('그림판', page + 1, '장(글자판 모양 %d개)' % len(tiles))


if __name__ == '__main__':
    main()
