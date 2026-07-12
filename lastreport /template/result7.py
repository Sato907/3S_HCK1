#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
結合テスト：エンターテイメント性アンケート結果のグラフ生成スクリプト
- CSATスコア（4または5と回答した割合）を，非標準化（点推定）と
  標準化（95% Wilson信頼区間）の両方で算出し，棒グラフを生成する．
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
import os

# ============================================================
# アンケート結果（1: 不満, 3: どちらともいえない, 4: 満足, 5: 大変満足）
# ============================================================
data = {
    '空間的な楽しさや驚き': [5, 5, 4, 5, 4, 5, 5, 5, 4, 4, 5, 4, 5, 5, 5, 5, 5, 5],
    '操作感':               [5, 4, 4, 4, 5, 4, 5, 4, 5, 4, 4, 4, 1, 4, 5, 5, 5, 3],
    '総合的な楽しさ':       [5, 4, 3, 5, 4, 5, 5, 5, 4, 5, 5, 5, 5, 4, 5, 5, 5, 5],
}

items = list(data.keys())
n_items = len(items)

# ---------- 日本語フォント設定 ----------
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

def apply_font(ax, title, xlabel, ylabel, items_list=None):
    if jp_font:
        ax.set_title(title, fontproperties=jp_font, fontsize=13, fontweight='bold')
        ax.set_xlabel(xlabel, fontproperties=jp_font, fontsize=11)
        ax.set_ylabel(ylabel, fontproperties=jp_font, fontsize=11)
        if items_list:
            ax.set_xticklabels(items_list, fontproperties=jp_font, fontsize=11)
    else:
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# 評価スコア別の回答人数分布（度数分布）
# ============================================================
counts = {item: [data[item].count(k) for k in range(1, 6)] for item in items}

fig0, axes0 = plt.subplots(1, 3, figsize=(13, 4.5))
score_x = np.arange(1, 6)
hist_color = '#4575b4'

for idx, item in enumerate(items):
    ax = axes0.flat[idx]
    n_resp = sum(counts[item])
    bars = ax.bar(score_x, counts[item], width=0.6, color=hist_color, edgecolor='white', linewidth=0.5)
    ax.bar_label(bars, padding=3, fontsize=9, fontweight='bold')
    ax.set_xticks(score_x)
    ax.set_ylim(0, max(max(counts[item]) * 1.25, 5))
    title = f'{item}（N = {n_resp}）'
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

suptitle = 'エンターテイメント性アンケート — 評価スコア別の回答人数分布'
if jp_font:
    fig0.suptitle(suptitle, fontproperties=jp_font, fontsize=15, fontweight='bold')
else:
    fig0.suptitle(suptitle, fontsize=15, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.93])
fig0.savefig(os.path.join(OUTDIR, 'entertainment_score_histogram.pdf'), dpi=300, bbox_inches='tight')
fig0.savefig(os.path.join(OUTDIR, 'entertainment_score_histogram.png'), dpi=300, bbox_inches='tight')
print(f"Graph 0 (per-question score histogram) saved to {OUTDIR}")

print("\n====== 評価スコア別の回答人数分布 ======")
print(f"{'質問項目':<14} {'1':>4} {'2':>4} {'3':>4} {'4':>4} {'5':>4}")
print("-" * 40)
for item in items:
    c = counts[item]
    print(f"{item:<12} {c[0]:>4} {c[1]:>4} {c[2]:>4} {c[3]:>4} {c[4]:>4}")

# ============================================================
# CSATスコアとMOP判定
#   非標準化：CSATの点推定のみで判定
#   標準化　：95% Wilson信頼区間の下限で判定
# ============================================================
MOP_TARGET = 75.0
Z_95 = 1.96

def wilson_ci(count, n, z=Z_95):
    p = count / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return p * 100, (center - margin) * 100, (center + margin) * 100

csat_n, csat_top2, csat_p, csat_lo, csat_hi = [], [], [], [], []
for item in items:
    vals = data[item]
    n_resp = len(vals)
    top2 = sum(1 for v in vals if v >= 4)
    p, lo, hi = wilson_ci(top2, n_resp)
    csat_n.append(n_resp)
    csat_top2.append(top2)
    csat_p.append(p)
    csat_lo.append(lo)
    csat_hi.append(hi)

x = np.arange(n_items)

