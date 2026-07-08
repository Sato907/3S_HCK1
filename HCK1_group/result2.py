import csv
import os
import numpy as np
from scipy import stats
from itertools import combinations

# ============================================================
# チーム40 Friedman検定・Wilcoxon検定 詳細計算過程
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- データ読み込み ---
with open(os.path.join(SCRIPT_DIR, 'team40_抽出.csv'), encoding='utf-8-sig') as f:
    r = csv.reader(f)
    rows = list(r)

header = rows[0]
data = rows[1:]
eval_cols = [1, 2, 3, 4]
short_labels = ['没入感・臨場感', '一体感・同期の心地よさ', '演出の華やかさ', '楽しさ・高揚感']

# 各回答者×各項目のデータ（2次元配列）
raw_data = []
for row in data:
    raw_data.append([int(row[col]) for col in eval_cols])
raw_data = np.array(raw_data)

n = raw_data.shape[0]  # 回答者数 = 26
k = raw_data.shape[1]  # 項目数 = 4

# ============================================================
# 元データの表示
# ============================================================
print("=" * 80)
print("チーム40 Friedman検定・Wilcoxon検定 詳細計算過程")
print("=" * 80)
print(f"\nサンプル数 n = {n}名")
print(f"項目数 k = {k}項目")
print()
print("元データ:")
print(f"{'回答者':>6} {'没入感':>8} {'一体感':>8} {'演出':>8} {'楽しさ':>8}")
print("-" * 42)
for i in range(n):
    print(f"{i+1:>6} {raw_data[i,0]:>8} {raw_data[i,1]:>8} {raw_data[i,2]:>8} {raw_data[i,3]:>8}")


# ============================================================
# 【Friedman検定の計算過程】
# ============================================================
print()
print("=" * 80)
print("【Friedman検定の計算過程】")
print("=" * 80)

# -------------------------------------------------------
# 手順1: 各回答者のデータを順位に変換
# -------------------------------------------------------
print()
print("■ 手順1: 各回答者の中で順位をつける")
print("  （各行の中で、値の小さい順に1,2,3,4と順位をつける）")
print("  （同じ値がある場合は、該当順位の平均をとる＝タイ処理）")
print()

# scipy.stats.rankdata で各行内の順位を算出
ranks = np.zeros_like(raw_data, dtype=float)
for i in range(n):
    ranks[i] = stats.rankdata(raw_data[i])

# 結果表示
print(f"{'回答者':>6} {'没入感':>8} {'一体感':>8} {'演出':>8} {'楽しさ':>8}  ←元データ")
print(f"{'':>6} {'順位':>8} {'順位':>8} {'順位':>8} {'順位':>8}")
print("-" * 55)
for i in range(n):
    vals_str = f"{raw_data[i,0]:>8} {raw_data[i,1]:>8} {raw_data[i,2]:>8} {raw_data[i,3]:>8}"
    rank_str = f"{ranks[i,0]:>8.1f} {ranks[i,1]:>8.1f} {ranks[i,2]:>8.1f} {ranks[i,3]:>8.1f}"
    print(f"{i+1:>6} {vals_str}")
    print(f"{'':>6} {rank_str}")

# -------------------------------------------------------
# 手順2: 各項目の順位合計 Rj を求める
# -------------------------------------------------------
print()
print("■ 手順2: 各項目の順位合計 Rj を求める")
print()

R = np.sum(ranks, axis=0)
R_mean = np.mean(ranks, axis=0)
for j in range(k):
    rank_values = [f"{ranks[i,j]:.1f}" for i in range(n)]
    print(f"  R{j+1}（{short_labels[j]}）:")
    print(f"    = {' + '.join(rank_values)}")
    print(f"    = {R[j]:.1f}")
    print(f"    平均順位 = {R[j]:.1f} / {n} = {R_mean[j]:.4f}")
    print()

# 差がない場合の期待値
expected_R = n * (k + 1) / 2
print(f"  もし差がなければ、各項目の順位合計の期待値 = n × (k+1)/2")
print(f"    = {n} × ({k}+1)/2 = {expected_R:.1f}")
print()

