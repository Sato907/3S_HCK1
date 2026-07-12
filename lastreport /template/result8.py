#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考察（sect5）および音色再現度テストのMOS評価（sect4）用の統計処理・グラフ生成スクリプト

1. 音色再現度テスト（N=100，5段階リッカート尺度）のMOS評価
   - 中央値・最頻値・四分位数の算出とMOP判定（中央値および最頻値がともに4.0以上）
   - MOP判定線付きの中央値・最頻値棒グラフ（figs/mos_median_mode.pdf）
2. ハッカソン参加者共通アンケート（7段階評価，チーム40: n=26，全教室: n=1671）
   - 五数要約に基づく箱ひげ図（figs/hackathon_boxplot.pdf）
   - チーム40と全教室平均の比較棒グラフ（平均±SD）（figs/hackathon_compare.pdf）
   - Welchのt検定（要約統計量から算出）とCohenのd
3. ボタン押下成功率158/160の95%Wilson信頼区間
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
import os
from scipy import stats

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUTDIR, exist_ok=True)

# ---------- 日本語フォント設定（result6.py と同一） ----------
font_candidates = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W2.ttc',
    '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf',
    '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]
font_path = None
for fp in font_candidates:
    if os.path.exists(fp):
        font_path = fp
        break
if font_path:
    from matplotlib.font_manager import FontProperties
    jp_font = FontProperties(fname=font_path)
else:
    plt.rcParams['font.family'] = 'sans-serif'
    jp_font = None


def jp(ax, title, xlabel, ylabel, xticklabels=None):
    kw = {'fontproperties': jp_font} if jp_font else {}
    ax.set_title(title, fontsize=13, fontweight='bold', **kw)
    ax.set_xlabel(xlabel, fontsize=11, **kw)
    ax.set_ylabel(ylabel, fontsize=11, **kw)
    if xticklabels is not None:
        ax.set_xticklabels(xticklabels, fontsize=10, **kw)


