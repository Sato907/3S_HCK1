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
#    生データは data/ 内の4教室分CSV（参加者共通アンケートの回答）から読み込む
# ============================================================
import csv
import glob

items = ['没入感・臨場感', '一体感・同期の心地よさ', '演出の華やかさ', '楽しさ・高揚感']
TEAM = 40

rows_all, rows_team = [], []
DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
for f in sorted(glob.glob(os.path.join(DATADIR, '*.csv'))):
    with open(f, encoding='utf-8-sig') as fh:
        reader = csv.reader(fh)
        next(reader)  # ヘッダ
        for row in reader:
            if len(row) < 5 or not row[0].strip():
                continue
            try:
                team = int(row[0])
                vals = [int(row[i]) for i in range(1, 5)]
            except ValueError:
                continue
            rows_all.append(vals)
            if team == TEAM:
                rows_team.append(vals)

arr_team = np.array(rows_team)   # (26, 4)
arr_all = np.array(rows_all)     # (1671, 4)
n_team, n_all = len(arr_team), len(arr_all)
print()
print("=" * 70)
print(f"2. 参加者共通アンケート: チーム{TEAM} n={n_team}, 全教室 n={n_all}")
print("=" * 70)

# ---------- 記述統計量と Shapiro-Wilk 検定（チーム40，生データから算出） ----------
print(f"{'評価項目':<14} | 平均 |  SD | 中央値 | 最頻値 | Q1 | Q3 | 歪度 | 尖度 |  W | p値")
for i, item in enumerate(items):
    a = arr_team[:, i]
    counts = np.bincount(a, minlength=8)[1:8]
    max_c = counts.max()
    modes = '・'.join(str(k + 1) for k in range(7) if counts[k] == max_c)
    q1, q3 = np.percentile(a, [25, 75])
    skew = stats.skew(a, bias=False)
    kurt = stats.kurtosis(a, bias=False)
    W, p = stats.shapiro(a)
    print(f"{item:<14} | {a.mean():.2f} | {a.std(ddof=1):.2f} | {np.median(a):>4} | {modes:>5} | "
          f"{q1:>4} | {q3:>4} | {skew:>5.2f} | {kurt:>5.2f} | {W:.3f} | {p:.2g}")

# ---------- 箱ひげ図（生データから作成，凡例付き） ----------
fig2, ax2 = plt.subplots(figsize=(9, 5))
bp = ax2.boxplot([arr_team[:, i] for i in range(4)], patch_artist=True, widths=0.5,
                 boxprops=dict(facecolor='#91bfdb', edgecolor='#4575b4'),
                 medianprops=dict(color='#d73027', linewidth=2),
                 flierprops=dict(marker='o', markerfacecolor='#d73027', markersize=6,
                                 markeredgecolor='black'))
ax2.set_xticks(range(1, 5))
jp(ax2, f'参加者共通アンケートの回答分布（チーム40，$n={n_team}$）', '評価項目', '評価値（7段階）', items)
ax2.set_ylim(0.5, 7.5)
ax2.set_yticks(range(1, 8))
ax2.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4)
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
# 凡例（箱・中央値・ひげ・外れ値の説明）
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_handles = [
    Patch(facecolor='#91bfdb', edgecolor='#4575b4', label='箱：四分位範囲（$Q_1$〜$Q_3$）'),
    Line2D([0], [0], color='#d73027', linewidth=2, label='太線：中央値'),
    Line2D([0], [0], color='black', linewidth=1, label='ひげ：外れ値を除く最小値・最大値'),
    Line2D([0], [0], marker='o', color='none', markerfacecolor='#d73027',
           markeredgecolor='black', markersize=6, label='点：外れ値（$Q_1-1.5$IQR未満または$Q_3+1.5$IQR超）'),
]
if jp_font:
    ax2.legend(handles=legend_handles, prop=jp_font, fontsize=9, loc='lower left', framealpha=0.9)
else:
    ax2.legend(handles=legend_handles, fontsize=9, loc='lower left', framealpha=0.9)
plt.tight_layout()
fig2.savefig(os.path.join(OUTDIR, 'hackathon_boxplot.pdf'), dpi=300, bbox_inches='tight')
fig2.savefig(os.path.join(OUTDIR, 'hackathon_boxplot.png'), dpi=300, bbox_inches='tight')
print(f"-> figs/hackathon_boxplot.pdf saved")

