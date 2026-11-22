# -*- coding: utf-8 -*-
r"""글자판 스프라이트 한글화 — 범용(2026-11-22, 하스피 «내가 준 스샷에서 바꿔» — 스샷 4~7 BOMBER STADIUM 화면)
  JOBS = (자료 P, 폭, 높이, 원문, 한글, 색 뱅크, 스테이트)
  1) 바탕색 = 판 안쪽 왼·오른 가장자리 4열에 나오는 색, 글자색 = 판 안쪽에서 그 밖의 색
  2) 글자 칸 지우기 = 가로 주기(1‥16) 중 바탕과 가장 잘 맞는 주기로 같은 줄 무늬 복사(빗금 바탕 대응)
  3) 새 글자 = 원래 글자 높이에 맞는 갈무리(12px 이상 = Galmuri11 Bold, 아니면 Galmuri9), 속 = 글자색 중 가장 많은 색,
     외곽선(8방향) = 바탕과 닿은 글자 칸에 가장 많은 색
  4) 압축: 배치(가로 ±2, 세로 ±1) 중 원래 자리(압축 끝~4 B 정렬)에 들어가는 것 → work/gfx/<P>.bin
  미리보기: work/check/그림미리보기/스샷4-7_글자판_원본_한글.png (실제 색, 스테이트 CRAM)
  python tools/gfx_plates.py"""
import os, sys
import numpy as np
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import bcomp, vdp2render as V

P = open(os.path.join(ROOT, 'work', 'disc1', 'PROGRAM.BIN'), 'rb').read()
F11 = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Bold.ttf'
F9 = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri9.ttf'
F7 = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri7.ttf'
F11C = r'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri11-Condensed.ttf'   # 좁은 판(«ステージ» 40px)에서 작은 글꼴로 내려가기 전에
NANUM_XB = r'C:/claude/utils/font/nanum-gothic/NanumGothicExtraBold.ttf'