# -------------------------------------------------------
# 手順3: 検定統計量の計算（タイ補正なし版）
# -------------------------------------------------------
print("■ 手順3: 検定統計量 χ² を計算する")
print()
print("  【タイ補正なしの基本公式】")
print("  χ² = [12 / (n × k × (k+1))] × Σ(Rj²) - 3 × n × (k+1)")
print()

sum_R_sq = np.sum(R**2)
print(f"  Σ(Rj²) = {R[0]:.1f}² + {R[1]:.1f}² + {R[2]:.1f}² + {R[3]:.1f}²")
print(f"         = {R[0]**2:.2f} + {R[1]**2:.2f} + {R[2]**2:.2f} + {R[3]**2:.2f}")
print(f"         = {sum_R_sq:.2f}")
print()

coeff = 12 / (n * k * (k + 1))
print(f"  12 / (n × k × (k+1)) = 12 / ({n} × {k} × {k+1})")
print(f"                        = 12 / {n * k * (k+1)}")
print(f"                        = {coeff:.6f}")
print()

term1 = coeff * sum_R_sq
term2 = 3 * n * (k + 1)
chi2_no_tie = term1 - term2
print(f"  χ²（タイ補正なし） = {coeff:.6f} × {sum_R_sq:.2f} - 3 × {n} × {k+1}")
print(f"                     = {term1:.4f} - {term2:.1f}")
print(f"                     = {chi2_no_tie:.4f}")
print()

# -------------------------------------------------------
# 手順3補足: タイ補正の計算
# -------------------------------------------------------
print("  【タイ（同順位）補正】")
print("  同じ値がある場合、検定統計量を補正する必要がある")
print("  補正公式: χ²_corrected = χ²_basic / C")
print("  C = 1 - Σtj / (n × k × (k²-1))")
print("  tj = Σ(tie_count³ - tie_count)  （各回答者のタイグループごと）")
print()

# タイ補正係数の計算
sum_tj = 0
for i in range(n):
    # 各回答者の行で、同じ値のグループを見つける
    unique_vals, counts = np.unique(raw_data[i], return_counts=True)
    tj = np.sum(counts**3 - counts)
    sum_tj += tj

C = 1 - sum_tj / (n * k * (k**2 - 1))
chi2_corrected = chi2_no_tie / C

print(f"  Σtj の計算（各回答者ごと）:")
for i in range(n):
    unique_vals, counts = np.unique(raw_data[i], return_counts=True)
    ties = [(v, c) for v, c in zip(unique_vals, counts) if c > 1]
    tj = np.sum(counts**3 - counts)
    if len(ties) > 0:
        tie_str = ", ".join([f"値{v}が{c}個" for v, c in ties])
        print(f"    回答者{i+1:>2}: タイあり（{tie_str}）→ tj = {tj}")
print()
print(f"  Σtj = {sum_tj}")
print(f"  C = 1 - {sum_tj} / ({n} × {k} × ({k}²-1))")
print(f"    = 1 - {sum_tj} / {n * k * (k**2 - 1)}")
print(f"    = 1 - {sum_tj / (n * k * (k**2 - 1)):.6f}")
print(f"    = {C:.6f}")
print()
print(f"  χ²（タイ補正あり） = {chi2_no_tie:.4f} / {C:.6f}")
print(f"                     = {chi2_corrected:.4f}")
print()

# SciPyでの検証
chi2_scipy, p_scipy = stats.friedmanchisquare(
    raw_data[:, 0], raw_data[:, 1], raw_data[:, 2], raw_data[:, 3]
)
print(f"  ※ SciPyでの計算結果（検証用）:")
print(f"    χ² = {chi2_scipy:.4f}（タイ補正あり）")
print(f"    手計算のタイ補正あり χ² = {chi2_corrected:.4f}")
print()

# -------------------------------------------------------
# 手順4: p値の算出
# -------------------------------------------------------
print("■ 手順4: p値を求める")
print()
print(f"  χ² = {chi2_scipy:.4f} を自由度 df = k-1 = {k-1} のカイ二乗分布で評価")
print()

