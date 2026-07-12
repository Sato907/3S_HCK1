#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音色再現度テスト結果のグラフ生成スクリプト
- 100%積み上げ棒グラフ（回答分布）
- 中央値・最頻値の棒グラフ（記述統計）
- 楽器別ヒストグラム（評価スコア別の人数，サンプル数Nを表示）
- CSATスコアによるMOP判定（非標準化：点推定 / 標準化：95%Wilson信頼区間）
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
import os

# ============================================================
# ★ ここに実際のデータを入力してください ★
# 各楽器の回答人数 [1:全く似ていない, 2:あまり似ていない, 3:どちらともいえない, 4:ある程度似ている, 5:非常に似ている]
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
n_instruments = len(instruments)

# data は各楽器の個々の回答（1〜5の生データ）のリストであるため，
# 度数分布（[1の人数, 2の人数, 3の人数, 4の人数, 5の人数]）に変換する
counts = {inst: [data[inst].count(k) for k in range(1, 6)] for inst in instruments}

# ---------- 統計量の計算 ----------
def compute_median(counts):
    """度数分布から中央値を計算（順序尺度のため，累積度数で判定）"""
    total = sum(counts)
    cumsum = 0
    for i, c in enumerate(counts):
        cumsum += c
        if cumsum >= total / 2:
            return i + 1  # 評価値は1~5
    return 5

def compute_mode(counts):
    """最頻値を計算"""
    return counts.index(max(counts)) + 1

medians = [compute_median(counts[inst]) for inst in instruments]
modes   = [compute_mode(counts[inst])   for inst in instruments]

# ---------- 日本語フォント設定 ----------
# macOS: Hiragino Sans（システム標準搭載）を優先，なければ IPAexGothic / Noto Sans CJK JP
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
    # フォールバック: matplotlib のデフォルト設定を試行
    plt.rcParams['font.family'] = 'sans-serif'
    jp_font = None

def apply_font(ax, title, xlabel, ylabel, instruments_list=None):
    """軸ラベルとタイトルに日本語フォントを適用"""
    if jp_font:
        ax.set_title(title, fontproperties=jp_font, fontsize=13, fontweight='bold')
        ax.set_xlabel(xlabel, fontproperties=jp_font, fontsize=11)
        ax.set_ylabel(ylabel, fontproperties=jp_font, fontsize=11)
        if instruments_list:
            ax.set_xticklabels(instruments_list, fontproperties=jp_font, fontsize=10)
    else:
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)

# ============================================================
# グラフ1: 100%積み上げ棒グラフ
# ============================================================
fig1, ax1 = plt.subplots(figsize=(9, 5.5))

categories = ['1: 全く似ていない', '2: あまり似ていない', '3: どちらともいえない',
              '4: ある程度似ている', '5: 非常に似ている']
colors = ['#d73027', '#fc8d59', '#fee08b', '#91bfdb', '#4575b4']

# パーセント変換
percentages = {}
for inst in instruments:
    total = sum(counts[inst])
    percentages[inst] = [c / total * 100 for c in counts[inst]]

x = np.arange(n_instruments)
bar_width = 0.55
bottoms = np.zeros(n_instruments)

bars_list = []
for i in range(5):
    vals = [percentages[inst][i] for inst in instruments]
    b = ax1.bar(x, vals, bar_width, bottom=bottoms, color=colors[i], edgecolor='white', linewidth=0.5)
    bars_list.append(b)
    # パーセント値を表示（5%以上のみ）
    for j, v in enumerate(vals):
        if v >= 5:
            label_text = f'{v:.0f}%'
            if jp_font:
                ax1.text(j, bottoms[j] + v/2, label_text,
                         ha='center', va='center', fontsize=8, fontweight='bold',
                         color='black' if i in [2,3] else 'white')
            else:
                ax1.text(j, bottoms[j] + v/2, label_text,
                         ha='center', va='center', fontsize=8, fontweight='bold',
                         color='black' if i in [2,3] else 'white')
    bottoms += vals

ax1.set_xticks(x)
apply_font(ax1,
           '各楽器の音色再現度 — 回答分布（100%積み上げ棒グラフ）',
           '楽器',
           '回答割合 [%]',
           instruments)
ax1.set_ylim(0, 100)
ax1.set_yticks(range(0, 101, 10))
ax1.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.4, zorder=0)
ax1.set_axisbelow(True)

# 凡例
if jp_font:
    legend_labels = [plt.Rectangle((0,0),1,1, fc=colors[i]) for i in range(5)]
    leg = ax1.legend(legend_labels, categories, loc='upper center',
                     bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False,
                     prop=jp_font, fontsize=9)
else:
    legend_labels = [plt.Rectangle((0,0),1,1, fc=colors[i]) for i in range(5)]
    ax1.legend(legend_labels, categories, loc='upper center',
               bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0.08, 1, 1])
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUTDIR, exist_ok=True)
fig1.savefig(os.path.join(OUTDIR, 'stacked_bar.pdf'), dpi=300, bbox_inches='tight')
fig1.savefig(os.path.join(OUTDIR, 'stacked_bar.png'), dpi=300, bbox_inches='tight')
print(f"Graph 1 (stacked bar) saved to {OUTDIR}")