# ============================================================
# 1. 音色再現度テストの MOS 評価（生データは result6.py と同一）
# ============================================================
data = {
    'ストリングス': [5, 5, 4, 5, 5, 5, 5, 4, 5, 5, 4, 5, 5, 4, 5, 4, 2, 4, 5, 5, 4, 5, 5, 5, 5, 5, 5, 4, 5, 2, 3, 2, 5, 4, 4, 4, 4, 5, 5, 2, 5, 5, 4, 5, 4, 5, 5, 5, 5, 4, 4, 4, 4, 4, 5, 4, 2, 4, 4, 5, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 5, 5, 4, 5, 5, 5, 4, 4, 5, 5, 3, 4, 5, 5, 5, 4, 4, 4, 3, 4, 4, 4, 4, 5, 5, 5, 4, 5, 4, 5],
    'フルート': [5, 5, 4, 5, 5, 5, 2, 2, 5, 5, 4, 4, 5, 5, 4, 5, 5, 4, 4, 4, 2, 5, 5, 5, 5, 5, 5, 2, 5, 2, 4, 4, 5, 4, 5, 5, 5, 5, 5, 2, 5, 5, 3, 5, 4, 5, 4, 5, 5, 5, 5, 2, 2, 4, 4, 5, 5, 2, 3, 4, 3, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 4, 4, 4, 5, 4, 2, 5, 4, 5, 5, 5, 4, 4, 5, 4, 5, 2, 5, 4, 4, 5, 5, 4, 5],
    'ピアノ': [3, 4, 3, 5, 5, 5, 1, 4, 5, 5, 5, 2, 4, 3, 3, 2, 2, 2, 5, 5, 4, 5, 5, 3, 5, 4, 5, 2, 5, 3, 2, 2, 5, 4, 4, 5, 5, 4, 3, 1, 4, 4, 4, 5, 5, 5, 5, 5, 4, 4, 4, 3, 4, 4, 4, 2, 2, 4, 4, 4, 4, 4, 2, 4, 5, 4, 2, 3, 4, 4, 4, 4, 4, 5, 5, 5, 4, 3, 4, 4, 3, 2, 5, 4, 5, 4, 4, 3, 3, 4, 2, 4, 1, 4, 4, 4, 4, 4, 5, 4],
    'ハイハット': [5, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 4, 5, 2, 5, 5, 4, 4, 4, 4, 3, 5, 4, 5, 5, 4, 5, 5, 5, 4, 1, 4, 5, 5, 5, 5, 4, 5, 5, 2, 5, 4, 4, 5, 5, 5, 4, 5, 5, 5, 4, 5, 4, 5, 5, 3, 2, 4, 5, 5, 4, 3, 5, 3, 5, 3, 2, 2, 5, 5, 5, 4, 4, 5, 5, 5, 5, 4, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 4, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4],
    'キックドラム': [1, 4, 4, 4, 5, 5, 3, 5, 4, 4, 5, 4, 4, 2, 3, 4, 1, 3, 3, 4, 3, 5, 3, 4, 4, 4, 5, 2, 5, 1, 3, 3, 5, 4, 4, 5, 5, 4, 4, 2, 5, 5, 4, 5, 5, 5, 5, 5, 4, 4, 4, 5, 2, 4, 5, 2, 4, 5, 2, 4, 3, 2, 4, 3, 3, 4, 2, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 2, 4, 4, 3, 4, 4, 4, 5, 4, 4, 4, 2, 4, 2, 4, 5, 4, 5, 4, 4, 4, 5, 4],
    'スネアドラム': [3, 4, 4, 5, 5, 5, 4, 5, 4, 4, 5, 4, 4, 3, 4, 4, 1, 2, 3, 4, 4, 5, 3, 4, 5, 4, 5, 5, 5, 2, 3, 3, 5, 4, 4, 4, 5, 4, 4, 4, 3, 4, 4, 5, 5, 5, 5, 5, 4, 4, 4, 3, 4, 4, 5, 3, 4, 2, 2, 4, 3, 5, 4, 4, 4, 3, 4, 2, 4, 4, 5, 3, 4, 5, 4, 5, 4, 4, 4, 5, 3, 3, 4, 4, 5, 4, 4, 4, 3, 4, 4, 4, 5, 4, 5, 5, 5, 5, 4, 5]
}
instruments = list(data.keys())

print("=" * 70)
print("1. 音色再現度テスト: MOS評価（中央値・最頻値・四分位数）")
print("=" * 70)
print(f"{'楽器':<8} | 中央値 | 最頻値 | Q1 | Q3 | IQR | MOP判定")
mos_medians, mos_modes = [], []
for inst in instruments:
    vals = np.array(data[inst])
    med = np.median(vals)
    counts = [int(np.sum(vals == k)) for k in range(1, 6)]
    max_c = max(counts)
    modes = [i + 1 for i, c in enumerate(counts) if c == max_c]  # 同数の場合は多峰
    # 順序尺度のため補間を行わない経験分布関数の逆関数で四分位数を求める
    q1 = np.percentile(vals, 25, method='inverted_cdf')
    q3 = np.percentile(vals, 75, method='inverted_cdf')
    ok = (med >= 4.0) and all(m >= 4.0 for m in modes)
    mos_medians.append(med)
    mos_modes.append(modes)
    mode_str = '・'.join(str(m) for m in modes)
    print(f"{inst:<8} | {med:>5} | {mode_str:>5} | {q1:>2} | {q3:>2} | {q3-q1:>3} | {'達成' if ok else '未達成'}")