p_friedman = 1 - stats.chi2.cdf(chi2_scipy, df=k-1)
print(f"  p値 = P(χ²({k-1}) ≥ {chi2_scipy:.4f})")
print(f"      = 1 - CDF({chi2_scipy:.4f}, df={k-1})")
print(f"      = {p_friedman:.6f}")
print()
print(f"  判定: p = {p_friedman:.6f} ≤ α = 0.05")
print(f"  → H0を棄却。4項目間に統計的に有意な差がある。")
print()

# -------------------------------------------------------
# 効果量: Kendall's W
# -------------------------------------------------------
print("■ 効果量: Kendall's W")
print()
W_effect = chi2_scipy / (n * (k - 1))
print(f"  W = χ² / (n × (k-1))")
print(f"    = {chi2_scipy:.4f} / ({n} × {k-1})")
print(f"    = {chi2_scipy:.4f} / {n*(k-1)}")
print(f"    = {W_effect:.4f}")
print()
if W_effect >= 0.5:
    w_interp = "大きい効果"
elif W_effect >= 0.3:
    w_interp = "中程度の効果"
elif W_effect >= 0.1:
    w_interp = "小さい効果"
else:
    w_interp = "ほぼ効果なし"
print(f"  解釈: W = {W_effect:.4f} → {w_interp}")
print()


# ============================================================
# 【Wilcoxon符号付順位検定の計算過程】
# ============================================================
print()
print("=" * 80)
print("【Wilcoxon符号付順位検定の計算過程】")
print("=" * 80)
print()
print("例として「没入感・臨場感 vs 演出の華やかさ」のペアを詳細に計算します。")
print()

col_a = raw_data[:, 0]  # 没入感
col_b = raw_data[:, 2]  # 演出

# -------------------------------------------------------
# 手順1: 差の計算
# -------------------------------------------------------
print("■ 手順1: 各回答者の差 d = 没入感 - 演出 を計算する")
print()

d = col_a - col_b

print(f"{'回答者':>6} {'没入感':>8} {'演出':>8} {'差 d':>8}")
print("-" * 34)
for i in range(n):
    print(f"{i+1:>6} {col_a[i]:>8} {col_b[i]:>8} {d[i]:>8}")

# -------------------------------------------------------
# 手順2: 差が0の回答者を除外
# -------------------------------------------------------
print()
print("■ 手順2: 差が0の回答者を除外する")
print()

zero_idx = np.where(d == 0)[0]
nonzero_idx = np.where(d != 0)[0]
zero_names = ', '.join(str(i+1) for i in zero_idx) if len(zero_idx) > 0 else 'なし'

print(f"  差が0の回答者: {len(zero_idx)}名（回答者番号: {zero_names}）")
print(f"  除外後の有効回答者数 N' = {len(nonzero_idx)}名")
print()

d_nonzero = d[nonzero_idx]
abs_d = np.abs(d_nonzero)
N_prime = len(d_nonzero)

# -------------------------------------------------------
# 手順3: 絶対値に順位をつける
# -------------------------------------------------------
print("■ 手順3: 差の絶対値に順位をつける（タイ処理あり）")
print()

abs_ranks = stats.rankdata(abs_d)

# ソートして表示
sorted_indices = np.argsort(abs_d)
print(f"{'回答者':>6} {'差 d':>8} {'|d|':>8} {'順位':>8}")
print("-" * 34)
for idx in sorted_indices:
    orig_idx = nonzero_idx[idx] + 1
    print(f"{orig_idx:>6} {d_nonzero[idx]:>8} {abs_d[idx]:>8} {abs_ranks[idx]:>8.1f}")

# -------------------------------------------------------
# 手順4: 正の順位和と負の順位和
# -------------------------------------------------------
print()
print("■ 手順4: 正の順位和 W⁺ と負の順位和 W⁻ を求める")
print()

pos_mask = d_nonzero > 0
neg_mask = d_nonzero < 0

W_plus = np.sum(abs_ranks[pos_mask])
W_minus = np.sum(abs_ranks[neg_mask])

pos_ranks_str = [f"{abs_ranks[i]:.1f}" for i in range(len(d_nonzero)) if d_nonzero[i] > 0]
neg_ranks_str = [f"{abs_ranks[i]:.1f}" for i in range(len(d_nonzero)) if d_nonzero[i] < 0]

