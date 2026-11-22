# -*- coding: utf-8 -*-
r"""대전 성적표 머리줄(배경 면 NBG1 칸 그림, 2026-11-22 하스피 실기) — 勝率·Bポイント·勝ち数·ステージ1‥8
  출처: PROGRAM.BIN 0x43ACE4 = [u32 VRAM 0x25E34000][u16 0x8000][u16 크기 4736][bcomp 압축] (메뉴 묶음, 스테이트 VRAM 0x34000 과 일치 확인)
  칸 번호 = 6656 + (덩어리 안 위치 / 32). 머리줄 = 칸 6×2(48×16):
    勝率 6666‥6671/6682‥6687 · Bポイント 6720‥6725/6736‥6741 · 勝ち数 6726‥6731/6742‥6747
    ステージN = 6732(왼쪽 테두리+ス) 6657 6658 6659 + 숫자 칸 쌍(6660/6661·6662/6663·6664/6665·6688/6689·6690/6691·6692/6693·6694/6695 …)
              아랫줄 6672 6673 6674 6675 + (6676/6677 …) — ジ 끝(32‥36열)이 숫자 칸 첫 칸에 걸침
  출력 work/nbg/43ACE4.bin(푼 덩어리 전체) → build.py 가 압축해 제자리. 미리보기 work/check/그림미리보기/성적표_머리줄_원본_한글.png
  python tools/nbg_score.py"""
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp
from gfx_custom_menu import dil8

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
BLOB = 0x43ACE4; C0 = 6656
F11 = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Bold.ttf'
F11C = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Condensed.ttf'
HEAD = [('勝率', '승률', list(range(6666, 6672)), list(range(6682, 6688))),
        ('Bポイント', 'B포인트', list(range(6720, 6726)), list(range(6736, 6742))),
        ('勝ち数', '승리 수', list(range(6726, 6732)), list(range(6742, 6748)))]
STAGE_TOP = [6732, 6657, 6658, 6659]; STAGE_BOT = [6672, 6673, 6674, 6675]
DIGIT_FIRST_TOP = [6660, 6662, 6664, 6688, 6690, 6692, 6694, 6696]      # 숫자 칸 쌍의 첫 칸(ジ 끝이 걸침, 0‥4열)
DIGIT_FIRST_BOT = [6676, 6678, 6680, 6704, 6706, 6708, 6710, 6712]


def load():
    n = struct.unpack_from('>H', P, BLOB + 6)[0]
    d, used = bcomp.decode(P[BLOB + 8:BLOB + 8 + n * 2 + 300], n); assert len(d) == n
    return bytearray(d), n, used


def get(d, ch):
    a = np.frombuffer(bytes(d[(ch - C0) * 32:(ch - C0) * 32 + 32]), np.uint8); return np.stack([a >> 4, a & 15], 1).ravel().reshape(8, 8).astype(int)


def put_cell(d, ch, px):
    f = px.ravel(); d[(ch - C0) * 32:(ch - C0) * 32 + 32] = bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def plate(d, top, bot):
    return np.vstack([np.hstack([get(d, c) for c in top]), np.hstack([get(d, c) for c in bot])])


def unplate(d, top, bot, img):
    for k, c in enumerate(top): put_cell(d, c, img[0:8, k * 8:k * 8 + 8])
    for k, c in enumerate(bot): put_cell(d, c, img[8:16, k * 8:k * 8 + 8])


def mask(t, fp, fs):
    im = Image.new('L', (200, 30), 0); ImageDraw.Draw(im).text((2, 2), t, font=ImageFont.truetype(fp, fs), fill=255)
    m = np.array(im) > 127; yy, xx = np.where(m); return m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]


