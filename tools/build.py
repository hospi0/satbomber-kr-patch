# -*- coding: utf-8 -*-
r"""새턴 봄버맨 빌드(2026-11-22) — PROGRAM.BIN 안 그림 자료를 한글 판으로 바꾸고 트랙 01 제자리 쓰기 + MODE1 EDC/ECC
  바꿀 그림: work/gfx/<자료 P 16진>.bin (풀린 바이트, tools/gfx_button.py 등) → bcomp.encode(b1 = 원래 값부터 시도)
  자리: 원래 압축 끝 ~ 다음 4 바이트 정렬까지(넘치면 빌드 실패 — 옮기기는 아직 없음). 남는 바이트는 원본 그대로.
  검산: 바꾼 자료 다시 풀기 = 한글 판 · PROGRAM.BIN 크기 같음 · 바뀐 섹터가 PROGRAM.BIN 안 · 되읽기 일치.
  python tools/build.py [--write] [--install]   ⛔--write·--install 은 하스피 허락 받고
"""
import glob, hashlib, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp
from iso import Disc, ROMS
from cdrom_ecc import recalc_sector

F_DIR = r'F:\hospi\roms\ss roms\Saturn Bomberman (Japan)'
OUT = os.path.join(ROOT, 'dist', 'build', 'Saturn Bomberman (Japan)')


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''): h.update(c)
    return h.hexdigest()


PIECE_COPY = (0x18080, 0x31B80, 0x4E59C)    # s_init 조각 구역의 사본(다른 묶음, D 0x1A4000) — 바이트 같음(2026-11-22 확인)
LIST_COPY = (0x45400, 0x4A000, 0x5AB90, -0x5A64)   # s_init 저장 화면 목록 159개의 사본: 위치 +0x5AB90, 포인터 −0x5A64


def gfx_jobs(P):
    """work/gfx 판 + s_init 조각 구역이면 사본 자리에도 같은 그림"""
    out = []
    for fn in sorted(glob.glob(os.path.join(ROOT, 'work', 'gfx', '*.bin'))):
        bl = int(os.path.basename(fn)[:-4], 16); new = open(fn, 'rb').read(); out.append((bl, new))
        a, b, d = PIECE_COPY
        if a <= bl < b:
            n = int.from_bytes(P[bl:bl + 2], 'big')
            assert P[bl:bl + 4 + n * 2 + 300] == P[bl + d:bl + d + 4 + n * 2 + 300], ('사본 조각이 원본과 다름', hex(bl))
            out.append((bl + d, new))
    return out