def big_mask(text, size):
    """나눔고딕 ExtraBold 를 4배로 그려 줄이고 문턱 0.5 → 굵고 또렷한 큰 글자(스테이지 큰 글자용)"""
    F = ImageFont.truetype(NANUM_XB, size * 4)
    im = Image.new('L', (len(text) * size * 5 + 40, size * 6), 0); ImageDraw.Draw(im).text((8, 8), text, font=F, fill=255)
    a = np.array(im, np.float32) / 255
    ys, xs = np.where(a > 0.1); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    H = -(-a.shape[0] // 4) * 4; W = -(-a.shape[1] // 4) * 4
    a = np.pad(a, ((0, H - a.shape[0]), (0, W - a.shape[1]))).reshape(H // 4, 4, W // 4, 4).mean((1, 3))
    return a >= 0.5

JOBS = [  # 스샷 4 (BOMBER STADIUM ボバり方)
    (0x48C30C, 56, 24, 'ボバり方', '게임방식', 0x2380, 's4'),
    (0x48C4CC, 56, 16, 'ルール', '규칙', 0x23a0, 's4'),
    (0x48C624, 56, 16, 'ボンバー', '봄버', 0x23a0, 's4'),
    (0x48C780, 56, 16, 'チーム', '팀', 0x23a0, 's4'),
    (0x48D2E8, 56, 16, 'ボバる', '시작', 0x2370, 's4'),
    (0x48D038, 56, 16, 'ステージ', '스테이지', 0x23a0, 's4'),
    (0x48E5CC, 56, 24, 'ステージ', '스테이지', 0x2380, 's4'),
    (0x48E72C, 56, 24, 'ノーマル', '노멀', 0x2380, 's4'),
    (0x48E8A8, 56, 24, 'ワイド', '와이드', 0x2380, 's4'),
    (0x48EB64, 56, 24, 'モード', '모드', 0x2390, 's4'),
    (0x48EC9C, 56, 24, 'シングル', '싱글', 0x2390, 's4'),
    (0x48EE40, 56, 24, 'タッグ', '태그', 0x2390, 's4'),
    (0x48EA08, 56, 24, '人数', '인원', 0x23a0, 's4'),
    # 스샷 5 (ルール)
    (0x48EFB4, 56, 24, 'ルール', '규칙', 0x2380, 's5'),
    (0x48F11C, 72, 24, 'COMレベル', 'COM레벨', 0x2390, 's5'),
    (0x4A95BC, 96, 16, 'バトル回数', '배틀 횟수', 0x23c0, 's5'),
    (0x4A9A5C, 96, 16, 'シャッフル', '셔플', 0x23c0, 's5'),
    (0x4A9C8C, 96, 16, 'サドンデス', '서든데스', 0x23c0, 's5'),
    (0x4A9EC4, 96, 16, 'デビル', '데빌', 0x23c0, 's5'),
    (0x4AA0D0, 96, 16, 'みそボン', '미소봄', 0x23c0, 's5'),
    (0x4AA2F0, 96, 16, 'ボンバーキャッチャー', '봄버캐처', 0x23c0, 's5'),
    # 스샷 6 (ボンバー)
    (0x48F5A8, 96, 24, '出場ボンバー', '출전 봄버', 0x2380, 's6'),
    (0x4AEF58, 80, 24, '白ボンバーマン', '흰 봄버맨', 0x2370, 's6'),
    # 같은 메뉴 묶음 — 하스피 실기 스샷(2026-11-22)에 «バトル決め»가 남아서 왼쪽 단추 줄·저장·결과 단추까지(색 뱅크는 추정)
    (0x48C894, 56, 16, '記録', '기록', 0x23a0, 's4'),
    (0x48C9EC, 56, 16, 'バトル決め', '배틀설정', 0x23a0, 's4'),
    (0x48CB90, 56, 16, '成績', '성적', 0x23a0, 's4'),
    (0x48CCE8, 56, 16, '残りバトル', '남은배틀', 0x23a0, 's4'),
    (0x48CE84, 56, 24, '同じステージ', '같은판', 0x2380, 's4'),
    (0x48D194, 56, 16, '賞状', '상장', 0x23a0, 's4'),
    (0x48D420, 56, 16, '終了', '종료', 0x2370, 's4'),
    (0x48D7E8, 120, 24, 'どっちでボバる？', '어느 쪽으로 할까?', 0x2380, 's3'),
    (0x48DB3C, 72, 24, 'マッチプレー', '매치플레이', 0x2390, 's3'),
    (0x48DD0C, 72, 24, 'Bリーグ', 'B리그', 0x23a0, 's3'),
    (0x48DEBC, 88, 24, '新しくボバる', '새로 시작', 0x2380, 's3'),
    (0x48E15C, 160, 24, 'セーブしたところからボバる', '저장한 곳부터 시작', 0x2380, 's3'),
    (0x4B9180, 104, 32, 'けってい/キャンセル', '결정/취소', 0x2360, 's4'),
]
JOBS += [  # 스샷 8·12~18 스테이지 큰 글자(투명 바탕·세로 그라데이션) — 공용 구역(LowRAM 0x200000 = P 0x8000)
    (0x037490, 64, 16, 'ステージ', '스테이지', 0x6350, 's12'),
    (0x0375A4, 64, 16, 'スタート', '스타트', 0x6350, 's12'),
    (0x03779C, 56, 16, 'ポーズ', '일시정지', 0x6F50, 's14'),
    (0x037B1C, 40, 16, 'ボス', '보스', 0x6F20, 's15'),
    (0x03768C, 64, 16, 'クリアー', '클리어', 0x6350, 's17'),
    (0x0378D0, 112, 16, 'タイムアップ！', '타임 업!', 0x6350, 's17'),
    (0x035D04, 128, 16, 'ヒゲヒゲワールド', '히게히게 월드', 0x6F20, 's18'),
    (0x035F54, 128, 16, 'マゲマゲワールド', '마게마게 월드', 0x6F20, 's18'),
    (0x036164, 128, 16, 'ガンマンワールド', '건맨 월드', 0x6F20, 's18'),
    (0x0363BC, 128, 16, 'ティラノワールド', '티라노 월드', 0x6F20, 's18'),
    (0x0365DC, 128, 16, 'ムジョーワールド', '무조 월드', 0x6F20, 's18'),
    (0x03680C, 128, 16, 'キャッスルジョー', '캐슬 조', 0x6350, 's16'),
    (0x036A3C, 96, 16, 'コウガイガー', '코가이가', 0x6350, 's16'),
    (0x036BC8, 80, 16, 'ロディオン', '로디온', 0x6350, 's16'),
    (0x036D70, 112, 16, 'エッグバードン', '에그바돈', 0x6350, 's16'),
    (0x036FB8, 64, 16, '伝説魔', '전설마', 0x6350, 's16'),
    (0x0370FC, 24, 16, '神', '신', 0x6350, 's16'),
    (0x037188, 64, 16, 'ムジョー', '무조', 0x6350, 's16'),
    (0x037294, 104, 16, 'Dr.メカード', 'Dr.메카드', 0x6350, 's16'),
    # 스샷 8 스테이지 이름판(메뉴 묶음) — 같은 꼴 9개 전부
    (0x497224, 64, 16, 'オウジャ', '왕좌로', 0x11C0, 's8'),
    (0x4973BC, 64, 16, 'ヘノミチ', '가는 길', 0x11C0, 's8'),
    (0x497540, 128, 16, 'ファイアーゴール', '파이어 골', 0x11C0, 's8'),
    (0x4977F4, 128, 16, 'ミツリンフカク', '밀림 깊숙이', 0x11C0, 's8'),
    (0x497AAC, 128, 16, 'デザートハザード', '데저트 해저드', 0x11C0, 's8'),
    (0x497D5C, 128, 16, 'ソラノカナタ', '하늘 저편', 0x11C0, 's8'),
    (0x497FE8, 128, 16, 'ホップステップ', '홉 스텝', 0x11C0, 's8'),
    (0x4982A4, 128, 16, 'ニンジャハウス', '닌자 하우스', 0x11C0, 's8'),
    (0x498568, 128, 16, 'キカイデゴーゴー', '기계로 고고', 0x11C0, 's8'),
    (0x498800, 128, 16, 'ホノオノセンシ', '불꽃의 전사', 0x11C0, 's8'),
    # 스샷 10·11 마스터 모드(흰 글자, 투명 바탕)
    (0x52B0E8, 40, 16, '時間', '시간', 0x0390, 's11'),
    (0x52B1B4, 24, 16, '点', '점', 0x0390, 's11'),
    (0x52B23C, 48, 16, '階最高', '층최고', 0x0390, 's11'),
    (0x52B33C, 40, 16, '得点', '득점', 0x0390, 's11'),
    (0x52B41C, 88, 16, '挑戦者得点', '도전자 득점', 0x0390, 's11'),
    # 스샷 2 옵션·제목(제목 묶음 0B0540)
    (0x0BB1F4, 56, 16, 'ボムセット', '폭탄놓기', 0x0200, 's2'),
    (0x0BB320, 56, 16, 'ラインボム', '라인봄', 0x0200, 's2'),
    (0x0BB440, 48, 16, 'リモコン', '리모컨', 0x0200, 's2'),
    (0x0BB530, 80, 16, 'パワーグローブ', '파워글러브', 0x0200, 's2'),
    (0x0BB6C0, 80, 16, 'キックストップ', '킥스톱', 0x0200, 's2'),
    (0x0BB870, 32, 16, 'ティラ', '티라', 0x0200, 's2'),
    (0x0BB904, 64, 16, 'アビリティー', '어빌리티', 0x0200, 's2'),
    (0x0BBBFC, 56, 16, 'ゲットオフ', '내리기', 0x0200, 's2'),
    (0x0BAFB4, 56, 16, 'モード', '모드', 0x0200, 's2'),
    (0x0BA12C, 40, 16, 'ステージ', '스테이지', 0x0200, 's2'),
    (0x0BA1F0, 32, 16, 'ボス', '보스', 0x0200, 's2'),
    (0x0BA284, 88, 16, 'デタガアリマセン', '데이터 없음', 0x0200, 's2'),
    (0x0BA448, 96, 16, 'ヨウリョウガタリマセン', '용량 부족', 0x0200, 's2'),
    (0x0D38D4, 72, 16, 'コンティニュー', '컨티뉴', 0x0200, 's2'),
    (0x0D3A18, 64, 16, 'ムジョー基地', '무조 기지', 0x0200, 's2'),
    # 스샷 3
    (0x4A47CC, 56, 24, 'やめる', '그만두기', 0x2380, 's3'),
]
JOBS += [  # 저장 메뉴·대전 결과·시상·캐릭터 이름판(메뉴 묶음 뒤쪽) — 색 뱅크는 미리보기용 추정
    (0x4A4340, 56, 24, 'セーブする', '저장하기', 0x2380, 's4'),
    (0x4A44C8, 56, 24, 'ロードする', '불러오기', 0x2380, 's4'),
    (0x4A4650, 56, 24, 'もどる', '돌아가기', 0x2380, 's4'),
    (0x4A7964, 64, 16, '白ボンバーマン', '흰 봄버맨', 0x2380, 's6'),
    (0x4A7A8C, 64, 16, '黒ボンバーマン', '검은 봄버맨', 0x2380, 's6'),
    (0x4A7BB8, 64, 16, '高橋名人', '타카하시 명인', 0x2380, 's6'),
    (0x4A7CF8, 64, 16, '卍丸', '만지마루', 0x2380, 's6'),
    (0x4A7DD4, 64, 16, 'カブキ', '카부키', 0x2380, 's6'),
    (0x4A7ECC, 64, 16, 'ミロン', '미론', 0x2380, 's6'),
    (0x4A7FB0, 64, 16, '絹', '키누', 0x2380, 's6'),
    (0x4A805C, 64, 16, 'ユナ', '유나', 0x2380, 's6'),
    (0x4A8104, 64, 16, '小鉄', '코테츠', 0x2380, 's6'),
    (0x4A81F4, 64, 16, '原人', '원인', 0x2380, 's6'),
    (0x4A82B8, 64, 16, 'マントー', '만토', 0x2380, 's6'),
    (0x4A8460, 48, 16, '白', '백', 0x2380, 's6'),
    (0x4A8504, 48, 16, '赤', '적', 0x2380, 's6'),
    (0x4A85B8, 48, 16, '青', '청', 0x2380, 's6'),
    (0x4A865C, 48, 16, '黄', '황', 0x2380, 's6'),
    (0x4A8708, 48, 16, '緑', '녹', 0x2380, 's6'),
    (0x4A8828, 64, 16, 'ボンバー名', '봄버 이름', 0x2380, 's6'),
    (0x4A8970, 48, 16, 'チーム名', '팀 이름', 0x2380, 's6'),
    (0x4AF170, 80, 16, '黒ボンバーマン', '검은 봄버맨', 0x2370, 's6'),
    (0x4AF364, 80, 16, '高橋名人', '타카하시 명인', 0x2370, 's6'),
    (0x4AF530, 80, 16, '卍丸', '만지마루', 0x2370, 's6'),
    (0x4AF680, 80, 16, 'カブキ', '카부키', 0x2370, 's6'),
    (0x4AF7E4, 80, 16, 'ミロン', '미론', 0x2370, 's6'),
    (0x4AF944, 80, 16, '絹', '키누', 0x2370, 's6'),
    (0x4AFA50, 80, 16, 'ユナ', '유나', 0x2370, 's6'),
    (0x4AFB48, 80, 16, '小鉄', '코테츠', 0x2370, 's6'),
    (0x4AFCB4, 80, 16, '原人', '원인', 0x2370, 's6'),
    (0x4AFDF0, 80, 16, 'マントー', '만토', 0x2370, 's6'),
    (0x4AFF44, 80, 16, 'ハニー', '허니', 0x2370, 's6'),
    (0x4B0CCC, 72, 32, '賞状', '상장', 0x2380, 's4'),
    (0x4B0F5C, 48, 16, '優勝', '우승', 0x2380, 's4'),
    (0x4B1124, 64, 16, '準優勝', '준우승', 0x2380, 's4'),
    (0x4B1304, 104, 16, '最優秀選手', '최우수 선수', 0x2380, 's4'),
    (0x4B164C, 112, 16, 'Bポイント王', 'B포인트왕', 0x2380, 's4'),
    (0x4B1884, 80, 16, 'みそボン王', '미소봄왕', 0x2380, 's4'),
    (0x4B1AA0, 40, 16, '勝', '승', 0x2380, 's4'),
    (0x4B1BE4, 72, 24, '第 戦', ['제', '전'], 0x2380, 's4'),
    (0x4B1D80, 88, 24, '第 試合', ['제', '경기'], 0x2380, 's4'),
    (0x4B1F74, 104, 24, '全 戦終了', ['전체', '전 종료'], 0x2380, 's4'),
    (0x4B21DC, 64, 24, '全 戦中', ['총', '전 중'], 0x2380, 's4'),
    (0x4B239C, 80, 24, '戦終了', '전 종료', 0x2380, 's4'),
    (0x4B256C, 56, 24, '自爆', '자폭', 0x2380, 's4'),
    (0x4BAFD4, 56, 24, '通信中', '통신 중', 0x2380, 's4'),
    (0x4BB77C, 56, 16, 'あなたは', '당신은', 0x2380, 's4'),
    (0x52DE7C, 128, 24, '階', '층', 0x6F10, 's10'),
    (0x01F804, 96, 40, '本体RAM', '본체RAM', 0x2100, 's1'),
    (0x01FC3C, 96, 40, 'カートリッジRAM', '카트리지RAM', 0x2100, 's1'),
    (0x4BA90C, 120, 48, '全/残り バトル', '총/남은 배틀', 0x2380, 's4'),
    (0x4A7378, 80, 16, '▶ボンバー名', '봄버 이름', 0x2380, 's6'),
    # 미추출(받은 스테이트에 없는 화면 — 하스피 실기 스샷 «バトル数·全 0試合», 2026-11-22). 색 뱅크는 미리보기용 추정
    (0x48FDAC, 56, 24, 'バトル数', '배틀 수', 0x2380, 's4'),
    (0x4903FC, 64, 24, '(全 ○)試合', ['경기'], 0x2380, 's4'),
    (0x490C8C, 72, 24, '全 戦', ['총', '전'], 0x2380, 's4'),
    (0x490120, 96, 24, '残り 試合', ['남은', '경기'], 0x2380, 's4'),
    (0x48F838, 96, 24, 'チームボンバー', '팀 봄버', 0x2380, 's4'),
    (0x48FF70, 72, 24, 'Bリーグ', 'B리그', 0x2380, 's4'),
    (0x48FA90, 112, 24, 'やっつけ / やられ', '처치 / 당함', 0x2380, 's4'),
    # 남은 그림 글자(전수 재검 2026-11-22) — 받은 스테이트에 없는 화면, 색 뱅크는 미리보기용 추정
    (0x037C0C, 112, 16, 'コンティニュー', '컨티뉴', 0x2100, 's1'),
    (0x037DC0, 48, 16, 'エンド', '종료', 0x2100, 's1'),
    (0x037EC4, 104, 16, 'セーブ・ゲーム', '게임 저장', 0x2100, 's1'),
    (0x042FF8, 72, 16, 'コノデータハシ|ヨウデキマセン', '사용할 수 없는 데이터', 0x2100, 's1'),
    (0x0432D4, 88, 16, 'データガアリマセン', '데이터가 없습니다', 0x2100, 's1'),
    (0x043498, 80, 16, 'セーブデキマス', '저장 가능', 0x2100, 's1'),
    (0x043628, 24, 16, 'セー|ブシマシタ', '저장했습니다', 0x2100, 's1'),
    (0x0437B0, 32, 16, 'ロード|シマシタ', '불러왔습니다', 0x2100, 's1'),
    (0x490538, 128, 24, 'Bリーグ残りバトル数', 'B리그 남은 배틀 수', 0x2380, 's4'),
]
# 원본이 왼쪽 정렬인 글자(옵션 항목 — 하스피 «줄맞춤 원래 이랬나»)
LEFT = {0x0BB1F4, 0x0BB320, 0x0BB440, 0x0BB530, 0x0BB6C0, 0x0BB870, 0x0BB904, 0x0BBBFC, 0x0BAFB4}
# 특수: A.C…けってい / B……キャンセル — 영문·점은 두고 가나 칸(가로 43‥95, 윗줄 4‥14 속 a·아랫줄 16‥26 속 c, 외곽선 7, 바탕 f)만
SPECIAL = {0x4B9180: [(43, 96, 4, 15, '결정', 0xA, 0x7), (43, 96, 16, 27, '취소', 0xC, 0x7)]}


def draw_special(idx, parts, dx=0):
    out = idx.copy()
    for x0, x1, y0, y1, ko, fc, oc in parts:
        out[y0:y1, x0:x1] = 0xF
        F = ImageFont.truetype(F9, 10)
        im = Image.new('L', (200, 30), 0); ImageDraw.Draw(im).text((2, 2), ko, font=F, fill=255)
        m = np.array(im) > 127; yy, xx = np.where(m); m = m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        mh, mw = m.shape; cy = y0 + (y1 - y0 - mh) // 2; cx = x0 + 2 + dx
        if cx + mw + 1 > x1 or mh + 2 > y1 - y0: return None
        M = np.zeros_like(idx, bool); M[cy:cy + mh, cx:cx + mw] = m
        reg = np.zeros_like(idx, bool); reg[y0:y1, x0:x1] = True
        out[dil8(M) & ~M & reg] = oc; out[M] = fc
    return out


DONORS = [(0x4A984C, 96, 16)]                                         # 번역 안 하지만 빈 판 만들 때 쓰는 같은 판(TIME)

# ── 묶음 정의(단색 바탕 판 — 하스피 «단색 노란 바탕인데 찌꺼기 덩어리 바탕», «글자체·색 통일 안 됨») ─────────────
# 묶음마다: 바탕 단색·글자 색 집합·안쪽 범위(행 y0‥y1, 열 x0‥(폭−xr))·속/외곽선 색. 글꼴은 묶음 전원이 들어가는 가장 큰 것 하나.
FAMILY = {}
def _fam(name, members, bgc, textc, y0, y1, x0, xr, fill, out):
    for b in members: FAMILY[b] = dict(name=name, bg=bgc, textc=set(textc), y0=y0, y1=y1, x0=x0, xr=xr, fill=fill, out=out)
_fam('노란 이름판', [0x4A7964, 0x4A7A8C, 0x4A7BB8, 0x4A7CF8, 0x4A7DD4, 0x4A7ECC, 0x4A7FB0, 0x4A805C, 0x4A8104, 0x4A81F4, 0x4A82B8],
     3, {6, 7, 9, 0xA}, 0, 13, 0, 2, 0x9, 0xA)
_fam('팀 색', [0x4A8460, 0x4A8504, 0x4A85B8, 0x4A865C, 0x4A8708], 3, {1, 6, 7, 8}, 0, 13, 0, 2, 0x1, 0x8)
_fam('시상', [0x4B0F5C, 0x4B1124, 0x4B1304, 0x4B164C, 0x4B1884], 5, {2, 3, 4, 6, 7, 8}, 0, 15, 0, None, 0x8, 0x2)   # 위아래 테두리 없음 — 0‥15줄 전체
_fam('이름 칸', [0x4A8828], 0xC, {4, 6, 8, 9}, 1, 13, 2, 4, 0x9, 0x8)   # 봄버 이름 = 정상(그대로)
_fam('이름 칸', [0x4A8970], 0xC, {4, 6, 8, 9}, 1, 13, 2, 2, 0x9, 0x8)   # 팀 이름만: 名 끝 획이 오른쪽 4열 안에 있어 찌꺼기(하스피) — 테두리 2열 앞까지
_fam('이름 칸', [0x4A7378], 0xC, {4, 6, 8, 9}, 1, 13, 18, 4, 0x9, 0x8)   # 왼쪽 16px 화살표 + ボンバー名 판(4A8828 과 같은 판)
_fam('하늘 이름판', [0x4AF170, 0x4AF364, 0x4AF530, 0x4AF680, 0x4AF7E4, 0x4AF944, 0x4AFA50, 0x4AFB48, 0x4AFCB4, 0x4AFDF0, 0x4AFF44],
     1, {9, 0xA, 0xE, 0xF}, 2, 15, 2, 2, 0xA, 0xF)
_fam('하늘 이름판', [0x4AEF58], 1, {8, 9, 0xA, 0xE, 0xF}, 2, 15, 2, 2, 0xA, 0xF)   # 白ボンバーマン(80×24, 아래 6줄 빈칸) — 혼자 굵은 글꼴이었음(하스피 «다른 것들하고 맞춰»)
_fam('승', [0x4B1AA0], 5, {3, 4, 0xB, 0xC, 0xD, 0xE}, 0, 15, 0, 0, 0xB, 0xC)
_fam('통신 중', [0x4BAFD4], 5, {2, 4, 0xF}, 1, 16, 1, 2, 0xF, 0x2)
_fam('상장', [0x4B0CCC], 0, {1, 9, 0xA, 0xC}, 0, 31, 0, 0, 0x1, 0xC)
FAMILY[0x4A8970] = dict(FAMILY[0x4A8970], head=('팀', 0x1))           # 원본 チーム = 하늘색(1)·名 = 흰색(9) — 하스피 «팀은 파란색»
FAM_FONT = {}                                                        # 묶음 이름 → (글꼴, 크기) — main 에서 정함
FAM_FONTS = {'상장': [('big', z) for z in (28, 27, 26, 25, 24, 22, 20)]}   # 큰 판은 큰 글꼴 후보
SLOT_FONT = [(F11, 12)]                                              # 녹색 진행 판(第○戦 등) 묶음 글꼴 — 12px 로 통일


def fam_inner(idx, f):
    h, w = idx.shape
    xr = f['xr']
    if xr is None:                                                   # 시상 판: 오른쪽은 투명(0) 앞까지, 경사 테두리 2열 빼고
        nz = np.where(idx[7] != 0)[0]; x1 = nz[-1]                   # 오른쪽 투명(0) 앞까지 — 원래 글자 끝까지 지움
    else: x1 = w - 1 - xr
    inner = np.zeros_like(idx, bool); inner[f['y0']:f['y1'] + 1, f['x0']:x1 + 1] = True
    return inner


def fam_blank(idx, f):
    """빈 판: 안쪽의 글자 색 칸(+1px)을 바탕 단색으로"""
    inner = fam_inner(idx, f)
    core = inner & np.isin(idx, list(f['textc']))
    out = idx.copy(); out[dil8(core) & inner] = f['bg']
    return out


def fam_draw(idx, ko, f, font, dx=0, ring8=True):
    h, w = idx.shape
    inner = fam_inner(idx, f)
    core = inner & np.isin(idx, list(f['textc']))
    text = dil8(core) & inner
    out = idx.copy(); out[text] = f['bg']                            # 단색 바탕으로 지움
    fp, fs = font
    if fp == 'big':
        m = big_mask(ko, fs)
    else:
        im = Image.new('L', (w * 3, 40), 0); ImageDraw.Draw(im).text((2, 2), ko, font=ImageFont.truetype(fp, fs), fill=255)
        m = np.array(im) > 127; yy, xx = np.where(m); m = m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
    mh, mw = m.shape
    iy = np.where(inner.any(1))[0]; ix = np.where(inner.any(0))[0]
    cy = (iy[0] + iy[-1] + 1) // 2 - mh // 2; cx = (ix[0] + ix[-1] + 1) // 2 - mw // 2 + dx
    if cx < ix[0] + 1 or cx + mw > ix[-1] or cy < iy[0] or cy + mh > iy[-1] + 1: return None
    M = np.zeros_like(idx, bool); M[cy:cy + mh, cx:cx + mw] = m
    out[(dil8(M) if ring8 else dil4(M)) & ~M & inner] = f['out']; out[M] = f['fill']
    if f.get('head'):                                                # 앞 낱말만 다른 색(チーム名: チーム 하늘색 1, 名 흰색 9)
        word, c = f['head']
        if fp == 'big': wf = big_mask(word, fs).shape[1]
        else:
            im2 = Image.new('L', (w * 3, 40), 0); ImageDraw.Draw(im2).text((2, 2), word, font=ImageFont.truetype(fp, fs), fill=255)
            xx2 = np.where((np.array(im2) > 127).any(0))[0]; wf = xx2[-1] - xx2[0] + 1
        cols = np.zeros_like(M); cols[:, :cx + wf] = True
        out[M & cols] = c
    assert ((out != idx) & ~inner).sum() == 0
    return out


def fam_font(members):
    """묶음 전원이 들어가는 가장 큰 글꼴"""
    name = FAMILY[members[0][0]]['name']
    for font in FAM_FONTS.get(name, []) + [(F11, 12), (F11C, 12), (F9, 10), (F7, 8)]:
        if all(fam_draw(o, ko, FAMILY[b], font) is not None for b, o, ko in members): return font
    return (F7, 8)


def idx_of(data, w, h):
    a = np.frombuffer(data, np.uint8)
    return np.stack([a >> 4, a & 15], 1).ravel().reshape(h, w).astype(int)


def pack(idx):
    f = idx.ravel(); return bytes(((f[0::2] << 4) | f[1::2]).astype(np.uint8))


def dil8(m):
    p = np.pad(m, 1); o = np.zeros_like(m)
    for dy in range(3):
        for dx in range(3): o |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
    return o


def dil4(m):
    p = np.pad(m, 1); return m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


TEXTC = {0x2, 0x8, 0x9, 0xA, 0xB, 0xD}                                # 원본 글자판의 글자 색(속 a·외곽선 2/d·음영 8/9/b) — 판마다 다르면 JOBS 뒤 TEXTC_OF 로
TEXTC_OF = {0x4AEF58: {0xA, 0x8, 0x9, 0xF, 0xE}}
PAIRS = {0x497224: (0x4973BC, '왕좌로 가는 길')}                         # 이어 붙는 판(왼쪽 → 오른쪽): 한 번에 그려 폭대로 자름([[feedback_render_joined_words_once]])
NAMEPLATES = [0x497224, 0x4973BC, 0x497540, 0x4977F4, 0x497AAC, 0x497D5C, 0x497FE8, 0x4982A4, 0x498568, 0x498800]
TEAM_TC = frozenset({1, 7, 8})                                       # 팀 색 판(白赤青黄緑 48×16): 바탕 3·글자 속 1·외곽선 8/7, 아래 2줄·오른쪽 2열이 테두리
for _b in (0x4A8460, 0x4A8504, 0x4A85B8, 0x4A865C, 0x4A8708): TEXTC_OF[_b] = TEAM_TC
NAMEPLATE_TC = frozenset(set(range(16)) - {0, 3, 4})
for _b in NAMEPLATES: TEXTC_OF[_b] = NAMEPLATE_TC          # 스테이지 이름판: 위장 무늬(3·4) 위 글자·그림자                      # 白ボンバーマン: 외곽선 f·음영 e


def analyse(idx, textc=None):
    h, w = idx.shape
    if textc == TEAM_TC:
        inner = np.zeros_like(idx, bool); inner[0:h - 2, 0:w - 2] = True
        core = inner & np.isin(idx, list(TEAM_TC))
        return -1, h - 2, {3}, inner, dil8(core) & inner, core
    full = [y for y in range(h) if (idx[y] != 0).sum() >= w - 6]
    rows = [y for y in full if Counter(int(v) for v in idx[y] if v).most_common(1)[0][1] >= w - 8]   # 판 위 테두리 = 거의 한 색으로 찬 줄
    if rows: rows = [rows[0], full[-1]]
    elif len(full) >= h * 0.6:                                       # 테두리 없이 무늬로 꽉 찬 판(스테이지 이름판) = 폭·높이 전체가 안쪽
        inner = np.zeros_like(idx, bool); inner[full[0]:full[-1] + 1, :] = True
        bg = {3, 4} if textc == NAMEPLATE_TC else set(int(v) for v in idx[full[0]]) | set(int(v) for v in idx[full[-1]])   # 이름판 바탕 = 위장 무늬 3·4 만(맨 아래 줄 그림자 2 는 글자)
        tc = (textc or TEXTC) - bg; core = inner & np.isin(idx, list(tc))
        if core.any():
            return full[0] - 1, full[-1] + 1, bg, inner, dil8(core) & inner, core
        inner = np.ones_like(idx, bool); core = idx != 0             # 폭 끝까지 찬 흰 글자(階最高) = 투명 바탕
        return 0, h, {0}, inner, dil8(core) & inner, core
    if rows and rows[0] + 2 >= h: rows = []                          # 맨 아래 줄만 꽉 찬 경우는 판 아님
    if not rows or (idx[rows[0] + 1] == 0).sum() > w // 3:          # 판 없이 투명 바탕(ボバる): 0 = 바탕
        inner = np.ones_like(idx, bool); core = idx != 0
        return 0, h, {0}, inner, dil8(core) & inner, core
    y0, y1 = rows[0], rows[-1]
    x0 = next(x for x in range(w) if idx[y0 + 2, x] != 0)
    x1 = max(x for x in range(w) if idx[y0 + 2, x] != 0)
    bg = set(int(v) for v in idx[y0 + 1, x0 + 1:x1])                 # 판 안쪽 첫 줄 = 바탕
    bottom = (idx[y1] == idx[y0]).all()                              # 아래 테두리 있음(회색 판은 없음 — 아래가 다른 스프라이트)
    inner = np.zeros_like(idx, bool); inner[y0 + 1:(y1 - 1 if bottom else y1 + 1), x0 + 1:x1] = True
    tc = (textc or TEXTC) - bg
    core = inner & np.isin(idx, list(tc))
    if not core.any():                                               # 판으로 봤는데 글자가 없으면 투명 바탕 글자(階最高처럼 폭 끝까지 찬 흰 글자)
        inner = np.ones_like(idx, bool); core = idx != 0
        return 0, h, {0}, inner, dil8(core) & inner, core
    text = dil8(core) & inner                                        # 빗금 판의 바깥 테두리(7)까지
    return y0, y1, bg, inner, text, core


SHARED = {}                                                          # 같은 판 묶음의 빈 판(칸마다 글자 아닌 판들의 최빈값)


def shared_plate(key, members):
    if key in SHARED: return SHARED[key]
    stack = []; masks = []
    for idx in members:
        _, _, _, inner, text, _ = analyse(idx); stack.append(idx); masks.append(text)
    A = np.stack(stack); T = np.stack(masks); h, w = A.shape[1:]
    plate = A[0].copy(); hole = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            c = Counter(int(A[k, y, x]) for k in range(len(A)) if not T[k, y, x])
            if c: plate[y, x] = c.most_common(1)[0][0]
            else: hole[y, x] = True
    SHARED[key] = (plate, hole); return SHARED[key]


def fill_bg(idx, text, inner):
    """글자 칸 메우기 — 단색 판(주기 1 어긋남 ≤ 6%)은 줄마다 바탕 최빈색, 빗금 판은 가로 주기 복사"""
    out = idx.copy(); h, w = idx.shape
    def rate(p):
        ok = bad = 0
        for y in range(h):
            a = idx[y, :w - p]; b = idx[y, p:]
            m = inner[y, :w - p] & inner[y, p:] & ~text[y, :w - p] & ~text[y, p:]
            m[:4] = False; m[-4:] = False                            # 판 좌우 끝(밝은 줄·그림자)은 판정에서 뺌
            ok += int((a[m] == b[m]).sum()); bad += int((a[m] != b[m]).sum())
        return bad / max(1, ok + bad)
    if rate(1) <= 0.06:
        rowc = {}
        for y in range(h):
            m = inner[y] & ~text[y]
            if m.any(): rowc[y] = Counter(int(v) for v in idx[y][m]).most_common(1)[0][0]
        for y in range(h):
            if not text[y].any(): continue
            c = rowc.get(y) if y in rowc else rowc[min(rowc, key=lambda r: abs(r - y))]
            out[y][text[y]] = c
        return out, 1
    p = min(range(2, 17), key=rate)
    for y in range(h):
        for x in range(w):
            if not text[y, x]: continue
            for k in range(1, 40):
                hit = None
                for xx in (x - k * p, x + k * p):
                    if 0 <= xx < w and inner[y, xx] and not text[y, xx]: hit = idx[y, xx]; break
                if hit is not None: out[y, x] = hit; break
    return out, p


def draw(idx, ko, dx, dy, use_diag=True, plate=None, textc=None, fskip=0, premask=None, left=False):
    h, w = idx.shape
    y0, y1, bg, inner, text, core = analyse(idx, textc)
    ys, xs = np.where(core)
    th = ys.max() - ys.min() + 1
    edge = core & dil4(~core & inner)                                # 바탕과 닿은 글자 칸 = 외곽선
    mid = core & ~edge                                               # 안쪽 = 속
    ocnt = Counter(int(v) for v in idx[edge]); icnt = Counter(int(v) for v in idx[mid])
    outc = ocnt.most_common(1)[0][0] if ocnt else Counter(int(v) for v in idx[core]).most_common(1)[0][0]
    fillc = next((c for c, _ in icnt.most_common() if c != outc), None)
    if fillc is None:                                                # 획이 가늘어 안쪽이 없으면 외곽선 아닌 색 중 가장 많은 것
        fillc = next((c for c, _ in Counter(int(v) for v in idx[core]).most_common() if c != outc), outc)
    if textc == NAMEPLATE_TC:                                        # 이름판: 같은 줄 짝수 칸 거리의 가장 가까운 바탕 칸(2px 결 유지), 없으면 위·아래 줄
        base = idx.copy(); per = 2
        for y in range(h):
            for x in range(w):
                if not text[y, x]: continue
                hit = None
                for d in range(2, w, 2):
                    for xx in (x - d, x + d):
                        if 0 <= xx < w and not text[y, xx]: hit = idx[y, xx]; break
                    if hit is not None: break
                if hit is None:
                    for d in range(1, h):
                        for yy in (y - d, y + d):
                            if 0 <= yy < h and not text[yy, x]: hit = idx[yy, x]; break
                        if hit is not None: break
                base[y, x] = hit if hit is not None else 3
    elif plate is not None:                                          # 같은 판 묶음 → 빈 판에서 메우고, 모든 판이 글자인 칸만 무늬 주기로
        pl, hole = plate
        base = np.where(text, pl, idx)
        if (hole & text).any():
            b2, per = fill_bg(base, hole & text, inner); base = b2
        else: per = 0
    else:
        base, per = fill_bg(idx, text, inner)
    iy = np.where(inner.any(1))[0]
    fonts = ([('big', z) for z in (16, 15, 14, 13)] if bg == {0} and th >= 15 else []) + ([(F11, 12), (F11C, 12)] if th >= 12 else []) + [(F9, 10), (F7, 8)]
    for fp, fs in fonts[fskip:]:                                     # 판에 들어가는 가장 큰 글꼴(자리 넘치면 fskip 으로 한 단계씩 작게)(큰 투명 글자는 나눔고딕 ExtraBold, 원본 높이 −2 까지)
        if fp == 'big':
            m = big_mask(''.join(ko) if isinstance(ko, (list, tuple)) else ko, fs)
        else:
            im = Image.new('L', (w * 3, 40), 0); ImageDraw.Draw(im).text((2, 2), ''.join(ko) if isinstance(ko, (list, tuple)) else ko, font=ImageFont.truetype(fp, fs), fill=255)
            m = np.array(im) > 127
            yy, xx = np.where(m); m = m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        mh, mw = m.shape
        if mw + 2 <= w - 4 and mh + 2 <= iy[-1] - iy[0] + 1 and (fp != 'big' or mh <= th - 2): break
    cy = (ys.min() + ys.max() + 1) // 2 - mh // 2 + dy; cx = (w - mw) // 2 + dx
    if left: cx = int(xs.min()) + 1 + max(0, dx)                      # 원본 글자 왼쪽 끝(외곽선 포함)에 맞춤
    if isinstance(ko, (list, tuple)) and premask is None:            # 숫자 칸이 가운데 있는 판(第 ○ 戦): 원래 글자 덩어리 열 빈틈으로 나눠 조각마다
        cols = np.where(core.any(0))[0]
        gaps = sorted(((cols[i + 1] - cols[i], i) for i in range(len(cols) - 1)), reverse=True)[:len(ko) - 1]
        cut = sorted(i for _, i in gaps); spans = []; a = 0
        for i in cut: spans.append((cols[a], cols[i])); a = i + 1
        spans.append((cols[a], cols[-1]))
        M = None
        for fp, fs in SLOT_FONT or [(F11, 12), (F11C, 12), (F9, 10), (F7, 8)]:   # 한 판의 조각은 같은 글꼴 하나(하스피 «총전중 쓰레기»)
            Mt = np.zeros_like(idx, bool); ok = True
            for (x0s, x1s), part in zip(spans, ko):
                im = Image.new('L', (w * 3, 40), 0); ImageDraw.Draw(im).text((2, 2), part, font=ImageFont.truetype(fp, fs), fill=255)
                m = np.array(im) > 127; yy, xx = np.where(m); m = m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
                mh, mw = m.shape
                cx = (x0s + x1s + 1) // 2 - mw // 2 + dx; cy = (ys[0] + ys[-1] + 1) // 2 - mh // 2 + dy
                if x1s >= w - 2: cx = min(cx, w - 4 - mw)                # 오른쪽 끝까지 열린 판(全 戦中): 원문처럼 끝에 붙임, 왼쪽(숫자 빈칸)으로 늘림
                if not (cx >= 1 and cx + mw <= w - 1 and cy >= iy[0] and cy + mh <= iy[-1] + 1 and cx >= x0s - 12 and mw <= (x1s - x0s + 1) + 12):
                    ok = False; break
                Mt[cy:cy + mh, cx:cx + mw] |= m
            if ok: M = Mt; break
        if M is None: return None
        premask = M
    if textc == NAMEPLATE_TC:                                        # 스테이지 이름판: 밝은 단색(하스피 «그라데이션 넣지 말고 단색으로 밝은색») — 속 8(크림)·외곽선 1
        fillc, outc = 0x8, 0x1
    if premask is not None:                                          # 이어 붙는 두 판: 한 번에 그린 덩어리를 잘라 받은 것
        M = premask
    else:
        if cx < (1 if left else 2) or cx + mw > w - (1 if left else 2) or cy < iy[0] + 1 or cy + mh > iy[-1]: return None
        M = np.zeros_like(idx, bool); M[cy:cy + mh, cx:cx + mw] = m
    resid = core & (base == idx) & ~dil8(dil8(M))                      # 원래 글자 칸이 그대로 남은 찌꺼기(새 글자 2px 밖) → 그 줄 바탕 최빈색 / 투명
    for y, x in zip(*np.where(resid)):
        if bg == {0}: base[y, x] = 0; continue
        c = Counter(int(v) for v in base[y][inner[y] & ~text[y]])
        base[y, x] = c.most_common(1)[0][0] if c else min(bg)
    out = base.copy()
    ring = (dil8(M) if use_diag else dil4(M)) & ~M
    out[ring & inner] = outc; out[M] = fillc
    if bg == {0}:                                                    # 투명 바탕 큰 글자: 원본 줄별 속 색(세로 그라데이션)을 새 글자 높이에 맞춰
        oy = np.where(core.any(1))[0]; o0, o1 = oy[0], oy[-1]
        rowc = {}
        for y in range(o0, o1 + 1):
            c = Counter(int(v) for v in idx[y][core[y] & (idx[y] != outc)])
            if c: rowc[y] = c.most_common(1)[0][0]
        if len(set(rowc.values())) > 1:
            gy = np.where(M.any(1))[0]; g0, g1 = gy[0], gy[-1]               # 실제 새 글자 위·아래(이어 그린 판도 맞게)
            for y in range(g0, g1 + 1):
                t = (y - g0) / max(1, g1 - g0); src = round(o0 + t * (o1 - o0))
                c = rowc.get(src, rowc[min(rowc, key=lambda r: abs(r - src))])
                out[y][M[y]] = c
    assert ((out != idx) & ~inner).sum() == 0
    return out, (fillc, outc, per, th)


def _pair_preview(rows, orig, new, col, st, h):
    _, _, cram = V.load(st); cram = np.asarray(cram).astype(int)
    e = lambda ix: cram[((col & 0x7F0) + ix) & 0x7FF]
    rgb = lambda ix: np.stack([(e(ix) & 31) << 3, (e(ix) >> 5 & 31) << 3, (e(ix) >> 10 & 31) << 3], -1).astype(np.uint8)
    rows[-1] = (rows[-1][0], rows[-1][1], np.concatenate([rgb(orig), np.full((h, 4, 3), 90, np.uint8), rgb(new)], 1))



def _glyph(t, fp=None, fs=12):
    im = Image.new('L', (200, 40), 0); ImageDraw.Draw(im).text((2, 2), t, font=ImageFont.truetype(fp or F11, fs), fill=255)
    m = np.array(im) > 127; yy, xx = np.where(m); return m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]


def battle_rows(o):
    """全 ○ バトル / 残り ○ バトル 두 줄 판(4BA90C 120×48): 줄마다 바탕 6 으로 지우고 왼쪽 흰 글자(9·외곽선 1), 오른쪽 어두운 글자(5·7) — 숫자 칸(가운데)은 비움"""
    out = o.copy(); h, w = o.shape
    for (y0, y1), left in (((8, 25), '총'), ((27, 43), '남은')):
        reg = np.zeros_like(o, bool); reg[y0:y1 + 1, 2:w - 2] = True
        out[reg & np.isin(o, [1, 5, 7, 9])] = 6
        for (x0, x1), t, fill, oc in (((8, 26 if left == '총' else 42), left, 9, 1), ((72, 113), '배틀', 5, 7)):
            m = big_mask(t, 15); mh, mw = m.shape                    # 원본 글자 높이 16px 에 맞춤(12px 은 작음)
            cy = (y0 + y1 + 1) // 2 - mh // 2; cx = x0                 # 원문처럼 왼쪽 끝 맞춤
            M = np.zeros_like(o, bool); M[cy:cy + mh, cx:cx + mw] = m
            out[dil8(M) & ~M & reg] = oc; out[M] = fill
    return out


def master_floor(o):
    """마스터 윗줄(52DE7C 128×24)의 «階»(x 90‥104, y 7‥17, 색 1·2·d) → «층»: 그 칸만 바탕 e 로 지우고 색 1 로"""
    out = o.copy()
    reg = np.zeros_like(o, bool); reg[7:18, 89:106] = True
    out[reg & np.isin(o, [1, 2, 0xD])] = 0xE
    m = _glyph('층'); mh, mw = m.shape
    cy = 12 - mh // 2; cx = 97 - mw // 2
    M = np.zeros_like(o, bool); M[cy:cy + mh, cx:cx + mw] = m
    assert (M & ~reg).sum() == 0
    out[M] = 1
    return out


def _put(out, M, reg, fill=0x8, oc=0xA):
    out[dil8(M) & ~M & reg] = oc; out[M] = fill


def ram_honttai(o):
    """저장 장치 단추 本体RAM(01F804 96×40): 本体(x 7‥44, y 10‥30)만 «본체» — RAM 은 원본 그대로"""
    out = o.copy(); reg = np.zeros_like(o, bool); reg[10:31, 7:45] = True
    out[reg & np.isin(o, [8, 0xA, 0xC])] = 0xB
    m = big_mask('본체', 17); mh, mw = m.shape
    cy = 20 - mh // 2; cx = 26 - mw // 2
    M = np.zeros_like(o, bool); M[cy:cy + mh, cx:cx + mw] = m; assert (M & ~reg).sum() == 0
    _put(out, M, reg); return out


def ram_cart(o):
    """カートリッジRAM(01FC3C 96×40): 윗줄 カートリッジ(y 4‥17) → «카트리지», 안쪽 틀 윗선(y 4) 복원 — RAM 줄은 그대로"""
    out = o.copy(); reg = np.zeros_like(o, bool); reg[5:18, 7:90] = True
    out[reg & np.isin(o, [8, 0xA, 0xC])] = 0xB
    out[4, 6:91] = 0xC                                               # 틀 윗선(원래 c, 글자 외곽선이 덮던 자리)
    m = big_mask('카트리지', 14); mh, mw = m.shape                # 원본 カートリッジ 높이 13px
    cy = 11 - mh // 2; cx = 48 - mw // 2
    M = np.zeros_like(o, bool); M[cy:cy + mh, cx:cx + mw] = m; assert (M & ~reg).sum() == 0
    _put(out, M, reg); return out


CUSTOM = {0x4BA90C: battle_rows, 0x52DE7C: master_floor, 0x01F804: ram_honttai, 0x01FC3C: ram_cart}

JOINED = {0x4B21DC: (0x4B22F4, 24), 0x042FF8: (0x04316C, 72), 0x043628: (0x0436A0, 48), 0x0437B0: (0x043840, 40)}


def _room(b):
    n = int.from_bytes(P[b:b + 2], 'big'); e = b + 4 + bcomp.decode(P[b + 4:b + 4 + n * 2 + 300], n)[1]
    while e % 4: e += 1
    return e - (b + 4)


def _do_pair(bl, w, h, col, st, ja, rows, pair_done, groups):
    bl2, text = PAIRS[bl]
    load = lambda b: idx_of(bcomp.decode_blob(P[b:b + 4 + int.from_bytes(P[b:b + 2], 'big') * 2 + 300]), w, h)
    o1, o2 = load(bl), load(bl2)
    def room(b):
        n = int.from_bytes(P[b:b + 2], 'big'); e = b + 4 + bcomp.decode(P[b + 4:b + 4 + n * 2 + 300], n)[1]
        while e % 4: e += 1
        return e - (b + 4)
    r1, r2 = room(bl), room(bl2)
    _, _, _, inner, _, core = analyse(o1, TEXTC_OF.get(bl))
    ys = np.where(core.any(1))[0]
    best = None
    for fp, fs in ((F11, 12), (F9, 10)):
        im = Image.new('L', (w * 4, 40), 0); ImageDraw.Draw(im).text((2, 2), text, font=ImageFont.truetype(fp, fs), fill=255)
        m = np.array(im) > 127; yy, xx = np.where(m); m = m[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        mh, mw = m.shape
        if mw + 6 > 2 * w: continue
        for dx in (0, 1, -1, 2, -2, 3, -3):
            cx = (2 * w - mw) // 2 + dx; cy = (ys[0] + ys[-1] + 1) // 2 - mh // 2
            big = np.zeros((h, 2 * w), bool); big[cy:cy + mh, cx:cx + mw] = m
            outs = []
            for o, b, half in ((o1, bl, big[:, :w]), (o2, bl2, big[:, w:])):
                key = (w, h, o[1].tobytes(), o[h - 1].tobytes())
                pl = None                                            # 이름판은 공유 안 함
                t = draw(o, text, 0, 0, True, pl, TEXTC_OF.get(b), 0, half)
                outs.append(t[0] if t else None)
            if any(o is None for o in outs): continue
            s1 = min(len(bcomp.encode(pack(outs[0]), x)) for x in range(5)); s2 = min(len(bcomp.encode(pack(outs[1]), x)) for x in range(5))
            if s1 <= r1 and s2 <= r2:
                best = (outs, s1, s2, fs, dx); break
        if best: break
    assert best, ('이어 붙는 판이 자리에 안 들어감', text)
    (n1, n2), s1, s2, fs, dx = best
    open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl), 'wb').write(pack(n1))
    open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl2), 'wb').write(pack(n2))
    pair_done[bl2] = (n2, o2)
    rows.append((ja, text, None)); _pair_preview(rows, o1, n1, col, st, h)
    print('%-12s → %-8s 이어 그림 %dpx · 압축 %d/%d + %d/%d · 가로 %+d' % (ja, text, fs, s1, r1, s2, r2, dx))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    pv = os.path.join(ROOT, 'work', 'check', '그림미리보기'); os.makedirs(pv, exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'work', 'gfx'), exist_ok=True)
    rows = []; fails = []
    def load_idx(bl, w, h):
        n = int.from_bytes(P[bl:bl + 2], 'big'); return idx_of(bcomp.decode_blob(P[bl:bl + 4 + n * 2 + 300]), w, h)
    groups = {}
    for bl, w, h in [(j[0], j[1], j[2]) for j in JOBS] + DONORS:
        idx = load_idx(bl, w, h)
        if (idx != 0).sum() > idx.size // 2:
            key = (w, h, idx[1].tobytes(), idx[h - 1].tobytes()); groups.setdefault(key, []).append(idx)
    pair_done = {}
    right_of = {v[0]: k for k, v in PAIRS.items()}
    only = {int(a, 16) for a in sys.argv[1:] if not a.startswith('-')}   # 판 번호를 주면 그 판만(하스피 «전부 다 돌리는 거 아니지?»)
    for bl, w, h, ja, ko, col, st in JOBS:
        if only and bl not in only and PAIRS.get(bl, (None,))[0] not in only and JOINED.get(bl, (None,))[0] not in only: continue
        if bl in right_of:                                           # 오른쪽 판은 왼쪽 판 차례에 같이 만듦
            new, orig = pair_done[bl]
            rows.append((ja, ko, None)); _pair_preview(rows, orig, new, col, st, h); continue
        if bl in PAIRS:
            _do_pair(bl, w, h, col, st, ja, rows, pair_done, groups); continue
        if bl in CUSTOM:
            t = CUSTOM[bl](load_idx(bl, w, h))
            assert min(len(bcomp.encode(pack(t), x)) for x in range(5)) <= _room(bl), ('자리 넘침', ja)
            open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl), 'wb').write(pack(t)); print('%-12s → %s 전용 그림' % (ja, ko)); continue
        if bl in JOINED:                                             # 오른쪽 다른 그림에 이어지는 판(全 ○ 戦中 = 4B21DC 64 + 4B22F4 24): 이어 붙여 한 번에 그리고 자름
            bl2, w2 = JOINED[bl]
            o2 = idx_of(bcomp.decode_blob(P[bl2:bl2 + 3000]), w2, h)
            Jn = np.concatenate([load_idx(bl, w, h), o2], 1); got = None
            for dx in (0, 1, -1, 2, -2):
                t = draw(Jn, ko, dx, 0, True, None, None)
                if not t: continue
                n1, n2 = t[0][:, :w], t[0][:, w:]
                if all(min(len(bcomp.encode(pack(n), x)) for x in range(5)) <= _room(b) for n, b in ((n1, bl), (n2, bl2))):
                    got = (n1, n2); break
            assert got, ('이어진 판이 자리에 안 들어감', ja)
            open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl), 'wb').write(pack(got[0]))
            open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl2), 'wb').write(pack(got[1]))
            print('%-12s → %s 이어 그림(+%06X)' % (ja, ''.join(ko), bl2)); continue
        n = int.from_bytes(P[bl:bl + 2], 'big')
        orig = idx_of(bcomp.decode_blob(P[bl:bl + 4 + n * 2 + 300]), w, h)
        used = bcomp.decode(P[bl + 4:bl + 4 + n * 2 + 300], n)[1]
        end = bl + 4 + used
        while end % 4: end += 1
        room = end - (bl + 4)
        cands = []
        if bl in FAMILY:                                             # 단색 바탕 묶음: 묶음 글꼴 하나, 가운데
            f = FAMILY[bl]
            if f['name'] not in FAM_FONT:
                mem = [(j[0], load_idx(j[0], j[1], j[2]), j[4]) for j in JOBS if FAMILY.get(j[0], {}).get('name') == f['name']]
                FAM_FONT[f['name']] = fam_font(mem)
            for r8 in (True, False):
                for dx in (0, 1, -1, 2, -2):
                    t = fam_draw(orig, ko, f, FAM_FONT[f['name']], dx, r8)
                    if t is not None:
                        cands.append((min(len(bcomp.encode(pack(t), b)) for b in range(5)), not r8, abs(dx), t, (f['fill'], f['out'], 0, 0), dx, 0))
        if bl in SPECIAL:
            for dx in (0, 2, 4, 6):
                t = draw_special(orig, SPECIAL[bl], dx)
                if t is not None:
                    cands.append((min(len(bcomp.encode(pack(t), b)) for b in range(5)), False, dx, t, (0xA, 0x7, 0, 0), dx, 0))
        for diag in ((True, False) if bl not in SPECIAL and bl not in FAMILY else ()):
            for dx in (0, 1, -1, 2, -2):
                for dy in (0, -1, 1):
                    key = (w, h, orig[1].tobytes(), orig[h - 1].tobytes())
                    pl = shared_plate(key, groups[key]) if len(groups.get(key, [])) >= 2 and bl not in NAMEPLATES else None   # 이름판(불규칙 위장 무늬)은 공유 안 함
                    r = draw(orig, ko, dx, dy, diag, pl, TEXTC_OF.get(bl), left=bl in LEFT)
                    if r is None: continue
                    t, info = r
                    sz = min(len(bcomp.encode(pack(t), b)) for b in range(5))
                    cands.append((sz, not diag, abs(dx) + abs(dy), t, info, dx, dy))
        fit = [c for c in cands if c[0] <= room]
        fsk = 0
        while cands and not fit and fsk < 3 and bl not in SPECIAL and bl not in FAMILY:       # 큰 글꼴이 넘치면 한 단계 작은 글꼴로
            fsk += 1; cands = []
            for diag in (True, False):
                for dx in (0, 1, -1, 2, -2):
                    for dy in (0, -1, 1):
                        key = (w, h, orig[1].tobytes(), orig[h - 1].tobytes())
                        pl = shared_plate(key, groups[key]) if len(groups.get(key, [])) >= 2 else None
                        r = draw(orig, ko, dx, dy, diag, pl, TEXTC_OF.get(bl), fsk, left=bl in LEFT)
                        if r is None: continue
                        t, info = r
                        cands.append((min(len(bcomp.encode(pack(t), b)) for b in range(5)), not diag, abs(dx) + abs(dy), t, info, dx, dy))
            fit = [c for c in cands if c[0] <= room]
        if not cands:
            fails.append((ja, ko, '글자가 판보다 큼')); continue
        if not fit:
            fails.append((ja, ko, '압축 %d > 자리 %d' % (min(c[0] for c in cands), room))); continue
        sz, nd, _, new, info, dx, dy = min(fit, key=lambda c: (c[1], c[2], c[0]))
        open(os.path.join(ROOT, 'work', 'gfx', '%06X.bin' % bl), 'wb').write(pack(new))
        _, _, cram = V.load(st); cram = np.asarray(cram).astype(int)
        def rgb(ix):
            e = cram[((col & 0x7F0) + ix) & 0x7FF]
            img = np.stack([(e & 31) << 3, (e >> 5 & 31) << 3, (e >> 10 & 31) << 3], -1).astype(np.uint8)
            img[ix == 0] = (40, 40, 40); return img
        rows.append((ja, ko, np.concatenate([rgb(orig), np.full((h, 4, 3), 90, np.uint8), rgb(new)], 1)))
        print('%-12s → %-8s 압축 %3d / 자리 %3d · 속 %x 외곽 %x 무늬주기 %d 글자높이 %d · 가로 %+d 세로 %+d%s' %
              (ja, ko, sz, room, info[0], info[1], info[2], info[3], dx, dy, '' if not nd else ' · 대각 외곽선 없음'))
    for f in fails: print('⚠️', *f)
    rows = [r for r in rows if r[2] is not None]
    if not rows: return
    if only: return                                                  # 일부만 돌릴 땐 전체 미리보기를 덮어쓰지 않음
    W = max(r[2].shape[1] for r in rows) * 3; H = sum(r[2].shape[0] * 3 + 6 for r in rows)
    S = Image.new('RGB', (W, H), (60, 60, 60)); y = 0
    for ja, ko, im in rows:
        S.paste(Image.fromarray(im).resize((im.shape[1] * 3, im.shape[0] * 3), Image.NEAREST), (0, y)); y += im.shape[0] * 3 + 6
    S.save(os.path.join(pv, '스샷4-7_글자판_원본_한글.png'))
    print('미리보기', len(rows), '장')


if __name__ == '__main__':
    main()
