# -*- coding: utf-8 -*-
r"""저장 안내문 한글(2026-11-22) — s_init 글자 조각(16×16 등) 조합 문장 15개
  구조: 스프라이트 목록 = 20 B 기록(+2 번호 · +8 크기(폭/8, 높이) · +10 x · +12 y · +16 LowRAM 포인터(= 파일 + 0x1F8000))… + 끝표 8000 0009
  방법: 안내문 전용 조각 칸에 한글 음절(넓은 칸은 자주 붙는 묶음)을 새로 그리고, 문장마다 글자 기록의 조각·x·y 를 다시 씀.
        남는 기록은 앞 기록과 똑같이 겹쳐 안 보이게. L·R·B·RAM·? 는 원본 조각 그대로.
  입력: data/save_msgs_ko.txt
  출력: work/gfx/<조각 P>.bin(build.py 가 압축·제자리) + work/raw/<목록 P>.bin(기록 영역 통째, build.py 가 덮어씀) + 미리보기
  python tools/save_msgs.py"""
import os, re, struct, sys
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
D = 0x1F8000
FONT = ImageFont.truetype(r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Bold.ttf', 12)
KEEP = {'L': 0x1E1F8, 'R': 0x1E220, 'B': 0x1EF40, 'RAM': 0x1F478, '?': 0x1EB44}
PUNCT = {'.': 0x1DC10, ',': 0x1D7D4}                                  # 8×8 조각(원래 。、)
FILL = 0x8                                                           # 원본 글자 몸통 색


def parse_lists():
    lists = []; o = 0x45400; cur = None
    while o < 0x4A000:
        if P[o:o + 4] == b'\x80\x00\x00\x09':
            if cur: lists.append(cur)
            cur = (o + 4, []); o += 4; continue
        if cur is not None and P[o:o + 2] == b'\0\0' and P[o + 4:o + 6] == b'\x08\x80':
            r = P[o:o + 20]
            cur[1].append(dict(off=o, id=struct.unpack_from('>H', r, 2)[0], w=r[8] * 8, h=r[9],
                               x=struct.unpack_from('>h', r, 10)[0], y=struct.unpack_from('>h', r, 12)[0],
                               p=struct.unpack_from('>I', r, 16)[0] - D))
            o += 20; continue
        o += 2
    return lists


def is_glyph(r):
    return (0x1B000 <= r['p'] < 0x20600) and r['w'] <= 64 and r['h'] in (8, 16)


def room(b):
    n = int.from_bytes(P[b:b + 2], 'big'); e = b + 4 + bcomp.decode(P[b + 4:b + 4 + n * 2 + 300], n)[1]
    while e % 4: e += 1
    return e - (b + 4)


def load_text():
    msgs = {}; cur = None
    for l in open(os.path.join(ROOT, 'data', 'save_msgs_ko.txt'), encoding='utf-8').read().splitlines():
        if l.startswith('== '): cur = int(l[3:], 16); msgs[cur] = []; continue
        if l.startswith('# ') or cur is None: continue
        msgs[cur].append(l)
    for k in msgs:
        while msgs[k] and msgs[k][-1] == '': msgs[k].pop()
    return msgs


def mask(t):
    im = Image.new('L', (80, 24), 0); ImageDraw.Draw(im).text((0, 4), t, font=FONT, fill=255)
    m = np.array(im) > 127
    return m


TOP = None


def glyph_img(t, w, h):
    """조각 그림: 글자 잉크 왼쪽 끝을 0 열, 세로는 '가' 윗줄을 2 행에 맞춤"""
    global TOP
    if TOP is None: TOP = np.where(mask('가').any(1))[0][0]
    m = mask(t); xs = np.where(m.any(0))[0]; m = m[:, xs[0]:xs[-1] + 1]
    out = np.zeros((h, w), int); sub = m[TOP - 2:TOP - 2 + h, :w]
    assert m.shape[1] <= w and not m[TOP - 2 + h:].any() and not m[:TOP - 2].any(), ('조각에 안 들어감', t)
    out[:sub.shape[0], :sub.shape[1]][sub] = FILL
    return out, m.shape[1]


def punct_img(t):
    out = np.zeros((8, 8), int)
    if t == '.': out[4:6, 1:3] = FILL
    else: out[4:6, 1:3] = FILL; out[6, 1] = FILL
    return out


def tokenize(line, grams):
    toks = []; i = 0
    while i < len(line):
        for k in ('RAM', 'L', 'R', 'B', '?', '.', ',', ' '):
            if line.startswith(k, i): toks.append(k); i += len(k); break
        else:
            for g in grams:
                if line.startswith(g, i): toks.append(g); i += len(g); break
            else: toks.append(line[i]); i += 1
    return toks


FORCE = ['기록', '습니']                                              # 기록 수가 빠듯한 문장(이 기록은…) 때문에 꼭 넣을 묶음


def choose_grams(words, caps):
    def cover(ch):
        need = set()
        for w in words:
            i = 0
            while i < len(w):
                for g in sorted(ch, key=len, reverse=True):
                    if w.startswith(g, i): i += len(g); break
                else: need.add(w[i]); i += 1
        return need
    gr = Counter()
    for w in words:
        for n in set(caps):
            for i in range(len(w) - n + 1): gr[w[i:i + n]] += 1
    ch = []; caps = list(caps)
    for f in FORCE: ch.append(f); caps.remove(len(f))
    for cap in sorted(caps, reverse=True):
        best = None
        for g in sorted(g for g in gr if len(g) == cap and g not in ch):
            n = len(cover(ch + [g]))
            if best is None or n < best[0]: best = (n, g)
        if best: ch.append(best[1])
    return sorted(ch, key=len, reverse=True), cover(ch)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    lists = parse_lists(); text = load_text()
    L = {st: R for st, R in lists if st in text}
    assert set(L) == set(text), set(text) - set(L)
    # 조각 칸
    slots = {}
    for st, R in L.items():
        for r in R:
            if is_glyph(r): slots[r['p']] = (r['w'], r['h'], r['id'])
    free = {p: v for p, v in slots.items() if p not in KEEP.values() and p not in PUNCT.values()}
    wide = sorted([p for p, v in free.items() if v[0] >= 32 and v[1] == 16 and room(p) >= 70], key=lambda p: -free[p][0])   # 자리 작은 넓은 칸은 낱음절용
    single = sorted([p for p, v in free.items() if v[1] == 16 and p not in wide], key=lambda p: -room(p))
    capw = {32: 2, 40: 3, 48: 3, 64: 5}
    words = [w for k in text for l in text[k] for w in re.findall(r'[가-힣]+', l.replace('#', ' '))]
    grams, need = choose_grams(words, [capw[free[p][0]] for p in wide])
    print('넓은 칸 묶음', grams, '· 낱음절', len(need), '/ 칸', len(single))
    assert len(need) <= len(single), '낱음절 칸 모자람'
    # 배정: 묶음 → 넓은 칸(길이 맞춰), 낱음절 → 복잡한(압축 큰) 글자부터 자리 큰 칸
    item_slot = {}
    def esz(t, w, h):
        img, _ = glyph_img(t, w, h); return min(len(bcomp.encode(pack(img), b)) for b in range(5))
    for cap in sorted(set(capw[free[p][0]] for p in wide)):            # 같은 길이 묶음끼리: 압축 큰 묶음 → 자리 큰 칸
        gs = [g for g in grams if len(g) == cap]; ps = [p for p in wide if capw[free[p][0]] == cap]
        gs.sort(key=lambda g: -esz(g, free[ps[0]][0], 16)); ps.sort(key=lambda p: -room(p))
        for g, p in zip(gs, ps): item_slot[g] = p
    sz = {}
    for ch in need:
        img, _ = glyph_img(ch, 16, 16); sz[ch] = min(len(bcomp.encode(bytes(((img.ravel()[0::2] << 4) | img.ravel()[1::2]).astype(np.uint8)), b)) for b in range(5))
    sq = list(single)
    for ch in sorted(need, key=lambda c: -sz[c]):
        p = sq.pop(0); item_slot[ch] = p
    for k, p in KEEP.items(): item_slot[k] = p
    for k, p in PUNCT.items(): item_slot[k] = p
    # 조각 그림
    os.makedirs(os.path.join(ROOT, 'work', 'gfx'), exist_ok=True); os.makedirs(os.path.join(ROOT, 'work', 'raw'), exist_ok=True)
    adv = {}
    for it, p in item_slot.items():
        w, h, _ = slots[p]
        if it in KEEP:
            g = idx_of(bcomp.decode_blob(P[p:p + 3000]), w, h); xs = np.where(g.any(0))[0]; adv[it] = xs[-1] + 2; continue
        if it in PUNCT: img = punct_img(it); adv[it] = 4
        else: img, iw = glyph_img(it, w, h); adv[it] = iw + 1
        data = pack(img); n = int.from_bytes(P[p:p + 2], 'big'); assert len(data) == n
        enc = min(len(bcomp.encode(data, b)) for b in range(5))
        assert enc <= room(p), ('조각 자리 넘침', it, hex(p), enc, room(p))
        open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p), 'wb').write(data)
    adv[' '] = 4
    # 문장 기록 다시 쓰기
    pv = []
    for st, R in sorted(L.items()):
        G = [r for r in R if is_glyph(r)]
        ys0 = sorted({r['y'] for r in G if r['h'] == 16})
        line_x = {y: min(r['x'] for r in G if r['y'] == y and r['h'] == 16) for y in ys0}
        ys = list(range(ys0[0], ys0[-1] + 1, 16))                     # 빈 줄(원문 y 144 등)도 한 줄로 셈
        lx0 = min(line_x.values())
        xmax = max(r['x'] + r['w'] for r in G)
        place = []
        for li, line in enumerate(text[st]):
            y = ys[li] if li < len(ys) else ys[-1] + 16 * (li - len(ys) + 1)
            if line == '': continue
            if line.startswith('#'):                                 # 선택지: 원래 はい·いいえ 자리
                xs = sorted(r['x'] for r in G if r['y'] == y); groups = [[xs[0]]]
                for x in xs[1:]:
                    if x - groups[-1][-1] > 20: groups.append([x])
                    else: groups[-1].append(x)
                parts = line.strip('#').split('#'); segs = list(zip([g[0] for g in groups], parts))
            else:
                segs = [(line_x.get(y, lx0), line.lstrip('@'))]
            for x, s in segs:
                for t in tokenize(s, grams):
                    if t != ' ':
                        dy = 8 if t in PUNCT else 0
                        place.append((t, x, y + dy))
                    x += adv[t]
                assert x <= xmax + 4, ('줄 넘침', hex(st), s, x, xmax)
        assert len(place) <= len(G), ('기록 모자람', hex(st), len(place), len(G))
        buf = bytearray(P[R[0]['off']:R[-1]['off'] + 20])
        for i, r in enumerate(G):
            t, x, y = place[i] if i < len(place) else place[0]
            p = item_slot[t]; w, h, iid = slots[p]
            o = r['off'] - R[0]['off']
            struct.pack_into('>H', buf, o + 2, iid); buf[o + 8] = w // 8; buf[o + 9] = h
            struct.pack_into('>hh', buf, o + 10, x, y); struct.pack_into('>I', buf, o + 16, p + D)
        open(os.path.join(ROOT, 'work', 'raw', '%06X.bin' % R[0]['off']), 'wb').write(bytes(buf))
        pv.append((st, place, G))
        print('%06X 기록 %d 중 %d 씀' % (st, len(G), len(place)))
    preview(pv, item_slot, slots)


