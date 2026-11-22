# -*- coding: utf-8 -*-
r"""장면 묶음의 스프라이트 레코드 → 자료마다 풀어(bdec_sim) 회색조 그림 + 목록 (2026-11-22)
  python tools/dump_sprites.py s4  → work/sprites/<s>/sheet_N.png · list.tsv(자료 주소·크기·방식·압축 크기·폭×높이)
  색: 4비트 = 칸 번호 ×17 회색(팔레트 모름), 8비트 = 그대로"""
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bdec_sim as B


def main(state, table=0x295548):
    d = os.path.join(ROOT, 'work', 'mem', state)
    H = open(os.path.join(d, 'WorkRAMH.bin'), 'rb').read(); L = open(os.path.join(d, 'WorkRAML.bin'), 'rb').read()
    m = lambda a: (H, a - 0x06000000) if a >= 0x06000000 else (L, a - 0x200000)
    r32 = lambda a: struct.unpack_from('>I', *m(a))[0]
    r16 = lambda a: struct.unpack_from('>H', *m(a))[0]
    blobs = {}
    for i in range(2000):
        p = r32(table + 4 * i)
        if not 0x200000 <= p < 0x300000: break
        q = p
        while r16(q) < 0x8000:
            bl = r32(q + 16); sz = r16(q + 8); fl = r16(q)
            if 0x200000 <= bl < 0x300000 and bl not in blobs:
                blobs[bl] = (sz, fl)
            q += 20
    out = os.path.join(ROOT, 'work', 'sprites', state); os.makedirs(out, exist_ok=True)
    rows = []; tiles = []
    for bl, (sz, fl) in sorted(blobs.items()):
        n = r16(bl); ty = r16(bl + 2)
        w, h = (sz >> 8) * 8, sz & 0xFF
        if ty == 5:
            data = bytes(m(bl + 4)[0][m(bl + 4)[1]:m(bl + 4)[1] + n]); csz = n
        else:
            if n == 0 or n > 0x10000: continue
            try:
                data, _, end = B.dec(state, bl); csz = end - (bl + 4)
            except Exception as e:                       # 표 밖 쓰레기 포인터 등
                print('  풀기 실패 %06X: %s' % (bl, e)); continue
        bpp = 8 if w * h and n >= w * h else 4
        rows.append((bl, w, h, bpp, n, ty, csz))
        a = np.frombuffer(data, np.uint8)
        px = np.stack([a >> 4, a & 15], -1).reshape(-1) * 17 if bpp == 4 else a
        if w and len(px) >= w * h:
            tiles.append((bl, Image.fromarray(px[:w * h].reshape(h, w).astype(np.uint8))))
    with open(os.path.join(out, 'list.tsv'), 'w', encoding='utf-8') as f:
        f.write('blob\tw\th\tbpp\tbytes\ttype\tcomp\n')
        for r in rows:
            f.write('%06X\t%d\t%d\t%d\t%d\t%d\t%d\n' % r)
    # 시트
    W = 1200; x = y = rh = 0; page = 0; S = Image.new('L', (W, 1600), 40); D = ImageDraw.Draw(S)
    for bl, im in tiles:
        im2 = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        if x + im2.width > W: x = 0; y += rh + 14; rh = 0
        if y + im2.height + 14 > 1600:
            S.save(os.path.join(out, 'sheet_%d.png' % page)); page += 1
            S = Image.new('L', (W, 1600), 40); D = ImageDraw.Draw(S); x = y = rh = 0
        D.text((x, y), '%06X' % bl, fill=255); S.paste(im2, (x, y + 12))
        x += max(im2.width, 50) + 6; rh = max(rh, im2.height)
    S.save(os.path.join(out, 'sheet_%d.png' % page))
    print(len(rows), '자료 · 시트', page + 1, '장 →', out)


if __name__ == '__main__':
    main(sys.argv[1])