# ---- グラフ1: CSAT（非標準化，点推定のみ） ----
fig1, ax1 = plt.subplots(figsize=(8, 5))
bars1 = ax1.bar(x, csat_p, width=0.45, color='#4575b4', edgecolor='white', linewidth=0.5, zorder=3)
ax1.bar_label(bars1, fmt='%.1f%%', padding=4, fontsize=10, fontweight='bold',
              bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1.5))
ax1.axhline(y=MOP_TARGET, color='#d73027', linewidth=1.5, linestyle='--', zorder=2)
ax1.set_xticks(x)
apply_font(ax1,
           'エンターテイメント性の CSAT スコア（非標準化：点推定）',
           '質問項目',
           'CSAT スコア [%]',
           items)
ax1.set_xlim(-0.7, n_items - 0.3)
ax1.set_ylim(0, 110)
if jp_font:
    ax1.legend([f'MOP 目標値 ({MOP_TARGET:.0f}%)'], prop=jp_font, fontsize=10, loc='lower right')
else:
    ax1.legend([f'MOP target ({MOP_TARGET:.0f}%)'], fontsize=10, loc='lower right')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3, zorder=0)
ax1.set_axisbelow(True)
plt.tight_layout()
fig1.savefig(os.path.join(OUTDIR, 'csat_entertainment_raw.pdf'), dpi=300, bbox_inches='tight')
fig1.savefig(os.path.join(OUTDIR, 'csat_entertainment_raw.png'), dpi=300, bbox_inches='tight')
print(f"Graph 1 (CSAT, non-standardized) saved to {OUTDIR}")

# ---- グラフ2: CSAT（標準化，95% Wilson信頼区間付き） ----
fig2, ax2 = plt.subplots(figsize=(8, 5))
err_lower = [max(0, p - lo) for p, lo in zip(csat_p, csat_lo)]
err_upper = [max(0, hi - p) for p, hi in zip(csat_p, csat_hi)]
bars2 = ax2.bar(x, csat_p, width=0.45, color='#4575b4', edgecolor='white', linewidth=0.5, zorder=3,
                 yerr=[err_lower, err_upper], capsize=5, error_kw={'linewidth': 1.2, 'color': 'black', 'zorder': 4})
for i, (p, hi) in enumerate(zip(csat_p, csat_hi)):
    ax2.text(x[i], hi + 2.5, f'{p:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.axhline(y=MOP_TARGET, color='#d73027', linewidth=1.5, linestyle='--', zorder=2)
ax2.set_xticks(x)
apply_font(ax2,
           'エンターテイメント性の CSAT スコア（標準化：95% Wilson 信頼区間）',
           '質問項目',
           'CSAT スコア [%]',
           items)
ax2.set_xlim(-0.7, n_items - 0.3)
ax2.set_ylim(0, 115)
if jp_font:
    ax2.legend([f'MOP 目標値 ({MOP_TARGET:.0f}%)'], prop=jp_font, fontsize=10, loc='lower right')
else:
    ax2.legend([f'MOP target ({MOP_TARGET:.0f}%)'], fontsize=10, loc='lower right')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3, zorder=0)
ax2.set_axisbelow(True)
plt.tight_layout()
fig2.savefig(os.path.join(OUTDIR, 'csat_entertainment_wilson.pdf'), dpi=300, bbox_inches='tight')
fig2.savefig(os.path.join(OUTDIR, 'csat_entertainment_wilson.png'), dpi=300, bbox_inches='tight')
print(f"Graph 2 (CSAT, standardized w/ Wilson CI) saved to {OUTDIR}")

# ---------- コンソール出力: 確認用 ----------
print(f"\n====== CSATスコアによるMOP判定（目標値 {MOP_TARGET:.0f}%） ======")
print(f"{'質問項目':<14} {'N':>4} {'Top2Box':>7} {'CSAT[%]':>8} {'95%CI':>16} {'非標準化':>8} {'標準化':>8}")
print("-" * 76)
for i, item in enumerate(items):
    raw_judge = "達成" if csat_p[i] >= MOP_TARGET else "未達成"
    std_judge = "達成" if csat_lo[i] >= MOP_TARGET else "未達成"
    ci_str = f"[{csat_lo[i]:5.1f}, {csat_hi[i]:5.1f}]"
    print(f"{item:<12} {csat_n[i]:>4} {csat_top2[i]:>7} {csat_p[i]:>7.1f} {ci_str:>16} {raw_judge:>8} {std_judge:>8}")

plt.close('all')
print("\nAll graphs generated successfully.")