# ---------- グラフ: MOP判定線（4.0）付きの中央値・最頻値棒グラフ ----------
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(instruments))
bar_w = 0.3
med_vals = mos_medians
# 最頻値が複数ある場合は最小値を棒の高さとし（保守的な表示），ラベルに全値を示す
mode_plot = [min(m) for m in mos_modes]
bars_med = ax.bar(x - bar_w / 2, med_vals, bar_w, color='#4575b4', edgecolor='white', linewidth=0.5)
bars_mod = ax.bar(x + bar_w / 2, mode_plot, bar_w, color='#91bfdb', edgecolor='white', linewidth=0.5)
ax.bar_label(bars_med, fmt='%.0f', padding=4, fontsize=10, fontweight='bold')
for rect, m in zip(bars_mod, mos_modes):
    ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.12,
            '・'.join(str(v) for v in m), ha='center', fontsize=10, fontweight='bold')
ax.axhline(y=4.0, color='#d73027', linestyle='--', linewidth=1.5, zorder=3)
ax.set_xticks(x)
jp(ax, '各楽器の音色再現度 — 中央値・最頻値とMOP目標値（4.0）', '楽器', '評価値', instruments)
ax.set_ylim(0, 6.2)
ax.set_yticks([1, 2, 3, 4, 5])
if jp_font:
    ax.legend(['MOP目標値（4.0）', '中央値', '最頻値'], prop=jp_font, fontsize=10, loc='lower right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(OUTDIR, 'mos_median_mode.pdf'), dpi=300, bbox_inches='tight')
fig.savefig(os.path.join(OUTDIR, 'mos_median_mode.png'), dpi=300, bbox_inches='tight')
print(f"-> figs/mos_median_mode.pdf saved")

# ============================================================
# 2. ハッカソン参加者共通アンケート（7段階評価）
#    チーム40（n=26）の統計量は配布された集計シートの値を転記
# ============================================================
items = ['没入感・臨場感', '一体感・同期の心地よさ', '演出の華やかさ', '楽しさ・高揚感']
team_n = 26
team_mean = [5.54, 5.00, 6.35, 6.27]
team_sd   = [1.14, 1.60, 0.80, 1.00]
team_med  = [5.5, 6.0, 6.5, 7.0]
team_q1   = [5.0, 4.0, 6.0, 6.0]
team_q3   = [6.75, 6.0, 7.0, 7.0]
# ひげの端（フェンス内の最小値・最大値）と外れ値（集計シートの外れ値欄と整合）
team_whislo = [4, 1, 5, 5]
team_whishi = [7, 7, 7, 7]
team_fliers = [[], [], [4], [4]]
# Shapiro-Wilk 検定（集計シートの Python 算出値）
shapiro_W = [0.8592, 0.8771, 0.7594, 0.7164]
shapiro_p = [0.0022, 0.0050, 0.00004, 0.000009]

all_n = 1671
all_mean = [5.03, 5.20, 5.05, 5.21]
all_sd   = [1.43, 1.40, 1.54, 1.46]

# ---------- 箱ひげ図（五数要約から作成） ----------
fig2, ax2 = plt.subplots(figsize=(9, 5))
bxp_stats = []
for i, item in enumerate(items):
    bxp_stats.append({
        'label': item, 'med': team_med[i], 'q1': team_q1[i], 'q3': team_q3[i],
        'whislo': team_whislo[i], 'whishi': team_whishi[i], 'fliers': team_fliers[i],
    })
ax2.bxp(bxp_stats, showfliers=True, patch_artist=True,
        boxprops=dict(facecolor='#91bfdb', edgecolor='#4575b4'),
        medianprops=dict(color='#d73027', linewidth=2),
        flierprops=dict(marker='o', markerfacecolor='#d73027', markersize=6))
ax2.set_xticks(range(1, len(items) + 1))
jp(ax2, '参加者共通アンケートの回答分布（チーム40，$n=26$）', '評価項目', '評価値（7段階）', items)
ax2.set_ylim(0.5, 7.5)
ax2.set_yticks(range(1, 8))
ax2.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4)
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
plt.tight_layout()
fig2.savefig(os.path.join(OUTDIR, 'hackathon_boxplot.pdf'), dpi=300, bbox_inches='tight')
fig2.savefig(os.path.join(OUTDIR, 'hackathon_boxplot.png'), dpi=300, bbox_inches='tight')
print(f"-> figs/hackathon_boxplot.pdf saved")

