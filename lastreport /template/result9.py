#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フローチャート生成スクリプト
- figs/flow_zentai.pdf : システム全体の処理フローチャート
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

# 指揮デバイス・中継機デバイスのloop関数フローチャート（flow_siki, flow_kan）は
# 図35・36の形式に統一した result11.py で生成する（本スクリプトからは削除済み）．
