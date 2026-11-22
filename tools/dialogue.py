# -*- coding: utf-8 -*-
r"""대사창 한글(2026-11-22) — 박사·보스 대사 7개 = s_init 스프라이트 목록(20 B 기록, 끝표 8000 0009)
  조각 = 03FBF8‥042824 의 대사 전용 93칸(16×16 한 글자·8×16 반각·32‥96×16 낱말, 색 a 몸통, D 0x1F8000). ゲームオーバー 조각 15개·뒤쪽 13칸(다른 목록이 씀)은 손대지 않음.
  방법: 조각 칸에 한글 음절·자주 붙는 묶음·부호를 새로 그리고, 대사마다 기록의 번호·크기·x·y·포인터를 다시 씀(남는 기록은 첫 기록과 겹침).
  입력 data/dialogue_ko.txt → work/gfx/<조각 P>.bin · work/raw/<목록 P>.bin · 미리보기 work/check/그림미리보기/대사창_원본_한글.png
  python tools/dialogue.py"""
import os, re, struct, sys
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
D = 0x1F8000
LISTS = [0x50530, 0x5096C, 0x50B50, 0x50D48, 0x5101C, 0x51408, 0x51704]
FONT = ImageFont.truetype(r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Bold.ttf', 12)
FILL = 0xA
PUNCT = ['...', '!', ',', '.']                                       # 부호 낱조각(8×16 칸 우선)
SP = 5                                                               # 띄어쓰기 폭


def records(o):
    R = []
    while P[o:o + 4] != b'\x80\x00\x00\x09':
        q = P[o:o + 20]; assert q[4:6] == b'\x08\x80'
        R.append(dict(off=o, id=struct.unpack_from('>H', q, 2)[0], w=q[8] * 8, h=q[9],
                      x=struct.unpack_from('>h', q, 10)[0], y=struct.unpack_from('>h', q, 12)[0], p=struct.unpack_from('>I', q, 16)[0] - D))
        o += 20
    return R


def room(b):
    n = int.from_bytes(P[b:b + 2], 'big'); e = b + 4 + bcomp.decode(P[b + 4:b + 4 + n * 2 + 300], n)[1]
    while e % 4: e += 1
    return e - (b + 4)


def idx_of(data, w, h):
    a = np.frombuffer(data, np.uint8); return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


def pack(idx):
    f = idx.ravel(); return bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def load_text():
    msgs = {}; cur = None
    for l in open(os.path.join(ROOT, 'data', 'dialogue_ko.txt'), encoding='utf-8').read().splitlines():
        if l.startswith('== '): cur = int(l[3:], 16); msgs[cur] = []; continue
        if l.startswith('#') or cur is None or not l.strip(): continue
        msgs[cur].append(l)
    return msgs


TOP = None
def glyph(t, w, h=16):
    """조각 그림: 잉크 왼쪽 끝 0열(…·부호는 1열), 세로는 '가' 윗줄을 2행에"""
    global TOP
    def m_of(s):
        im = Image.new('L', (120, 24), 0); ImageDraw.Draw(im).text((0, 4), s, font=FONT, fill=255); return np.array(im) > 127
    if TOP is None: TOP = np.where(m_of('가').any(1))[0][0]
    if t == '...':
        out = np.zeros((h, w), int); [out.__setitem__((12, slice(1 + 4 * i, 3 + 4 * i)), FILL) for i in range(3)]
        out[13, 1:3] = out[13, 5:7] = out[13, 9:11] = FILL; return out, 12
    m = m_of(t); xs = np.where(m.any(0))[0]; m = m[:, xs[0]:xs[-1] + 1]
    out = np.zeros((h, w), int); sub = m[TOP - 2:TOP - 2 + h, :w]
    assert m.shape[1] <= w and not m[TOP - 2 + h:].any() and not m[:TOP - 2].any(), ('조각에 안 들어감', t, m.shape, w)
    x0 = 1 if t in PUNCT else 0
    out[:sub.shape[0], x0:x0 + sub.shape[1]][sub] = FILL
    return out, m.shape[1] + x0


def tokenize(line, grams):
    toks = []; i = 0
    while i < len(line):
        for k in PUNCT + [' ']:
            if line.startswith(k, i): toks.append(k); i += len(k); break
        else:
            for g in grams:
                if line.startswith(g, i): toks.append(g); i += len(g); break
            else: toks.append(line[i]); i += 1
    return toks


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    text = load_text(); L = {o: records(o) for o in LISTS}
    assert set(text) == set(L)
    slots = {}
    for R in L.values():
        for r in R: slots.setdefault(r['p'], (r['w'], r['h'], r['id']))
    wide = sorted([p for p, v in slots.items() if v[0] >= 32], key=lambda p: -slots[p][0])
    half = [p for p, v in slots.items() if v[0] < 16]
    single = sorted([p for p, v in slots.items() if v[0] in (16, 24)], key=lambda p: -room(p))
    # 묶음 고르기: 넓은 칸마다(폭 큰 칸부터) 그 폭에 그려지는 낱말 조각 중 기록을 가장 많이 줄이는 것
    lines = [l for k in text for l in text[k]]
    words = [w for l in lines for w in re.findall(r'[가-힣0-9]+', l)]
    def fits(g, w):
        try: glyph(g, w); return True
        except AssertionError: return False
    budget = {o: len(R) for o, R in L.items()}
    nslot = len(slots)
    cands = sorted({w_[i:i + n] for w_ in words for n in range(2, 8) for i in range(len(w_) - n + 1)})
    fitw = {g: min([slots[p][0] for p in wide if fits(g, slots[p][0])] or [0]) for g in cands}
    cands = [g for g in cands if fitw[g]]
    def cost(gs):
        gs2 = sorted(gs, key=len, reverse=True); over = 0; items = set()
        for o in text:
            n = 0
            for l in text[o]:
                for t in tokenize(l, gs2):
                    if t != ' ': n += 1; items.add(t)
            over += max(0, n - budget[o])
        return max(0, len(items) - nslot) + over, len(items)
    grams = []; free_wide = sorted(slots[p][0] for p in wide)
    cur = cost(grams)
    while True:
        best = None
        for g in cands:
            if g in grams or not any(w >= fitw[g] for w in free_wide): continue
            c = cost(grams + [g])
            if best is None or c < best[0]: best = (c, g)
        if best is None or best[0] >= cur: break
        grams.append(best[1]); cur = best[0]
        free_wide.remove(min(w for w in free_wide if w >= fitw[best[1]]))
    print('남은 초과(칸+기록)', cur[0], '· 항목', cur[1], '/ 칸', nslot)
    grams.sort(key=len, reverse=True)
    toks = [t for l in lines for t in tokenize(l, grams) if t != ' ']
    need = sorted(set(t for t in toks if t not in grams and t not in PUNCT))
    puncts = sorted(set(t for t in toks if t in PUNCT))
    print('묶음', grams); print('낱음절', len(need), '부호', puncts, '· 16칸', len(single), '반각', len(half))
    # 배정
    item = {}; free_w = [p for p in wide]
    for g in grams:                                                  # 묶음 → 들어가는 가장 좁은 넓은 칸
        p = min((p for p in free_w if fits(g, slots[p][0])), key=lambda p: slots[p][0]); item[g] = p; free_w.remove(p)
    hq = list(half)
    for t in puncts:
        if t != '...' and hq: item[t] = hq.pop(0)
    pool = single + [p for p in free_w] + hq                          # 남은 넓은 칸·반각 칸도 낱음절에
    def esz(t):
        img, _ = glyph(t, 16); return min(len(bcomp.encode(pack(img), b)) for b in range(5))
    rest = [t for t in puncts if t not in item] + sorted(need, key=lambda c: -esz(c))
    pool = [p for p in pool if slots[p][0] >= 16]
    pool.sort(key=lambda p: -room(p))
    assert len(rest) <= len(pool), ('칸 모자람', len(rest), len(pool))
    for t in rest: item[t] = pool.pop(0)
    # 그리기
    adv = {}
    for t, p in item.items():
        w, h, _ = slots[p]; img, iw = glyph(t, w); adv[t] = iw + 1
        data = pack(img); assert len(data) == int.from_bytes(P[p:p + 2], 'big')
        enc = min(len(bcomp.encode(data, b)) for b in range(5))
        assert enc <= room(p), ('조각 자리 넘침', t, hex(p), enc, room(p))
        open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p), 'wb').write(data)
    adv[' '] = SP
    # 기록
    pv = []
    for o, R in L.items():
        ys = sorted({r['y'] for r in R}); x0 = min(r['x'] for r in R); xmax = x0 + 17 * 16
        place = []
        for li, line in enumerate(text[o]):
            y = ys[0] + 16 * li; x = x0
            for t in tokenize(line, grams):
                if t != ' ': place.append((t, x, y))
                x += adv[t]
            assert x <= xmax, ('줄 넘침', hex(o), line, x - x0)
        assert len(place) <= len(R), ('기록 모자람', hex(o), len(place), len(R))
        buf = bytearray(P[R[0]['off']:R[-1]['off'] + 20])
        for i, r in enumerate(R):
            t, x, y = place[i] if i < len(place) else place[0]
            p = item[t]; w, h, iid = slots[p]; q = r['off'] - R[0]['off']
            struct.pack_into('>H', buf, q + 2, iid); buf[q + 8] = w // 8; buf[q + 9] = h
            struct.pack_into('>hh', buf, q + 10, x, y); struct.pack_into('>I', buf, q + 16, p + D)
        open(os.path.join(ROOT, 'work', 'raw', '%06X.bin' % R[0]['off']), 'wb').write(bytes(buf))
        print('%06X 기록 %d 중 %d 씀 · 원문 %d줄 → %d줄' % (o, len(R), len(place), len(ys), len(text[o])))
        pv.append((R, place))
    # 미리보기(글자판): 원문 | 한글
    rows = []
    for R, place in pv:
        def canvas(items):
            x0 = min(x for _, x, _ in items); y0 = min(y for _, _, y in items)
            c = np.zeros((16 * 8, 300), np.uint8)
            for g, x, y in items:
                Y, X = y - y0, x - x0; sub = c[Y:Y + g.shape[0], X:X + g.shape[1]]; m = g[:sub.shape[0], :sub.shape[1]] > 0; sub[m] = 230
            return c
        a = canvas([(idx_of(bcomp.decode_blob(P[r['p']:r['p'] + 3000]), r['w'], r['h']), r['x'], r['y']) for r in R])
        b = canvas([(idx_of(open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % item[t]), 'rb').read(), *slots[item[t]][:2]), x, y) for t, x, y in place])
        rows.append(np.concatenate([a, np.full((a.shape[0], 6), 90, np.uint8), b], 1)); rows.append(np.full((6, 606), 90, np.uint8))
    S = np.concatenate(rows)
    Image.fromarray(S).resize((S.shape[1] * 2, S.shape[0] * 2), Image.NEAREST).save(os.path.join(ROOT, 'work', 'check', '그림미리보기', '대사창_원본_한글.png'))


if __name__ == '__main__':
    main()