def patch_program(P):
    P = bytearray(P)
    for bl, new in gfx_jobs(P):
        n = int.from_bytes(P[bl:bl + 2], 'big'); ty = int.from_bytes(P[bl + 2:bl + 4], 'big')
        assert ty != 5 and len(new) == n, ('크기·방식 다름', hex(bl), len(new), n, ty)
        src = bytes(P[bl + 4:bl + 4 + n * 2 + 300]); used = bcomp.decode(src, n)[1]
        end = bl + 4 + used
        while end % 4: end += 1
        room = end - (bl + 4)
        b1s = ([src[1]] + [b for b in range(5) if b != src[1]]) if src[0] else list(range(5))
        enc = min((bcomp.encode(new, b) for b in b1s), key=len)
        assert len(enc) <= room, ('자리 넘침', hex(bl), len(enc), room)
        P[bl + 4:bl + 4 + len(enc)] = enc
        assert bcomp.decode_blob(bytes(P[bl:bl + 4 + n * 2 + 300])) == new
        print('  %06X 압축 %d / 자리 %d' % (bl, len(enc), room))
    for fn in sorted(glob.glob(os.path.join(ROOT, 'work', 'raw', '*.bin'))):   # 저장 안내문 글자 기록(tools/save_msgs.py): 목록 영역 통째
        off = int(os.path.basename(fn)[:-4], 16); new = open(fn, 'rb').read()
        assert (0x45400 <= off and off + len(new) <= 0x4A000) or (off == 0x54B268 and len(new) == 400) or (0x50530 <= off and off + len(new) <= 0x52570), ('기록 덮어쓰기 범위 밖', hex(off))   # 저장 안내문 · 스샷 9 세로쓰기(story_vert.py) · 대사창 7개(dialogue.py) · 게임 오버 12프레임(gameover.py)
        old = bytes(P[off:off + len(new)])
        for i in range(0, len(new), 20):                             # 20 B 기록마다 바뀌는 칸은 번호(+2)·크기(+8)·x·y(+10)·포인터(+16)뿐
            a, b = old[i:i + 20], new[i:i + 20]
            assert a[0:2] == b[0:2] and a[4:8] == b[4:8] and a[14:16] == b[14:16], ('기록 바깥 필드가 바뀜', hex(off + i))
        P[off:off + len(new)] = new
        print('  %06X 문장 기록 %d 개' % (off, len(new) // 20))
        a0, a1, dl, dp = LIST_COPY
        if a0 <= off < a1:                                           # 사본 목록: 원래 기록이 «포인터만 dp 다른» 똑같은 것인지 확인 후 같은 변경
            c = off + dl; cold = bytes(P[c:c + len(new)]); cnew = bytearray(new)
            for i in range(0, len(new), 20):
                po = int.from_bytes(old[i + 16:i + 20], 'big'); pc = int.from_bytes(cold[i + 16:i + 20], 'big')
                assert cold[i:i + 16] == old[i:i + 16] and pc == po + dp, ('사본 목록이 원본과 다름', hex(c + i))
                cnew[i + 16:i + 20] = (int.from_bytes(new[i + 16:i + 20], 'big') + dp).to_bytes(4, 'big')
            P[c:c + len(new)] = cnew
            print('  %06X 문장 기록 %d 개(사본)' % (c, len(new) // 20))
    return bytes(P)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1)
    jobs = []                                                        # (이름, LBA, 크기, 원본, 새것)
    lba, size = next((l, s) for p, l, s in D.files if p == '/PROGRAM.BIN')
    orig = D.read('PROGRAM.BIN'); new = patch_program(orig)
    assert len(new) == size; jobs.append(('PROGRAM.BIN', lba, size, orig, new))
    for fn in sorted(glob.glob(os.path.join(ROOT, 'work', 'kr', '*.CPK'))):   # 자막 동영상(tools/moviesub.py): 같은 크기로 제자리
        nm = os.path.basename(fn); l, s = next((l, s) for p, l, s in D.files if p == '/' + nm)
        o = D.read(nm); n = open(fn, 'rb').read(); assert len(n) == s, ('동영상 크기 다름', nm, len(n), s)
        jobs.append((nm, l, s, o, n))
    if '--write' not in sys.argv:
        for nm, l, s, o, n in jobs: print('계획만 — %s 바뀐 바이트 %d' % (nm, sum(a != b for a, b in zip(o, n))))
        return
    os.makedirs(OUT, exist_ok=True)
    src_dir = os.path.dirname(ROMS[1]); t1 = os.path.join(OUT, os.path.basename(ROMS[1]))
    shutil.copyfile(ROMS[1], t1)
    for f in os.listdir(src_dir):
        q = os.path.join(src_dir, f)
        if os.path.isfile(q) and f != os.path.basename(ROMS[1]) and not os.path.exists(os.path.join(OUT, f)):
            shutil.copyfile(q, os.path.join(OUT, f))
    dirty = set()
    with open(t1, 'r+b') as fh:
        for nm, lba, size, orig, new in jobs:
            for i in range(0, size, 2048):
                if orig[i:i + 2048] == new[i:i + 2048]: continue
                s = lba + i // 2048
                fh.seek(s * 2352); sec = bytearray(fh.read(2352)); assert sec[15] == 1, ('MODE1 아님', nm, s)
                chunk = new[i:i + 2048]
                sec[16:16 + len(chunk)] = chunk
                fh.seek(s * 2352); fh.write(recalc_sector(bytes(sec))); dirty.add(s)
    N = Disc.__new__(Disc); N.n = 1; N.f = open(t1, 'rb'); N.files = D.files
    for nm, lba, size, orig, new in jobs: assert N.read(nm) == new, ('되읽기 다름', nm)
    a = open(ROMS[1], 'rb'); b = open(t1, 'rb'); bad = []
    for s in range(os.path.getsize(t1) // 2352):
        if a.read(2352) != b.read(2352) and s not in dirty: bad.append(s)
    assert not bad, ('바꾼 파일 밖 섹터가 바뀜', bad[:5])
    print('  검산 통과 · 바뀐 섹터 %d · 트랙 01 md5 %s' % (len(dirty), md5(t1)))
    if '--install' in sys.argv:
        dst = os.path.join(F_DIR, os.path.basename(ROMS[1])); assert os.path.exists(dst)
        shutil.copyfile(t1, dst); assert md5(dst) == md5(t1)
        print('  F: 설치(원래 폴더 트랙 01 덮어씀)', dst)


if __name__ == '__main__':
    main()
