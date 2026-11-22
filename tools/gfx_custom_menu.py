# -*- coding: utf-8 -*-
r"""미추출 메뉴 판 중 구조가 제각각인 것(2026-11-22) — 판마다 전용 규칙으로 work/gfx/<P>.bin
  490368 «全» 덧씌움(24×16, 녹색 試合 판 왼쪽) → 총 · 4911FC Bポイント → B포인트(B 원본 유지)
  493440 やっつけ! → 처치! · 49366C やられ! → 당함!(줄마다 바탕 메우고 속 8·외곽 1·윗가장자리 9)
  4BB170‥4BB58C 白赤青黄緑チーム → 백·적·청·황·녹 팀(앞 글자 속 f·외곽 5, 팀 = 5)
  python tools/gfx_custom_menu.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
F11 = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Bold.ttf'
F9 = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri9.ttf'
F11C = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Condensed.ttf'
NEB = r'C:/claude/utils/font/nanum-gothic/NanumGothicExtraBold.ttf'


def load(p, w, h):
    n = int.from_bytes(P[p:p + 2], 'big'); a = np.frombuffer(bcomp.decode_blob(P[p:p + 4 + n * 2 + 300]), np.uint8)
    return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


def room(p):
    n = int.from_bytes(P[p:p + 2], 'big'); e = p + 4 + bcomp.decode(P[p + 4:p + 4 + n * 2 + 300], n)[1]
    while e % 4: e += 1
    return e - (p + 4)


def mask(t, fp, fs):
    im = Image.new('L', (200, 40), 0); ImageDraw.Draw(im).text((2, 2), t, font=ImageFont.truetype(fp, fs), fill=255)
    m = np.array(im) > 127; yy, xx = np.where(m); return m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]


def big_mask(t, h):
    """나눔고딕 ExtraBold 4배 그려 문턱 — 잉크 높이 h 이하 중 가장 큰 크기"""
    for fs in range(30, 8, -1):
        im = Image.new('L', (400 * 4, 40 * 4), 0); ImageDraw.Draw(im).text((8, 8), t, font=ImageFont.truetype(NEB, fs * 4), fill=255)
        a = np.array(im, np.float32) / 255; yy, xx = np.where(a > 0.1); a = a[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        H = -(-a.shape[0] // 4) * 4; W = -(-a.shape[1] // 4) * 4
        m = np.pad(a, ((0, H - a.shape[0]), (0, W - a.shape[1]))).reshape(H // 4, 4, W // 4, 4).mean((1, 3)) >= 0.5
        yy, xx = np.where(m); m = m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        if m.shape[0] <= h: return m


def dil8(m):
    p = np.pad(m, 1); o = np.zeros_like(m)
    for dy in range(3):
        for dx in range(3): o |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
    return o


def put(out, m, y, x, fill, outline=None, hi=None):
    H, W = m.shape; M = np.zeros(out.shape, bool); M[y:y + H, x:x + W] = m
    if outline is not None: out[dil8(M) & ~M] = outline
    out[M] = fill
    if hi is not None:                                               # 윗가장자리 밝은 색(원본 9)
        up = np.zeros_like(M); up[1:] = M[:-1]; out[M & ~up] = hi


def zen(o):
    out = o.copy(); out[1:, 1:] = 7
    m = mask('총', F11, 12); y = 1 + (15 - m.shape[0]) // 2; x = 1 + (23 - m.shape[1]) // 2
    put(out, m, y, x, 0xA, 0x2); return out


def bpoint(o):
    out = o.copy(); out[5:20, 14:43] = 0xA
    m = mask('포인트', F9, 10); assert m.shape[1] <= 29, m.shape
    y = 6 + (14 - m.shape[0]) // 2; x = 14 + (29 - m.shape[1]) // 2
    put(out, m, y, x, 0x7, 0x2); return out


def shout(o, ko):
    out = o.copy(); T = {1, 8, 9}
    for y in range(1, 17):                                           # 줄 바탕 = 글자 색 아닌 칸 최빈값
        row = [v for v in o[y, 1:79] if v not in T]; bg = max(set(row), key=row.count); out[y, 1:79] = bg
    m = big_mask(ko, 12); y = 2 + (13 - m.shape[0]) // 2; x = (80 - m.shape[1]) // 2
    put(out, m, y, x, 0x8, 0x1, 0x9); return out


def master_btn(o, ko):
    """마스터 再挑戦·終了(56×24): 판 안쪽(3‥20행, 3‥52열) 바탕 8, 글자 = 어두운 1(원본처럼 외곽선 없음)"""
    out = o.copy(); out[3:21, 3:53] = 0x8
    m = big_mask(ko, 15); y = 3 + (18 - m.shape[0]) // 2; x = 3 + (50 - m.shape[1]) // 2
    put(out, m, y, x, 0x1); return out


def two_tone(o):
    """やっつけ/やられ 두 색 판(112×24, 493130): 글자 칸(1·8·9)을 같은 줄 가장 가까운 바탕색으로 메워 빗금 경계 유지, 왼쪽 처치·오른쪽 당함"""
    out = o.copy()
    for y in range(1, 17):                                           # 줄마다 왼쪽 바탕(최빈)·오른쪽 바탕(최빈), 경계 = 50‥70열에서 오른쪽 색이 처음 나오는 곳
        L = [v for v in o[y, 1:56] if v not in (1, 8, 9)]; R = [v for v in o[y, 62:111] if v not in (1, 8, 9)]; Lm = max(set(L), key=L.count); Rm = max(set(R), key=R.count)
        b = next((x for x in range(50, 71) if o[y, x] == Rm), 58)
        out[y, 1:b] = Lm; out[y, b:111] = Rm
        if 0 < b - 1 and o[y, b - 1] not in (1, 8, 9, Lm): out[y, b - 1] = o[y, b - 1]   # 경계 한 칸 바림 유지
    for ko, a, b in (('처치', 1, 57), ('당함', 59, 111)):
        m = big_mask(ko, 12); put(out, m, 2 + (13 - m.shape[0]) // 2, a + (b - a - m.shape[1]) // 2, 0x8, 0x1, 0x9)
    return out


def team_box(o, ch):
    """白チーム 사본(40×24, 4AB2D4 등): 위 4줄(머리띠) 유지, 그 아래 바탕 6 으로 지우고 왼쪽 큰 색 글자(속 1·외곽 = 원본 외곽색 f/d), 오른쪽 «팀»(f)"""
    from collections import Counter
    oc = Counter(int(v) for v in o[4:23, 1:17].ravel() if v not in (1, 6, 7)).most_common(1) or [(0xF, 0)]
    oc = oc[0][0]
    out = o.copy(); out[4:23, 1:39] = 0x6
    m = big_mask(ch, 16); put(out, m, 4 + (18 - m.shape[0]) // 2, 2 + (15 - m.shape[1]) // 2, 0x1, oc)
    b = mask('팀', F11, 12); put(out, b, 11, 18 + (20 - b.shape[1]) // 2, 0xF)
    return out


def which_stage(o):
    """«どのステージに / いどうする?»(72×24 투명, 글자 f): 두 줄 → 어느 스테이지로 / 이동할까?"""
    out = np.zeros_like(o)
    a = mask('어느 스테이지로', F11C, 12); b = mask('이동할까?', F11C, 12)
    put(out, a, 0, 0, 0xF); put(out, b, 12, 16, 0xF); return out


def sfx_vert(o, a, b):
    """세로 두 글자 효과음(0237F4 16×40 «バブ»→바부, 02AF60 24×48 «ギャオ»→갸오): 원본처럼 글자마다 칸(폭 × 높이/2)을 바깥선까지 꽉 채움
       — 큰 글꼴 잉크를 (폭−2)×(칸 높이−2) 로 늘려 그리고 외곽 b(1px)·속 2·윗가장자리 f"""
    h, w = o.shape; out = np.zeros_like(o); hh = h // 2
    for k, ch in enumerate((a, b)):
        m = big_mask(ch, 28)
        m = np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((w - 2, hh - 2), Image.LANCZOS)) >= 128
        put(out, m, k * hh + 1, 1, 0x2, 0xB, 0xF)
    return out


def team(o, ch):
    out = o.copy(); out[2:15, 3:46] = 0x2
    a = mask(ch, F11, 12); b = mask('팀', F11, 12)
    put(out, a, 2 + (13 - a.shape[0]) // 2, 3 + (13 - a.shape[1]) // 2, 0xF, 0x5)
    put(out, b, 2 + (13 - b.shape[0]) // 2, 20, 0x5)                                   # 앞 글자 바로 뒤(원본 チーム 시작 자리)
    return out


JOBS = [(0x52BAA0, 56, 24, lambda o: master_btn(o, '재도전')), (0x52BC80, 56, 24, lambda o: master_btn(o, '종료')), (0x493130, 112, 24, two_tone),
        (0x490368, 24, 16, zen), (0x0237F4, 16, 40, lambda o: sfx_vert(o, '바', '부')), (0x02AF60, 24, 48, lambda o: sfx_vert(o, '갸', '오')), (0x039FCC, 72, 24, which_stage),
        *[(p, 40, 24, (lambda c: lambda o: team_box(o, c))(c)) for p, c in zip((0x4AB2D4, 0x4AB8FC, 0x4ABA18, 0x4ABB2C, 0x4ABC38), '백적청황녹')], (0x4911FC, 48, 24, bpoint),
        (0x493440, 80, 24, lambda o: shout(o, '처치!')), (0x49366C, 80, 24, lambda o: shout(o, '당함!'))] + \
       [(p, 48, 16, (lambda c: lambda o: team(o, c))(c)) for p, c in zip((0x4BB170, 0x4BB288, 0x4BB390, 0x4BB48C, 0x4BB58C), '백적청황녹')]


def pack(idx):
    f = idx.ravel(); return bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for p, w, h, fn in JOBS:
        new = fn(load(p, w, h)); b = pack(new)
        enc = min((bcomp.encode(b, k) for k in range(5)), key=len)
        print('%06X 압축 %3d / 자리 %3d%s' % (p, len(enc), room(p), '' if len(enc) <= room(p) else '  ⚠️넘침'))
        if len(enc) <= room(p): open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p), 'wb').write(b)


if __name__ == '__main__':
    main()
