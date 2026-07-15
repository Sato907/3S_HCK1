#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同期開始条件（60ms/50ms）別の応答遅延・成功率の比較グラフ生成スクリプト
- データ源: 本文表「同期開始条件を60ms/50ms以下とした場合のボタン押下から
  楽曲再生開始までの応答遅延」(tab:song_start_60ms, tab:song_start_50ms)
- 左: BPM別の平均応答遅延（エラーバーは標準誤差）
- 右: BPM別の楽曲再生開始の成功率（60s以内に再生開始した試行の割合）
- 出力: figs/sync_condition_compare.pdf / .png
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
font_candidates = ['/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc',
                   '/System/Library/Fonts/ヒラギノ角ゴシック W2.ttc',
                   '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf']
font_path = next((fp for fp in font_candidates if os.path.exists(fp)), None)
jp = FontProperties(fname=font_path) if font_path else None
jp_bold = FontProperties(fname=font_path, weight='bold') if font_path else None

bpm = [60, 90, 120, 150, 180]
x = np.arange(len(bpm))

# 応答遅延（平均値・標準誤差）[ms]
mean_60 = [7816.0, 6100.0, 9360.0, 9768.0, 12226.0]
se_60 = [355.2, 399.9, 523.7, 1906.5, 2616.8]
mean_50 = [21065.0, 22417.8, 15430.0, 22872.0, 15339.2]
se_50 = [5802.5, 5013.0, 2837.3, 7890.2, 2842.5]

# 成功率 [%]（60s以内に楽曲再生が開始された試行の割合）
succ_60 = [100.0, 100.0, 100.0, 100.0, 100.0]
succ_50 = [80.0, 90.0, 100.0, 50.0, 100.0]

C60 = '#4878a8'   # 60ms条件
C50 = '#d1495b'   # 50ms条件
W = 0.36

fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0))

# ---- 左: 平均応答遅延 ----
ax = axes[0]
ax.bar(x - W / 2, np.array(mean_60) / 1000, W, yerr=np.array(se_60) / 1000,
       color=C60, edgecolor='black', linewidth=0.6,
       error_kw=dict(ecolor='black', lw=1.0, capsize=3),
       label='同期開始条件 60 ms 以下')
ax.bar(x + W / 2, np.array(mean_50) / 1000, W, yerr=np.array(se_50) / 1000,
       color=C50, edgecolor='black', linewidth=0.6,
       error_kw=dict(ecolor='black', lw=1.0, capsize=3),
       label='同期開始条件 50 ms 以下')
ax.set_xticks(x)
ax.set_xticklabels([str(b) for b in bpm])
ax.set_xlabel('BPM設定値', fontproperties=jp, fontsize=11)
ax.set_ylabel('平均応答遅延 [s]', fontproperties=jp, fontsize=11)
ax.set_title('(a) ボタン押下から楽曲再生開始までの平均応答遅延',
             fontproperties=jp, fontsize=11, pad=10)
ax.set_ylim(0, 35)
ax.yaxis.grid(True, linestyle=':', linewidth=0.6, alpha=0.6)
ax.set_axisbelow(True)
leg = ax.legend(prop=jp, fontsize=9, loc='upper left', frameon=True,
                edgecolor='#888888')
ax.text(0.98, 0.02, '注: エラーバーは標準誤差．\n50 ms条件は60 s以内に再生開始した試行のみ',
        transform=ax.transAxes, ha='right', va='bottom',
        fontproperties=jp, fontsize=8, color='#444444')

# ---- 右: 成功率 ----
ax = axes[1]
ax.bar(x - W / 2, succ_60, W, color=C60, edgecolor='black', linewidth=0.6,
       label='同期開始条件 60 ms 以下')
ax.bar(x + W / 2, succ_50, W, color=C50, edgecolor='black', linewidth=0.6,
       label='同期開始条件 50 ms 以下')
for xi, v in zip(x, succ_50):
    ax.text(xi + W / 2, v + 2, f'{v:.0f}', ha='center', va='bottom',
            fontsize=9, fontproperties=jp)
for xi, v in zip(x, succ_60):
    ax.text(xi - W / 2, v + 2, f'{v:.0f}', ha='center', va='bottom',
            fontsize=9, fontproperties=jp)
ax.set_xticks(x)
ax.set_xticklabels([str(b) for b in bpm])
ax.set_xlabel('BPM設定値', fontproperties=jp, fontsize=11)
ax.set_ylabel('成功率 [%]', fontproperties=jp, fontsize=11)
ax.set_title('(b) 60 s以内に楽曲再生が開始された試行の割合',
             fontproperties=jp, fontsize=11, pad=10)
ax.set_ylim(0, 118)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.yaxis.grid(True, linestyle=':', linewidth=0.6, alpha=0.6)
ax.set_axisbelow(True)
# 凡例は左パネルと共通のため省略（色の対応は(a)の凡例を参照）

fig.tight_layout()
fig.savefig(os.path.join(OUTDIR, 'sync_condition_compare.pdf'),
            bbox_inches='tight')
fig.savefig(os.path.join(OUTDIR, 'sync_condition_compare.png'),
            dpi=200, bbox_inches='tight')
print('saved: sync_condition_compare.pdf / .png')
