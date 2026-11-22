# -*- coding: utf-8 -*-
r"""스샷 9 세로쓰기 이야기(마스터 모드 시작, 2026-11-22) — 4D4540 묶음 스프라이트 묶음 하나(목록 포인터 0x50E748 → P 0x54B268, 20 B 기록 20개 + 끝표 8000 0009)
  조각 = 폭 16 세로 글자 조각 18개(색 1 몸통·2/3 가장자리, 투명 바탕, colr 0x3200). 기록 +0 깃발(0x30 = 뒤집기, 15번만) · +2 번호 · +8 크기 · +10 x · +12 y · +16 포인터(파일 − 0x280000).
  방법: 조각 칸에 한글 낱말 조각을 새로 그림 → 기록 20개의 번호·크기·x·y·포인터를 다시 씀(조각마다 원래 번호 유지, 깃발 칸은 그대로라 뒤집힌 ” = 15번 자리).
  출력: work/gfx/<조각 P>.bin · work/raw/54B268.bin · 미리보기 work/check/그림미리보기/스샷9_세로쓰기_*.png
  python tools/story_vert.py [글꼴 이름]"""
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp, vdp2render as V

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
D = 0x280000; LIST = 0x54B268; NREC = 20
FONTS = {'blackhansans': r'C:/claude/utils/font/blackhansans/BlackHanSans-Regular.ttf',
         'dohyeon': r'C:/claude/utils/font/dohyeon/DoHyeon-Regular.ttf',
         'jua': r'C:/claude/utils/font/jua/Jua-Regular.ttf',
         'nanumeb': r'C:/claude/utils/font/nanum-gothic/NanumGothicExtraBold.ttf'}
PITCH = 16; GAP = 8                                                   # 글자 간격·띄어쓰기

# 줄(열) = 오른쪽부터. 조각 토큰 목록, ' ' = 띄어쓰기, '“' '”' = 원래 ” 조각(뒤집기)
COLS = [(56, ['봄버', '의', ' ', '극', '에']),                      # 하스피 문구 «봄버의 극에 / 달하고자»(쉼표 없음)
        (24, ['달하고자']),
        (-8, ['지', '금', ' ', '한', ' ', '명', '의', ' ', '봄버', '맨이']),
        (-40, ['“', '봄버', ' ', '사원', '”', '에']),
        (-72, ['도전하는', ' ', '것이', '었다'])]
QUOTE = 0x5146FC; COMMA = 0x514120                                   # 원래 ” (16×8)·、(8×8) 조각은 그대로 씀


def records():
    R = []
    for i in range(NREC):
        r = P[LIST + i * 20:LIST + i * 20 + 20]
        R.append(dict(fl=r[0:2], id=struct.unpack_from('>H', r, 2)[0], w=r[8] * 8, h=r[9],
                      x=struct.unpack_from('>h', r, 10)[0], y=struct.unpack_from('>h', r, 12)[0],
                      p=struct.unpack_from('>I', r, 16)[0] + D))
    assert P[LIST + NREC * 20:LIST + NREC * 20 + 4] == b'\x80\x00\x00\x09'
    return R


def room(b):
    n = int.from_bytes(P[b:b + 2], 'big'); e = b + 4 + bcomp.decode(P[b + 4:b + 4 + n * 2 + 300], n)[1]
    while e % 4: e += 1
    return e - (b + 4)


def orig_idx(p, w, h):
    n = int.from_bytes(P[p:p + 2], 'big'); a = np.frombuffer(bcomp.decode_blob(P[p:p + 4 + n * 2 + 300]), np.uint8)
    return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


_REF = {}
def SCALE_REF(fp, S):
    if fp not in _REF:
        big = Image.new('L', (40 * S, 40 * S), 0); ImageDraw.Draw(big).text((4 * S, 4 * S), '봄', font=ImageFont.truetype(fp, 30 * S), fill=255)
        ys, xs = np.where(np.array(big) > 127); _REF[fp] = ys.max() + 1 - ys.min()
    return _REF[fp]


