# -*- coding: utf-8 -*-
r"""받은 스테이트 18장의 화면 스프라이트(VDP1 명령표) → PROGRAM.BIN 자료 짝짓기 + 실제 색 그림판 (2026-11-22)
  python tools/state_sprites.py → work/states_map.tsv(스테이트·VRAM·크기·colr·자리·자료 P) · work/check/스테이트별_스프라이트/s<N>.png"""
import csv, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp, vdp1cmd, vdp2render as V, spritesheet as SS

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    byd = {}
    for r in csv.DictReader(open(os.path.join(ROOT, 'work', 'all', 'list.tsv'), encoding='utf-8'), delimiter='\t'):
        bl = int(r['P'], 16); n = int(r['bytes'])
        try: d = bcomp.decode_blob(P[bl:bl + 4 + n * 2 + 300])
        except Exception: continue
        byd.setdefault(d, r['P'])
    out = os.path.join(ROOT, 'work', 'check', '스테이트별_스프라이트'); os.makedirs(out, exist_ok=True)
    rows = []
    for k in range(1, 19):
        s = 's%d' % k; v = vdp1cmd.load(os.path.join(ROOT, 'work', 'mem', s)); _, _, cram = V.load(s)
        items = []; seen = set()
        for i, cmd, pm, col, sa, w, h, x, y in vdp1cmd.cmds(v):
            if (sa, w, h, col) in seen or w < 8 or h < 8: continue
            seen.add((sa, w, h, col))
            mode = (pm >> 3) & 7; nb = w * h // 2 if mode in (0, 1) else w * h if mode in (2, 3, 4) else w * h * 2
            src = byd.get(bytes(v[sa:sa + nb]), '')
            rows.append((s, '%05X' % sa, w, h, '%04X' % col, mode, x, y, src))
            im = SS.sprite(v, cram, pm, col, sa, w, h)
            if im is not None: items.append(('%05X %s' % (sa, src or '?'), im))
        W = 1400; xx = yy = rh = 0; S = Image.new('RGB', (W, 3000), (50, 50, 50)); D = ImageDraw.Draw(S)
        for lab, im in items:
            im = Image.fromarray(im.astype(np.uint8)); im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
            if xx + im.width > W: xx = 0; yy += rh + 14; rh = 0
            D.text((xx, yy), lab, fill=(255, 255, 0)); S.paste(im, (xx, yy + 12)); xx += max(im.width, 100) + 6; rh = max(rh, im.height)
        S.crop((0, 0, W, yy + rh + 14)).save(os.path.join(out, '%s.png' % s))
    with open(os.path.join(ROOT, 'work', 'states_map.tsv'), 'w', encoding='utf-8') as f:
        f.write('state\tvram\tw\th\tcolr\tmode\tx\ty\tblob\n')
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
    print(len(rows), '스프라이트,', sum(1 for r in rows if r[-1]), '개 자료 짝지음')


if __name__ == '__main__':
    main()