print(f"  W⁺（差が正＝没入感 > 演出 の回答者の順位和）:")
if len(pos_ranks_str) > 0:
    print(f"    = {' + '.join(pos_ranks_str)}")
else:
    print(f"    = 0（該当者なし）")
print(f"    = {W_plus:.1f}")
print()
print(f"  W⁻（差が負＝没入感 < 演出 の回答者の順位和）:")
if len(neg_ranks_str) > 0:
    print(f"    = {' + '.join(neg_ranks_str)}")
else:
    print(f"    = 0（該当者なし）")
print(f"    = {W_minus:.1f}")
print()

# -------------------------------------------------------
# 手順5: 検定統計量
# -------------------------------------------------------
print("■ 手順5: 検定統計量 W を求める")
print()

W_stat = min(W_plus, W_minus)
print(f"  W = min(W⁺, W⁻) = min({W_plus:.1f}, {W_minus:.1f}) = {W_stat:.1f}")
print()

# 検証
expected_sum = N_prime * (N_prime + 1) / 2
print(f"  ※ 検証: W⁺ + W⁻ = {W_plus:.1f} + {W_minus:.1f} = {W_plus + W_minus:.1f}")
print(f"          N'×(N'+1)/2 = {N_prime}×{N_prime+1}/2 = {expected_sum:.1f}")
print(f"          → 一致するので計算は正しい")
print()

# -------------------------------------------------------
# 手順6: Zスコアとp値
# -------------------------------------------------------
print("■ 手順6: 正規近似によるZスコアとp値の算出")
print()

mu_W = N_prime * (N_prime + 1) / 4
sigma_W = np.sqrt(N_prime * (N_prime + 1) * (2 * N_prime + 1) / 24)

print(f"  Wの期待値 μ_W = N'×(N'+1) / 4")
print(f"               = {N_prime}×{N_prime+1} / 4")
print(f"               = {N_prime*(N_prime+1)} / 4")
print(f"               = {mu_W:.2f}")
print()
print(f"  Wの標準偏差 σ_W = √(N'×(N'+1)×(2N'+1) / 24)")
print(f"                  = √({N_prime}×{N_prime+1}×{2*N_prime+1} / 24)")
print(f"                  = √({N_prime*(N_prime+1)*(2*N_prime+1)} / 24)")
print(f"                  = √({N_prime*(N_prime+1)*(2*N_prime+1)/24:.4f})")
print(f"                  = {sigma_W:.4f}")
print()

Z_manual = (W_stat - mu_W) / sigma_W
print(f"  Z = (W - μ_W) / σ_W")
print(f"    = ({W_stat:.1f} - {mu_W:.2f}) / {sigma_W:.4f}")
print(f"    = {W_stat - mu_W:.2f} / {sigma_W:.4f}")
print(f"    = {Z_manual:.4f}")
print()

# 両側検定のp値
p_manual = 2 * stats.norm.cdf(Z_manual)  # Zは負の値なので左側確率×2
print(f"  p値（両側検定）= 2 × P(Z ≤ {Z_manual:.4f})")
print(f"                 = 2 × Φ({Z_manual:.4f})")
print(f"                 = 2 × {stats.norm.cdf(Z_manual):.6f}")
print(f"                 = {p_manual:.6f}")
print()

# SciPyでの検証
stat_scipy, p_scipy_w = stats.wilcoxon(col_a, col_b)
print(f"  ※ SciPyでの計算結果（検証用）:")
print(f"    W = {stat_scipy:.4f}, p = {p_scipy_w:.6f}")
print(f"    （SciPyはタイ補正や連続性補正を行うため、手計算と若干異なります）")
print()

# -------------------------------------------------------
# 手順7: 効果量
# -------------------------------------------------------
print("■ 手順7: 効果量 r の計算")
print()