def syl(ch, fp, size):
    """한 음절 16×16: 4배로 그려 줄여 덮임 비율 → 1(몸통)·2·3(가장자리)"""
    S = 8; big = Image.new('L', (40 * S, 40 * S), 0); f = ImageFont.truetype(fp, 30 * S)
    ImageDraw.Draw(big).text((4 * S, 4 * S), ch, font=f, fill=255)
    a = np.array(big); ys, xs = np.where(a > 127)
    k = 15 * S / SCALE_REF(fp, S)                                    # 글꼴 하나에 배율 하나(«봄» 잉크 높이 = 15)
    ink = big.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    nw, nh = min(15 * S, round(ink.width * k)), min(15 * S, round(ink.height * k))
    ink = ink.resize((nw, nh), Image.LANCZOS)
    im = Image.new('L', (16 * S, 16 * S), 0); im.paste(ink, (S + (15 * S - nw) // 2, S + (15 * S - nh) // 2))
    a = np.array(im, float).reshape(16, S, 16, S).mean((1, 3)) / 255
    out = np.zeros((16, 16), int); out[a >= 0.2] = 3; out[a >= 0.45] = 2; out[a >= 0.7] = 1
    out[0, :] = 0; out[:, 0] = 0                                     # 원본처럼 위·왼쪽 1px 비움
    return out


def piece(tok, fp, size, h):
    out = np.zeros((h, 16), int)
    for i, ch in enumerate(tok): out[i * PITCH:i * PITCH + 16] = syl(ch, fp, size)
    return out


def pack(idx):
    f = idx.ravel(); return bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    fname = next((a for a in sys.argv[1:] if not a.startswith('-')), 'dohyeon'); fp = FONTS[fname]; size = 15
    R = records()
    slots = {}                                                       # 조각 P → (w, h, 번호)
    for r in R: slots.setdefault(r['p'], (r['w'], r['h'], r['id']))
    toks = []
    for _, col in COLS:
        for t in col:
            if t not in (' ', '“', '”', '、') and t not in toks: toks.append(t)
    free = sorted([p for p in slots if p not in (QUOTE, COMMA)], key=lambda p: slots[p][1])
    assign = {}
    for t in sorted(toks, key=lambda t: -len(t)):                     # 긴 낱말부터 들어가는 가장 작은 칸
        need = len(t) * PITCH
        p = next(p for p in free if slots[p][1] >= need and p not in assign.values()); assign[t] = p
    # 조각 그림 + 압축 검사
    gfx = {}
    for t, p in assign.items():
        w, h, _ = slots[p]; img = piece(t, fp, size, h)
        enc = min((bcomp.encode(pack(img), b) for b in range(5)), key=len)
        print('%-6s → %06X %2d×%-3d 압축 %3d / 자리 %3d%s' % (t, p, w, h, len(enc), room(p), '' if len(enc) <= room(p) else '  ⚠️넘침'))
        gfx[p] = img
    # 기록
    recs = []
    for x, col in COLS:
        y = -104
        for t in col:
            if t == ' ': y += GAP; continue
            if t == '“': recs.append(('“', QUOTE, x + 8, y)); y += 8; continue
            if t == '”': recs.append(('”', QUOTE, x - 8, y)); y += 8 + 3; continue
            if t == '、': recs.append(('、', COMMA, x + 8, y - 2)); y += 8; continue
            recs.append((t, assign[t], x, y)); y += len(t) * PITCH
        assert y <= 96, ('열이 화면 밖', x, y)
    assert len(recs) <= NREC, len(recs)
    flip = [r for r in recs if r[0] == '”']; rest = [r for r in recs if r[0] != '”']
    order = rest[:15] + flip + rest[15:]
    while len(order) < NREC: order.append(order[-1])                  # 남는 기록은 마지막 것과 똑같이 겹침
    assert order[15][0] == '”' and R[15]['fl'] == b'\x00\x30'
    raw = bytearray(P[LIST:LIST + NREC * 20])
    for i, (t, p, x, y) in enumerate(order):
        w, h, rid = slots[p]
        struct.pack_into('>H', raw, i * 20 + 2, rid); raw[i * 20 + 8] = w // 8; raw[i * 20 + 9] = h
        struct.pack_into('>hh', raw, i * 20 + 10, x, y); struct.pack_into('>I', raw, i * 20 + 16, p - D)
    # 미리보기(글자판): 원본 조각|한글 조각, 그리고 기록대로 놓은 글자 배치(바탕 없음)
    _, _, cram = V.load('s9'); cram = np.asarray(cram).astype(int)
    def rgb(ix):
        e = cram[((0x3200 & 0x7F0) + ix) & 0x7FF]
        im = np.stack([(e & 31) << 3, (e >> 5 & 31) << 3, (e >> 10 & 31) << 3], -1).astype(np.uint8); im[ix == 0] = (40, 60, 70); return im
    def layout(rs, src):
        c = np.zeros((224, 320), int)
        for fl, p, x, y in rs:
            w, h, _ = slots[p]; img = src(p, w, h)
            if fl: img = img[::-1, ::-1]
            X, Y = 160 + x, 112 + y
            sub = c[Y:Y + h, X:X + w]; m = img[:sub.shape[0], :sub.shape[1]] != 0; sub[m] = img[:sub.shape[0], :sub.shape[1]][m]
        return c[:, 60:240]
    o_rs = [(r['fl'] == b'\x00\x30', r['p'], r['x'], r['y']) for r in R]
    n_rs = [(i == 15, p, x, y) for i, (t, p, x, y) in enumerate(order)]
    newsrc = lambda p, w, h: gfx[p] if p in gfx else orig_idx(p, w, h)
    L = np.concatenate([rgb(layout(o_rs, orig_idx)), np.full((224, 4, 3), 90, np.uint8), rgb(layout(n_rs, newsrc))], 1)
    out = os.path.join(ROOT, 'work', 'check', '그림미리보기', '스샷9_세로쓰기_%s_원본_한글.png' % fname)
    Image.fromarray(L).resize((L.shape[1] * 3, L.shape[0] * 3), Image.NEAREST).save(out); print('미리보기', out)
    if '--write' in sys.argv:
        for p, img in gfx.items(): open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % p), 'wb').write(pack(img))
        open(os.path.join(ROOT, 'work', 'raw', '%06X.bin' % LIST), 'wb').write(bytes(raw)); print('work/gfx·raw 기록')


if __name__ == '__main__':
    main()
