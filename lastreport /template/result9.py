#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フローチャート生成スクリプト
- figs/flow_zentai.pdf : システム全体の処理フローチャート
- figs/flow_siki.pdf   : 指揮デバイスのloop関数の処理フローチャート
- figs/flow_kan.pdf    : 中継機デバイスのloop関数の処理フローチャート
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle
from matplotlib.lines import Line2D
import os

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUTDIR, exist_ok=True)

font_candidates = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W2.ttc',
    '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf',
]
font_path = None
for fp in font_candidates:
    if os.path.exists(fp):
        font_path = fp
        break
from matplotlib.font_manager import FontProperties
jp = FontProperties(fname=font_path) if font_path else None

FS = 9


def rounded(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle='round,pad=0.02,rounding_size=0.12',
                                fc='white', ec='black', lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=FS, fontproperties=jp)


def rect(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle='square,pad=0.02', fc='white', ec='black', lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=FS, fontproperties=jp)


def diamond(ax, x, y, w, h, text):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
                         closed=True, fc='white', ec='black', lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=FS, fontproperties=jp)


def connector(ax, x, y, label='A'):
    ax.add_patch(Circle((x, y), 0.28, fc='white', ec='black', lw=1))
    ax.text(x, y, label, ha='center', va='center', fontsize=FS, fontproperties=jp)


def arrow(ax, x1, y1, x2, y2, label=None, lx=0.12, ly=0.0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label,
                fontsize=FS - 1, fontproperties=jp)


def polyline_arrow(ax, pts, label=None, lpos=None):
    for i in range(len(pts) - 2):
        ax.add_line(Line2D([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                           color='black', lw=1))
    ax.annotate('', xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle='->', lw=1))
    if label and lpos:
        ax.text(lpos[0], lpos[1], label, fontsize=FS - 1, fontproperties=jp)


def new_ax(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 10)
    ax.axis('off')
    return fig, ax


# ============================================================
# 1. システム全体の処理フローチャート（2列構成）
# ============================================================
fig, ax = new_ax(8.6, 7.2)
ax.set_ylim(0, 12)

# 左列 x=2.6
Lx = 2.6
rounded(ax, Lx, 11.2, 2.4, 0.7, '開始')
rect(ax, Lx, 9.9, 4.2, 0.8, '各デバイスの起動・\nWi-Fiネットワークへの接続')
diamond(ax, Lx, 8.3, 3.4, 1.3, '指揮デバイスの\nボタン押下？')
rect(ax, Lx, 6.7, 4.2, 0.8, "演奏開始信号'S'を中継機・\n全楽器デバイスへ送信")
rect(ax, Lx, 5.3, 4.2, 0.8, '中継機デバイス：回転開始・\nLEDマトリクスにBPM表示')
connector(ax, Lx, 3.9, 'A')
arrow(ax, Lx, 10.85, Lx, 10.3)
arrow(ax, Lx, 9.5, Lx, 8.95)
arrow(ax, Lx, 7.65, Lx, 7.1, label='yes')
# no ループ（左側に回す）
polyline_arrow(ax, [(Lx - 1.7, 8.3), (Lx - 2.3, 8.3), (Lx - 2.3, 9.2), (Lx - 0.5, 9.2), (Lx - 0.5, 8.98)])
ax.text(Lx - 2.15, 8.5, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Lx, 6.3, Lx, 5.7)
arrow(ax, Lx, 4.9, Lx, 4.18)