# ---------- Q-Qプロット（正規分布との比較，2×2） ----------
# 横軸: 理論分位数 Φ^{-1}((i-0.5)/n)，縦軸: 順序統計量（実測値を昇順に並べた値）
fig_qq, axes = plt.subplots(2, 2, figsize=(9, 8))
for i, item in enumerate(items):
    ax = axes[i // 2][i % 2]
    a = np.sort(arr_team[:, i])
    n = len(a)
    theo = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    ax.scatter(theo, a, color='#4575b4', s=28, zorder=3)
    # 参照直線: データが正規分布に従う場合の期待直線（平均と標準偏差から構成）
    ref_x = np.array([theo.min(), theo.max()])
    ax.plot(ref_x, a.mean() + a.std(ddof=1) * ref_x, color='#d73027', linewidth=1.5, zorder=2)
    if jp_font:
        ax.set_title(item, fontproperties=jp_font, fontsize=11, fontweight='bold')
        ax.set_xlabel('理論分位数', fontproperties=jp_font, fontsize=10)
        ax.set_ylabel('実測値（順序統計量）', fontproperties=jp_font, fontsize=10)
    ax.set_ylim(0.5, 7.8)
    ax.set_yticks(range(1, 8))
    ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
plt.tight_layout()
fig_qq.savefig(os.path.join(OUTDIR, 'hackathon_qq.pdf'), dpi=300, bbox_inches='tight')
fig_qq.savefig(os.path.join(OUTDIR, 'hackathon_qq.png'), dpi=300, bbox_inches='tight')
print(f"-> figs/hackathon_qq.pdf saved")

# ---------- チーム40 vs 全教室平均の比較棒グラフ（平均±SD） ----------
team_mean = arr_team.mean(axis=0)
team_sd = arr_team.std(axis=0, ddof=1)
all_mean = arr_all.mean(axis=0)
all_sd = arr_all.std(axis=0, ddof=1)

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
    ax3.legend([f'チーム40（n={n_team}）', f'全教室（n={n_all}）'],
               prop=jp_font, fontsize=10, loc='upper left')
ax3.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4)
ax3.set_axisbelow(True)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
plt.tight_layout()
fig3.savefig(os.path.join(OUTDIR, 'hackathon_compare.pdf'), dpi=300, bbox_inches='tight')
fig3.savefig(os.path.join(OUTDIR, 'hackathon_compare.png'), dpi=300, bbox_inches='tight')
print(f"-> figs/hackathon_compare.pdf saved")

# ---------- チーム40 vs 全教室: Welchのt検定・Cohenのd・Mann-WhitneyのU検定 ----------
print()
print(f"{'評価項目':<14} | {'t値':>6} | {'自由度':>6} | {'p(Welch)':>9} | {'d':>6} | {'U':>8} | {'p(MW)':>9}")
for i, item in enumerate(items):
    a, b = arr_team[:, i], arr_all[:, i]
    t, p_w = stats.ttest_ind(a, b, equal_var=False)
    se2 = a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)
    df = se2**2 / ((a.var(ddof=1) / len(a))**2 / (len(a) - 1) + (b.var(ddof=1) / len(b))**2 / (len(b) - 1))
    d = (a.mean() - b.mean()) / b.std(ddof=1)
    U, p_mw = stats.mannwhitneyu(a, b, alternative='two-sided')
    print(f"{item:<14} | {t:>6.2f} | {df:>6.1f} | {p_w:>9.3g} | {d:>6.2f} | {U:>8.1f} | {p_mw:>9.3g}")

# ---------- 項目間の比較: Friedman検定と事後Wilcoxon符号付き順位検定（Holm補正） ----------
print()
chi2, p_fr = stats.friedmanchisquare(*[arr_team[:, i] for i in range(4)])
print(f"Friedman検定: chi2={chi2:.2f}, df=3, p={p_fr:.2g}")

pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
results = []
for i, j in pairs:
    diff = arr_team[:, i] - arr_team[:, j]
    # 差が0のペアはWilcoxon検定の慣例に従い除外（zero-splitはscipyのデフォルト'wilcox'）
    try:
        stat_w, p = stats.wilcoxon(arr_team[:, i], arr_team[:, j])
    except ValueError:
        stat_w, p = np.nan, 1.0
    results.append([i, j, stat_w, p])

# Holm補正: p値を昇順に並べ，k番目のp値に (m-k+1) を乗じる（単調性を保証）
m = len(results)
order = np.argsort([r[3] for r in results])
adj = {}
running_max = 0.0
for rank, idx in enumerate(order):
    p_adj = min(1.0, results[idx][3] * (m - rank))
    running_max = max(running_max, p_adj)
    adj[idx] = running_max
print(f"{'ペア':<30} | {'W':>6} | {'p値':>9} | {'Holm補正p':>10}")
for idx, (i, j, stat_w, p) in enumerate(results):
    name = f"{items[i][:3]} vs {items[j][:3]}"
    print(f"{name:<30} | {stat_w:>6.1f} | {p:>9.3g} | {adj[idx]:>10.3g}")

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
