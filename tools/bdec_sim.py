# -*- coding: utf-8 -*-
r"""봄버맨 압축 풀기 0x0603EA08 을 스테이트 메모리 위에서 SH-2 흉내기로 돌림(검증·기준 출력용, 2026-11-22)
  dec(state, blob) → (풀린 바이트, 걸음 수, 압축 자료 끝 주소) (blob = 스프라이트 자료 머리 주소: u16 풀린 크기, u16 방식, +4 압축 자료)"""
import os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import sh2sim as S

STOP = 0x0600DEA0                          # 돌아올 가짜 주소(0KRNL 안 아무 곳 — PR 로만 씀)


def load_mem(state):
    m = S.Mem()
    d = os.path.join(ROOT, 'work', 'mem', state)
    m.map(0x00200000, open(os.path.join(d, 'WorkRAML.bin'), 'rb').read())
    m.map(0x06000000, open(os.path.join(d, 'WorkRAMH.bin'), 'rb').read())
    return m


def dec(state, blob, dst=0x002FB000):
    m = load_mem(state)
    n = m.r16(blob)
    c = S.CPU(m, 0x0603EA08, {4: blob + 4, 5: dst, 6: n}, stack_top=0x060FFF00)
    c.pr = STOP
    steps = c.run(STOP, 20_000_000)
    out = bytes(m.r8(dst + i) for i in range(n))
    end = m.r32(0x060C2404)                    # 풀기 상태 구조체 +0 = 읽은 끝(원본 포인터)
    return out, steps, end