# ---------- チーム40 vs 全教室平均の比較棒グラフ（平均±SD） ----------
fig3, ax3 = plt.subplots(figsize=(9, 5))
x3 = np.arange(len(items))
bar_w = 0.32
b1 = ax3.bar(x3 - bar_w / 2, team_mean, bar_w, yerr=team_sd, capsize=4,
             color='#4575b4', edgecolor='white', error_kw=dict(linewidth=1))
b2 = ax3.bar(x3 + bar_w / 2, all_mean, bar_w, yerr=all_sd, capsize=4,
             color='#bdbdbd', edgecolor='white', error_kw=dict(linewidth=1))
for bars in (b1, b2):
    ax3.bar_label(bars, fmt='%.2f', padding=2, fontsize=9, fontweight='bold')
ax3.set_xticks(x3)
jp(ax3, '参加者共通アンケート — チーム40と全教室平均の比較（平均±SD）',
   '評価項目', '評価値（7段階）', items)
ax3.set_ylim(0, 8)
ax3.set_yticks(range(0, 8))
if jp_font:
    ax3.legend([f'チーム40（n={team_n}）', f'全教室（n={all_n}）'],
               prop=jp_font, fontsize=10, loc='upper left')
ax3.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4)
ax3.set_axisbelow(True)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
plt.tight_layout()
fig3.savefig(os.path.join(OUTDIR, 'hackathon_compare.pdf'), dpi=300, bbox_inches='tight')
fig3.savefig(os.path.join(OUTDIR, 'hackathon_compare.png'), dpi=300, bbox_inches='tight')
print(f"-> figs/hackathon_compare.pdf saved")

# ---------- Welchのt検定（要約統計量から）と Cohen の d ----------
print()
print("=" * 70)
print("2. チーム40 vs 全教室: Welchのt検定（要約統計量から算出）・Cohenのd")
print("=" * 70)
print(f"{'評価項目':<14} | {'t値':>7} | {'自由度':>7} | {'p値':>10} | {'d':>6}")
for i, item in enumerate(items):
    m1, s1, n1 = team_mean[i], team_sd[i], team_n
    m2, s2, n2 = all_mean[i], all_sd[i], all_n
    se2 = s1**2 / n1 + s2**2 / n2
    t = (m1 - m2) / math.sqrt(se2)
    df = se2**2 / ((s1**2 / n1)**2 / (n1 - 1) + (s2**2 / n2)**2 / (n2 - 1))
    p = 2 * stats.t.sf(abs(t), df)
    d = (m1 - m2) / s2  # 全教室のSDを基準としたCohenのd
    print(f"{item:<14} | {t:>7.2f} | {df:>7.1f} | {p:>10.4g} | {d:>6.2f}")

# ---------- Shapiro-Wilk（転記値の一覧） ----------
print()
print("Shapiro-Wilk検定（チーム40，集計シートより）:")
for i, item in enumerate(items):
    print(f"  {item}: W={shapiro_W[i]:.4f}, p={shapiro_p[i]:.2g}")

# ============================================================
# 3. ボタン押下成功率 158/160 の 95%Wilson信頼区間
# ============================================================
print()
print("=" * 70)
print("3. ボタン押下成功率の95%Wilson信頼区間")
print("=" * 70)
k, n = 158, 160
z = 1.959963984540054
p_hat = k / n
denom = 1 + z**2 / n
center = (p_hat + z**2 / (2 * n)) / denom
half = z * math.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
print(f"成功率 {p_hat*100:.1f}% ({k}/{n}), 95%Wilson CI = [{(center-half)*100:.1f}%, {(center+half)*100:.1f}%]")