# 右列 x=7.2
Rx = 7.2
connector(ax, Rx, 11.2, 'A')
rect(ax, Rx, 10.1, 4.2, 0.8, '回転するレーザー光が\n楽器デバイスの受光部を通過')
rect(ax, Rx, 8.7, 4.2, 0.8, '楽器デバイス：受光間隔から\nBPMを推定し同期を補正')
diamond(ax, Rx, 7.1, 3.6, 1.3, '全楽器の同期ズレが\n閾値未満？')
rect(ax, Rx, 5.5, 3.9, 0.8, '楽曲の演奏（輪唱）')
diamond(ax, Rx, 3.9, 3.9, 1.3, '振り動作による\nBPM・音量変更？')
diamond(ax, Rx, 2.2, 3.4, 1.2, '終了ボタン\n押下？')
rect(ax, Rx, 0.9, 4.2, 0.7, "'E'送信：回転停止・消灯・演奏終了")
rounded(ax, 3.6, 0.9, 2.0, 0.6, '終了')
arrow(ax, Rx, 10.92, Rx, 10.5)
arrow(ax, Rx, 9.7, Rx, 9.1)
arrow(ax, Rx, 8.3, Rx, 7.75)
arrow(ax, Rx, 6.45, Rx, 5.9, label='yes')
# no → 同期補正へ戻る
polyline_arrow(ax, [(Rx - 1.8, 7.1), (Rx - 2.42, 7.1), (Rx - 2.42, 8.7), (Rx - 2.1, 8.7)])
ax.text(Rx - 2.38, 7.3, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Rx, 4.9, Rx, 4.55)
# yes → 'B'/'V'送信して演奏継続
polyline_arrow(ax, [(Rx + 1.95, 3.9), (Rx + 2.75, 3.9), (Rx + 2.75, 5.5), (Rx + 1.95, 5.5)])
ax.text(Rx + 2.0, 4.15, "yes（'B'・'V'送信）", fontsize=FS - 1.5, fontproperties=jp)
arrow(ax, Rx, 3.25, Rx, 2.8, label='no')
# 終了ボタン no → 演奏継続
polyline_arrow(ax, [(Rx - 1.7, 2.2), (Rx - 2.4, 2.2), (Rx - 2.4, 5.5), (Rx - 1.95, 5.5)])
ax.text(Rx - 2.3, 2.4, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Rx, 1.6, Rx, 1.25, label='yes')
arrow(ax, Rx - 2.1, 0.9, 3.6 + 1.0, 0.9)

fig.savefig(os.path.join(OUTDIR, 'flow_zentai.pdf'), bbox_inches='tight')
fig.savefig(os.path.join(OUTDIR, 'flow_zentai.png'), dpi=200, bbox_inches='tight')
print('flow_zentai saved')

# ============================================================
# 2. 指揮デバイス loop関数の処理フローチャート
# ============================================================
fig, ax = new_ax(7.6, 8.0)
ax.set_ylim(0, 13.4)
Cx = 4.6
rounded(ax, Cx, 12.9, 2.6, 0.7, 'loop() 開始')
diamond(ax, Cx, 11.5, 3.8, 1.3, 'button()：\ninput_PINの立下り？')
rect(ax, Cx, 9.9, 5.4, 0.9, "isButtonPlayingを反転し'S'（開始）\nまたは'E'（終了）を送信，300 ms待機")
diamond(ax, Cx, 8.3, 4.2, 1.3, 'pot.update()：\nSAMPLE_INTERVAL経過？')
rect(ax, Cx, 6.7, 5.4, 0.9, '可変抵抗器2系統をサンプリングし\n移動平均・段階算出（変化時にフラグ設定）')
rect(ax, Cx, 5.3, 5.4, 0.9, 'acc.update()：合成加速度を取得\n（I2C異常時はrecoverI2C()で復旧）')
diamond(ax, Cx, 3.6, 4.6, 1.4, '|差分| > accThreshold かつ\nshakeInterval経過？')
rect(ax, Cx, 1.9, 5.4, 0.9, "フラグの立っている項目について\n'B'（BPM）・'V'（音量）を送信")
rounded(ax, Cx, 0.6, 2.9, 0.7, 'loop() 先頭へ戻る')

arrow(ax, Cx, 12.55, Cx, 12.15)
arrow(ax, Cx, 10.85, Cx, 10.35, label='yes')
arrow(ax, Cx, 9.45, Cx, 8.95)
# button no → pot.update()へ
polyline_arrow(ax, [(Cx + 1.9, 11.5), (Cx + 3.3, 11.5), (Cx + 3.3, 8.3), (Cx + 2.15, 8.3)])
ax.text(Cx + 2.7, 11.7, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 7.65, Cx, 7.15, label='yes')
# pot no → acc.update()
polyline_arrow(ax, [(Cx - 2.1, 8.3), (Cx - 3.3, 8.3), (Cx - 3.3, 5.75), (Cx - 2.7, 5.75)])
ax.text(Cx - 3.15, 8.5, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 6.25, Cx, 5.75)
arrow(ax, Cx, 4.85, Cx, 4.3)
arrow(ax, Cx, 2.9, Cx, 2.35, label='yes')
# acc no → loop先頭
polyline_arrow(ax, [(Cx - 2.3, 3.6), (Cx - 3.5, 3.6), (Cx - 3.5, 0.6), (Cx - 1.45, 0.6)])
ax.text(Cx - 3.35, 3.8, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 1.45, Cx, 0.95)