# ============================================================
# グラフ2: 中央値・最頻値の棒グラフ（記述統計．MOPの判定線は付けない）
# MOP の判定は，後段の CSAT スコア（非標準化／標準化）で行う．
# ============================================================
fig2, ax2 = plt.subplots(figsize=(9, 5))

x2 = np.arange(n_instruments)
bar_w = 0.3

bars_med = ax2.bar(x2 - bar_w/2, medians, bar_w, color='#4575b4', edgecolor='white', linewidth=0.5)
bars_mod = ax2.bar(x2 + bar_w/2, modes,   bar_w, color='#91bfdb', edgecolor='white', linewidth=0.5)

# 数値ラベル（bar_label はポイント単位で余白を取るため，スケールに関わらず一定の見やすさを保てる）
for bar_group in [bars_med, bars_mod]:
    ax2.bar_label(bar_group, fmt='%.1f', padding=4, fontsize=10, fontweight='bold')

ax2.set_xticks(x2)
apply_font(ax2,
           '各楽器の音色再現度 — 中央値・最頻値（記述統計）',
           '楽器',
           '評価値',
           instruments)
ax2.set_xlim(-0.8, n_instruments - 0.2)
ax2.set_ylim(0, 6.2)
ax2.set_yticks([1, 2, 3, 4, 5])

# 凡例
if jp_font:
    ax2.legend(['中央値', '最頻値'], prop=jp_font, fontsize=10, loc='lower right')
else:
    ax2.legend(['Median', 'Mode'], fontsize=10, loc='lower right')

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
fig2.savefig(os.path.join(OUTDIR, 'median_mode_bar.pdf'), dpi=300, bbox_inches='tight')
fig2.savefig(os.path.join(OUTDIR, 'median_mode_bar.png'), dpi=300, bbox_inches='tight')
print(f"Graph 2 (median/mode bar) saved to {OUTDIR}")

# ============================================================
# グラフ3: 楽器別ヒストグラム（x軸=評価スコア1〜5，y軸=人数，N を表示）
# ============================================================
fig3, axes3 = plt.subplots(2, 3, figsize=(13, 8))
score_x = np.arange(1, 6)
hist_color = '#4575b4'

for idx, inst in enumerate(instruments):
    ax = axes3.flat[idx]
    n_resp = sum(counts[inst])
    bars = ax.bar(score_x, counts[inst], width=0.6, color=hist_color, edgecolor='white', linewidth=0.5)
    ax.bar_label(bars, padding=3, fontsize=9, fontweight='bold')
    ax.set_xticks(score_x)
    ax.set_ylim(0, max(max(counts[inst]) * 1.25, 5))
    title = f'{inst}（N = {n_resp}）'
    if jp_font:
        ax.set_title(title, fontproperties=jp_font, fontsize=12, fontweight='bold')
        ax.set_xlabel('評価スコア', fontproperties=jp_font, fontsize=10)
        ax.set_ylabel('人数 [人]', fontproperties=jp_font, fontsize=10)
    else:
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Score', fontsize=10)
        ax.set_ylabel('Count', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

suptitle = '各楽器の音色再現度 — 評価スコア別の回答人数分布'
if jp_font:
    fig3.suptitle(suptitle, fontproperties=jp_font, fontsize=15, fontweight='bold')
else:
    fig3.suptitle(suptitle, fontsize=15, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig3.savefig(os.path.join(OUTDIR, 'score_histogram.pdf'), dpi=300, bbox_inches='tight')
fig3.savefig(os.path.join(OUTDIR, 'score_histogram.png'), dpi=300, bbox_inches='tight')
print(f"Graph 3 (per-instrument score histogram) saved to {OUTDIR}")

# ============================================================
# CSAT スコアによる MOP 判定
#   非標準化：CSAT の点推定（4 または 5 と回答した割合）のみで判定
#   標準化　：95% Wilson 信頼区間の下限で判定（サンプルサイズに基づく
#             推定の不確実性を考慮した，より保守的で信頼性の高い判定）
# MOP 目標値は結合テストのエンターテイメント性評価と同一の 75%\cite{acsi} を用いる．
# ============================================================
MOP_TARGET = 75.0
Z_95 = 1.96

def wilson_ci(count, n, z=Z_95):
    """2項比率に対する Wilson score interval（95%信頼区間）を返す"""
    p = count / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return p * 100, (center - margin) * 100, (center + margin) * 100

csat_n = []
csat_top2 = []
csat_p = []
csat_lo = []
csat_hi = []
for inst in instruments:
    n_resp = sum(counts[inst])
    top2 = sum(1 for v in data[inst] if v >= 4)
    p, lo, hi = wilson_ci(top2, n_resp)
    csat_n.append(n_resp)
    csat_top2.append(top2)
    csat_p.append(p)
    csat_lo.append(lo)
    csat_hi.append(hi)

# ---- グラフ4: CSAT（非標準化，点推定のみ） ----
fig4, ax4 = plt.subplots(figsize=(9, 5))
bars4 = ax4.bar(x2, csat_p, width=0.5, color='#4575b4', edgecolor='white', linewidth=0.5, zorder=3)
ax4.bar_label(bars4, fmt='%.1f%%', padding=4, fontsize=10, fontweight='bold',
              bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1.5))
ax4.axhline(y=MOP_TARGET, color='#d73027', linewidth=1.5, linestyle='--', zorder=2)
ax4.set_xticks(x2)
apply_font(ax4,
           '各楽器の CSAT スコア（非標準化：点推定）',
           '楽器',
           'CSAT スコア [%]',
           instruments)
ax4.set_xlim(-0.8, n_instruments - 0.2)
ax4.set_ylim(0, 105)
if jp_font:
    ax4.legend([f'MOP 目標値 ({MOP_TARGET:.0f}%)'], prop=jp_font, fontsize=10, loc='lower right')
else:
    ax4.legend([f'MOP target ({MOP_TARGET:.0f}%)'], fontsize=10, loc='lower right')
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3, zorder=0)
ax4.set_axisbelow(True)
plt.tight_layout()
fig4.savefig(os.path.join(OUTDIR, 'csat_raw.pdf'), dpi=300, bbox_inches='tight')
fig4.savefig(os.path.join(OUTDIR, 'csat_raw.png'), dpi=300, bbox_inches='tight')
print(f"Graph 4 (CSAT, non-standardized) saved to {OUTDIR}")

