# -*- coding: utf-8 -*-
r"""PROGRAM.BIN 장면 묶음 찾기·스프라이트 목록 (2026-11-22)
  묶음 = PROGRAM.BIN 의 한 구간이 LowRAM 0x254540 부터 그대로 실림. 머리(h) = [h+8, 번호표 포인터, 레코드 목록 포인터…]
  레코드 20 B: +0 깃발(≥0x8000 목록 끝) · +8 크기 코드(폭/8, 높이) · +16 자료 포인터.
  자료 = [u16 n][u16 방식(5 무압축)][압축 자료] (tools/bcomp.py)
  python tools/packs.py scan          → 머리 후보 검증(풀기 성공·크기 맞음 비율)
  python tools/packs.py dump <묶음 P 시작 16진> [머리 P 16진] → work/packs/<시작>/sheet_N.png·list.tsv
"""
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
BASE = 0x254540
r32 = lambda o: struct.unpack_from('>I', P, o)[0] if 0 <= o <= len(P) - 4 else 0
r16 = lambda o: struct.unpack_from('>H', P, o)[0] if 0 <= o <= len(P) - 2 else 0xFFFF


def heads(ps):
    """묶음 시작 ps 안에서 머리 후보(첫 값 = 자기 LowRAM 주소 + 8)"""
    D = BASE - ps; out = []
    for o in range(ps, min(ps + 0x9C000, len(P) - 8), 4):
        if r32(o) == o + D + 8 and o + D + 8 < r32(o + 4) < 0x2F0540:
            out.append(o)
    return out


def records(ps, h):
    """머리 h → [(레코드 P, 깃발, 크기 코드, 자료 P)] (중복 자료 포함)"""
    D = BASE - ps; recs = []
    t = h + 8
    for i in range(3000):
        p = r32(t + 4 * i) - D
        if not ps <= p < ps + 0x9C000: break
        q = p; k = 0
        while r16(q) < 0x8000 and k < 64:
            bl = r32(q + 16) - D
            if ps <= bl < ps + 0x9C000:
                recs.append((q, r16(q), r16(q + 8), bl))
            q += 20; k += 1
    return recs


def blob_ok(bl, sz):
    n = r16(bl); ty = r16(bl + 2); w, h = (sz >> 8) * 8, sz & 0xFF
    if n == 0 or n > 0x20000 or ty > 6: return None
    try:
        data = bcomp.decode_blob(P[bl:bl + 4 + n * 2 + 300])
    except Exception:
        return None
    return data if len(data) == n and n in (w * h // 2, w * h) else None


def scan():
    starts = sorted({o - (r32(o) - 8 - BASE) for o in range(0, len(P) - 8, 4)
                     if BASE <= r32(o) < 0x2F0540 and (o - (r32(o) - 8 - BASE)) % 0x1000 == 0x540
                     and 0 <= o - (r32(o) - 8 - BASE) < len(P)})
    for ps in starts:
        for h in heads(ps):
            rs = records(ps, h)
            uniq = {bl: sz for _, _, sz, bl in rs}
            good = sum(1 for bl, sz in list(uniq.items())[:200] if blob_ok(bl, sz) is not None)
            if good >= 5:
                print('묶음 P %06X 머리 P %06X(LowRAM %06X) 레코드 %d 자료 %d 검사 %d/%d' %
                      (ps, h, h + BASE - ps, len(rs), len(uniq), good, min(200, len(uniq))), flush=True)


def dump(ps, h=None):
    if h is None:
        h = max(heads(ps), key=lambda x: len(records(ps, x)))
    rs = records(ps, h); uniq = {}
    for _, fl, sz, bl in rs: uniq.setdefault(bl, sz)
    out = os.path.join(ROOT, 'work', 'packs', '%06X' % ps); os.makedirs(out, exist_ok=True)
    rows = []; tiles = []
    for bl, sz in sorted(uniq.items()):
        data = blob_ok(bl, sz)
        if data is None: continue
        w, hh = (sz >> 8) * 8, sz & 0xFF; n = len(data); bpp = 8 if n == w * hh else 4
        comp = bcomp.decode(P[bl + 4:bl + 4 + n * 2 + 300], n)[1] if r16(bl + 2) != 5 else n
        rows.append((bl, bl + BASE - ps, w, hh, bpp, n, r16(bl + 2), comp))
        a = np.frombuffer(data, np.uint8)
        px = np.stack([a >> 4, a & 15], -1).reshape(-1) * 17 if bpp == 4 else a
        tiles.append((bl, Image.fromarray(px[:w * hh].reshape(hh, w).astype(np.uint8))))
    with open(os.path.join(out, 'list.tsv'), 'w', encoding='utf-8') as f:
        f.write('P\tLowRAM\tw\th\tbpp\tbytes\ttype\tcomp\n')
        for r in rows: f.write('%06X\t%06X\t%d\t%d\t%d\t%d\t%d\t%d\n' % r)
    W = 1200; x = y = rh = 0; page = 0; S = Image.new('L', (W, 1600), 40); Dd = ImageDraw.Draw(S)
    for bl, im in tiles:
        im2 = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        if x + im2.width > W: x = 0; y += rh + 14; rh = 0
        if y + im2.height + 14 > 1600:
            S.save(os.path.join(out, 'sheet_%d.png' % page)); page += 1
            S = Image.new('L', (W, 1600), 40); Dd = ImageDraw.Draw(S); x = y = rh = 0
        Dd.text((x, y), '%06X' % bl, fill=255); S.paste(im2, (x, y + 12))
        x += max(im2.width, 50) + 6; rh = max(rh, im2.height)
    S.save(os.path.join(out, 'sheet_%d.png' % page))
    print('묶음 %06X 머리 %06X 자료 %d → %s (%d장)' % (ps, h, len(rows), out, page + 1))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'scan': scan()
    else: dump(int(sys.argv[2], 16), int(sys.argv[3], 16) if len(sys.argv) > 3 else None)