fig.savefig(os.path.join(OUTDIR, 'flow_siki.pdf'), bbox_inches='tight')
fig.savefig(os.path.join(OUTDIR, 'flow_siki.png'), dpi=200, bbox_inches='tight')
print('flow_siki saved')

# ============================================================
# 3. 中継機デバイス loop関数の処理フローチャート
# ============================================================
fig, ax = new_ax(8.6, 7.0)
ax.set_ylim(0, 11.4)
Cx = 5.0
rounded(ax, Cx, 10.9, 2.6, 0.7, 'loop() 開始')
diamond(ax, Cx, 9.5, 3.6, 1.3, 'UDPパケット\n到着？')
rect(ax, Cx, 8.0, 5.0, 0.8, 'ヘッダ（1バイト目）と\nペイロード（2バイト目）を読み取り')
diamond(ax, Cx, 6.4, 3.2, 1.2, 'ヘッダ判定')
# 3分岐
rect(ax, 1.8, 4.6, 3.0, 0.9, "'S'：startRamp()\ndisplayBPM()")
diamond(ax, 5.0, 4.5, 3.0, 1.2, "'B'：演奏中？")
rect(ax, 8.2, 4.6, 2.8, 0.9, "'E'：stopRamp()\nclearDisplay()")
rect(ax, 4.0, 2.7, 2.9, 0.9, 'changeBPM()\ndisplayBPM()')
rect(ax, 6.6, 2.7, 2.0, 0.7, '無視')
rounded(ax, Cx, 1.0, 3.2, 0.7, 'loop() 先頭へ戻る')

arrow(ax, Cx, 10.55, Cx, 10.15)
arrow(ax, Cx, 8.85, Cx, 8.4, label='yes')
# no → loop先頭
polyline_arrow(ax, [(Cx + 1.8, 9.5), (9.85, 9.5), (9.85, 0.35), (Cx, 0.35), (Cx, 0.62)])
ax.text(Cx + 2.6, 9.7, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 7.6, Cx, 7.0)
# 分岐
polyline_arrow(ax, [(Cx - 1.6, 6.4), (1.8, 6.4), (1.8, 5.05)])
ax.text(2.3, 6.55, "'S'", fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 5.8, Cx, 5.1)
ax.text(Cx + 0.15, 5.45, "'B'", fontsize=FS - 1, fontproperties=jp)
polyline_arrow(ax, [(Cx + 1.6, 6.4), (8.2, 6.4), (8.2, 5.05)])
ax.text(7.4, 6.55, "'E'", fontsize=FS - 1, fontproperties=jp)
# 'B' の分岐
polyline_arrow(ax, [(4.0, 4.5), (4.0, 3.15)])
ax.text(3.5, 3.9, 'yes', fontsize=FS - 1, fontproperties=jp)
polyline_arrow(ax, [(6.5, 4.5), (6.6, 4.5), (6.6, 3.05)])
ax.text(6.75, 3.9, 'no', fontsize=FS - 1, fontproperties=jp)
# 合流
polyline_arrow(ax, [(1.8, 4.15), (1.8, 1.0), (Cx - 1.6, 1.0)])
polyline_arrow(ax, [(4.0, 2.25), (4.0, 1.35)])
polyline_arrow(ax, [(6.6, 2.35), (6.6, 1.35)])
polyline_arrow(ax, [(8.2, 4.15), (8.2, 1.0), (Cx + 1.6, 1.0)])

fig.savefig(os.path.join(OUTDIR, 'flow_kan.pdf'), bbox_inches='tight')
fig.savefig(os.path.join(OUTDIR, 'flow_kan.png'), dpi=200, bbox_inches='tight')
print('flow_kan saved')