def idx_of(data, w, h):
    a = np.frombuffer(data, np.uint8)
    return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


def pack(idx):
    f = idx.ravel()
    return bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def preview(pv, item_slot, slots):
    imgs = []
    for st, place, G in pv:
        def canvas(items):
            x0 = min(0, min(x for _, x, _, _ in items)); W = 320; H = max(y + h for _, _, y, h in items) + 4
            c = np.full((H, W), 40, np.uint8)
            for g, x, y, h in items:
                sub = c[y:y + g.shape[0], x:x + g.shape[1]]; sub[g[:sub.shape[0], :sub.shape[1]] > 0] = 230
            return c
        orig = []
        for r in G:
            g = idx_of(bcomp.decode_blob(P[r['p']:r['p'] + 3000]), r['w'], r['h']); orig.append((g, r['x'], r['y'], r['h']))
        new = []
        for t, x, y in place:
            p = item_slot[t]; w, h, _ = slots[p]
            fn = os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p)
            g = idx_of(open(fn, 'rb').read(), w, h) if os.path.exists(fn) else idx_of(bcomp.decode_blob(P[p:p + 3000]), w, h)
            new.append((g, x, y, h))
        a, b = canvas(orig), canvas(new); H = max(a.shape[0], b.shape[0])
        row = np.full((H, 650), 90, np.uint8); row[:a.shape[0], :320] = a; row[:b.shape[0], 330:650] = b
        imgs.append(row)
    S = np.concatenate([np.concatenate([r, np.full((4, 650), 0, np.uint8)]) for r in imgs])
    out = os.path.join(ROOT, 'work', 'check', '그림미리보기'); os.makedirs(out, exist_ok=True)
    Image.fromarray(S).resize((S.shape[1] * 2, S.shape[0] * 2), Image.NEAREST).save(os.path.join(out, '저장안내문_원본_한글.png'))


if __name__ == '__main__':
    main()