Z_for_effect = stats.norm.ppf(1 - p_scipy_w / 2)
r_effect = Z_for_effect / np.sqrt(n)
print(f"  SciPyのp値からZを逆算:")
print(f"  |Z| = Φ⁻¹(1 - p/2) = Φ⁻¹(1 - {p_scipy_w:.6f}/2)")
print(f"       = Φ⁻¹({1 - p_scipy_w/2:.6f})")
print(f"       = {Z_for_effect:.4f}")
print()
print(f"  r = |Z| / √n")
print(f"    = {Z_for_effect:.4f} / √{n}")
print(f"    = {Z_for_effect:.4f} / {np.sqrt(n):.4f}")
print(f"    = {r_effect:.4f}")
print()

if abs(r_effect) >= 0.5:
    r_interp = "大きい効果"
elif abs(r_effect) >= 0.3:
    r_interp = "中程度の効果"
elif abs(r_effect) >= 0.1:
    r_interp = "小さい効果"
else:
    r_interp = "ほぼ効果なし"
print(f"  解釈: r = {r_effect:.4f} → {r_interp}")
print()

# -------------------------------------------------------
# 手順8: Bonferroni補正
# -------------------------------------------------------
print("■ 手順8: Bonferroni補正による判定")
print()

num_comp = 6
bonf = 0.05 / num_comp
print(f"  比較ペア数 = C({k},2) = {k}! / (2! × {k-2}!) = {num_comp}")
print(f"  補正後の有意水準 α' = 0.05 / {num_comp} = {bonf:.4f}")
print()
print(f"  p = {p_scipy_w:.6f} {'≤' if p_scipy_w <= bonf else '>'} α' = {bonf:.4f}")
if p_scipy_w <= bonf:
    print(f"  → 有意差あり")
else:
    print(f"  → 有意差なし")
print()


# ============================================================
# 【残り5ペアの計算結果】
# ============================================================
print()
print("=" * 80)
print("【残り5ペアの計算結果】")
print("=" * 80)
print()
print("同じ手順で残りの5ペアを計算した結果:")
print()

all_pairs = list(combinations(range(k), 2))
all_results = []

for (i, j) in all_pairs:
    d_pair = raw_data[:, i] - raw_data[:, j]
    n_eff = np.sum(d_pair != 0)
    pos_count = np.sum(d_pair > 0)
    neg_count = np.sum(d_pair < 0)
    zero_count = np.sum(d_pair == 0)

    stat_w, p_w = stats.wilcoxon(raw_data[:, i], raw_data[:, j])
    z_val = stats.norm.ppf(1 - p_w / 2)
    r_val = z_val / np.sqrt(n)

    if abs(r_val) >= 0.5:
        r_int = "大きい"
    elif abs(r_val) >= 0.3:
        r_int = "中程度"
    elif abs(r_val) >= 0.1:
        r_int = "小さい"
    else:
        r_int = "ほぼなし"

    sig = "有意差あり **" if p_w <= bonf else "有意差なし"

    all_results.append({
        'i': i, 'j': j, 'n_eff': n_eff,
        'pos': pos_count, 'neg': neg_count, 'zero': zero_count,
        'stat': stat_w, 'p': p_w, 'z': z_val, 'r': r_val,
        'r_int': r_int, 'sig': sig
    })

    # 詳細計算済みのペアはスキップ
    if i == 0 and j == 2:
        continue

    print(f"--- {short_labels[i]} vs {short_labels[j]} ---")
    print(f"  差が0でない回答者数 N' = {n_eff}")
    print(f"  正の差（{short_labels[i]}が高い）: {pos_count}名")
    print(f"  負の差（{short_labels[j]}が高い）: {neg_count}名")
    print(f"  差なし: {zero_count}名")
    print(f"  W = {stat_w:.4f}")
    print(f"  p = {p_w:.6f}")
    print(f"  Z = {z_val:.4f}")
    print(f"  r = {r_val:.4f}（{r_int}）")
    print(f"  判定: {sig}")
    print()


# ============================================================
# 最終結果まとめ
# ============================================================
print("=" * 80)
print("最終結果まとめ")
print("=" * 80)
print()
print(f"{'ペア':<40} {'p値':>10} {'r':>8} {'判定':>14}")
print("-" * 74)

for res in all_results:
    pair_name = f"{short_labels[res['i']]} vs {short_labels[res['j']]}"
    print(f"{pair_name:<40} {res['p']:>10.6f} {res['r']:>8.4f} {res['sig']:>14}")

print()