# ---- グラフ5: CSAT（標準化，95% Wilson信頼区間付き） ----
fig5, ax5 = plt.subplots(figsize=(9, 5))
err_lower = [max(0, p - lo) for p, lo in zip(csat_p, csat_lo)]
err_upper = [max(0, hi - p) for p, hi in zip(csat_p, csat_hi)]
bars5 = ax5.bar(x2, csat_p, width=0.5, color='#4575b4', edgecolor='white', linewidth=0.5, zorder=3,
                 yerr=[err_lower, err_upper], capsize=5, error_kw={'linewidth': 1.2, 'color': 'black', 'zorder': 4})
for i, (p, lo, hi) in enumerate(zip(csat_p, csat_lo, csat_hi)):
    ax5.text(x2[i], hi + 2.5, f'{p:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax5.axhline(y=MOP_TARGET, color='#d73027', linewidth=1.5, linestyle='--', zorder=2)
ax5.set_xticks(x2)
apply_font(ax5,
           '各楽器の CSAT スコア（標準化：95% Wilson 信頼区間）',
           '楽器',
           'CSAT スコア [%]',
           instruments)
ax5.set_xlim(-0.8, n_instruments - 0.2)
ax5.set_ylim(0, 110)
if jp_font:
    ax5.legend([f'MOP 目標値 ({MOP_TARGET:.0f}%)'], prop=jp_font, fontsize=10, loc='lower right')
else:
    ax5.legend([f'MOP target ({MOP_TARGET:.0f}%)'], fontsize=10, loc='lower right')
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3, zorder=0)
ax5.set_axisbelow(True)
plt.tight_layout()
fig5.savefig(os.path.join(OUTDIR, 'csat_wilson.pdf'), dpi=300, bbox_inches='tight')
fig5.savefig(os.path.join(OUTDIR, 'csat_wilson.png'), dpi=300, bbox_inches='tight')
print(f"Graph 5 (CSAT, standardized w/ Wilson CI) saved to {OUTDIR}")

# ---------- コンソール出力: 確認用 ----------
print("\n====== 記述統計（中央値・最頻値） ======")
print(f"{'楽器':<14} {'N':>4} {'中央値':>6} {'最頻値':>6}")
print("-" * 40)
for i, inst in enumerate(instruments):
    print(f"{inst:<12} {sum(counts[inst]):>4} {medians[i]:>6} {modes[i]:>6}")

print(f"\n====== CSATスコアによるMOP判定（目標値 {MOP_TARGET:.0f}%） ======")
print(f"{'楽器':<14} {'N':>4} {'Top2Box':>7} {'CSAT[%]':>8} {'95%CI':>16} {'非標準化':>8} {'標準化':>8}")
print("-" * 76)
for i, inst in enumerate(instruments):
    raw_judge = "達成" if csat_p[i] >= MOP_TARGET else "未達成"
    std_judge = "達成" if csat_lo[i] >= MOP_TARGET else "未達成"
    ci_str = f"[{csat_lo[i]:5.1f}, {csat_hi[i]:5.1f}]"
    print(f"{inst:<12} {csat_n[i]:>4} {csat_top2[i]:>7} {csat_p[i]:>7.1f} {ci_str:>16} {raw_judge:>8} {std_judge:>8}")

plt.close('all')
print("\nAll graphs generated successfully.")