def draw(img, m, x0, x1, fill, out):
    """글자를 [x0,x1) 가운데, 1‥13행 가운데에 속 fill·외곽 out"""
    H, W = m.shape; assert W + 2 <= x1 - x0 and H + 2 <= 13, ('안 들어감', m.shape, x1 - x0)
    y = 1 + (13 - H) // 2; x = x0 + (x1 - x0 - W) // 2
    M = np.zeros(img.shape, bool); M[y:y + H, x:x + W] = m
    img[dil8(M) & ~M] = out; img[M] = fill


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    d, n, used = load(); orig = bytes(d); rows = []
    for ja, ko, top, bot in HEAD:                                   # 바탕 c 로 안쪽(1‥13행, 1‥46열) 지우고 속 9·외곽 8
        o = plate(d, top, bot); img = o.copy(); img[1:14, 1:46] = 0xC
        draw(img, mask(ko, F11, 12), 1, 46, 0x9, 0x8); unplate(d, top, bot, img); rows.append((o, img))
    # ステージ: 원본처럼 테두리 칸 다음(1열)부터 숫자 칸 첫머리(36열)까지 → 스테이지(좁은 글꼴), 어두운 글자 속 1·외곽 8.
    #   32‥36열은 숫자 칸 쌍 8개의 첫 칸(0‥4열)이라 같은 그림을 8벌 다 씀(숫자 상자 5열~ 는 그대로)
    top5 = STAGE_TOP + [DIGIT_FIRST_TOP[0]]; bot5 = STAGE_BOT + [DIGIT_FIRST_BOT[0]]
    o = plate(d, top5, bot5); img = o.copy(); img[1:14, 1:37] = 0xC; img[14:, 32:37] = o[14:, 32:37]
    draw(img, mask('스테이지', F11C, 12), 1, 37, 0x1, 0x8)
    unplate(d, STAGE_TOP, STAGE_BOT, img[:, :32]); rows.append((o, img))
    for t, b in zip(DIGIT_FIRST_TOP, DIGIT_FIRST_BOT):
        for ch, part in ((t, img[0:8, 32:37]), (b, img[8:16, 32:37])):
            px = get(d, ch); keep = px.copy(); px[:, 0:5] = part
            if ch == t: px[0] = keep[0]                               # 맨 윗줄 테두리 b 는 원래대로
            put_cell(d, ch, px)
    enc = min((bcomp.encode(bytes(d), b) for b in range(5)), key=len)
    room = used
    while room % 4: room += 1
    print('압축 %d / 자리 %d (원래 %d)' % (len(enc), room, used))
    assert len(enc) <= room, '자리 넘침'
    os.makedirs(os.path.join(ROOT, 'work', 'nbg'), exist_ok=True)
    open(os.path.join(ROOT, 'work', 'nbg', '%06X.bin' % BLOB), 'wb').write(bytes(d))
    # 미리보기: 스테이트(work/mem/ss) VDP2 VRAM 0x34000 에 새 칸을 넣고 NBG1 머리줄을 실제 색으로 그림(원본 | 한글)
    import shutil, vdp2render as V
    src = os.path.join(ROOT, 'work', 'mem', 'ss'); dst = os.path.join(ROOT, 'work', 'mem', 'ss_kr')
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        v = bytearray(open(os.path.join(src, 'VDP2_VRAM.bin'), 'rb').read()); assert bytes(v[0x34000:0x34000 + n]) == orig
        v[0x34000:0x34000 + n] = d; open(os.path.join(dst, 'VDP2_VRAM.bin'), 'wb').write(v)
        a0 = np.asarray(V.render('ss', 1)[0])[0:16, 0:512]; a1 = np.asarray(V.render('ss_kr', 1)[0])[0:16, 0:512]
        S = np.vstack([a0, np.full((4, 512, 3), 90, np.uint8), a1])
        Image.fromarray(S).resize((S.shape[1] * 3, S.shape[0] * 3), Image.NEAREST).save(os.path.join(ROOT, 'work', 'check', '그림미리보기', '성적표_머리줄_원본_한글.png'))


if __name__ == '__main__':
    main()
