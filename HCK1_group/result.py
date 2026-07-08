import csv
import numpy as np
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.family'] = 'Hiragino Sans'

# ============================================================
# チーム40 Shapiro-Wilk正規性検定
# ============================================================

# --- データ読み込み ---
with open('team40_抽出.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f)
    rows = list(r)

header = rows[0]
data = rows[1:]
eval_cols = [1, 2, 3, 4]
short_labels = ['没入感・臨場感', '一体感・同期の心地よさ', '演出の華やかさ', '楽しさ・高揚感']

# 各列のデータを取得
col_values = {}
for i, col_idx in enumerate(eval_cols):
    vals = [int(row[col_idx]) for row in data if row[col_idx].strip() != '']
    col_values[short_labels[i]] = np.array(vals)

# --- Shapiro-Wilk検定 ---
alpha = 0.05
results = []

for label, vals in col_values.items():
    stat, p = stats.shapiro(vals)       # Shapiro-Wilk検定
    n = len(vals)                        # サンプル数
    mean = np.mean(vals)                 # 平均値
    std = np.std(vals, ddof=1)           # 標準偏差（不偏）
    median = np.median(vals)             # 中央値
    skew = stats.skew(vals)              # 歪度
    kurt = stats.kurtosis(vals)          # 尖度

    # p値が有意水準より大きければ正規分布に従うと判定
    is_normal = "正規分布に従う" if p > alpha else "正規分布に従わない"

    results.append({
        'label': label, 'n': n, 'mean': mean, 'std': std,
        'median': median, 'skew': skew, 'kurt': kurt,
        'stat': stat, 'p': p, 'judgment': is_normal
    })

# --- 結果表示 ---
print("=" * 70)
print("チーム40 Shapiro-Wilk正規性検定レポート")
print("=" * 70)
print(f"\nサンプル数: {len(data)}名")
print(f"有意水準: α = {alpha}")
print(f"帰無仮説 H0: データは正規分布に従う")
print(f"対立仮説 H1: データは正規分布に従わない")
print(f"判定基準: p値 > {alpha} → H0を棄却しない（正規分布に従う）")
print(f"          p値 ≤ {alpha} → H0を棄却（正規分布に従わない）")
print()

for r_item in results:
    print("-" * 70)
    print(f"【{r_item['label']}】")
    print("-" * 70)
    print(f"  基本統計量:")
    print(f"    平均値       = {r_item['mean']:.4f}")
    print(f"    中央値       = {r_item['median']:.1f}")
    print(f"    標準偏差     = {r_item['std']:.4f}")
    print(f"    歪度         = {r_item['skew']:.4f}")
    print(f"    尖度         = {r_item['kurt']:.4f}")
    print()
    print(f"  Shapiro-Wilk検定:")
    print(f"    検定統計量 W = {r_item['stat']:.4f}")
    print(f"    p値          = {r_item['p']:.6f}")
    print(f"    判定         → {r_item['judgment']}")
    print()

# --- 総合判断 ---
non_normal = [r_item for r_item in results if "従わない" in r_item['judgment']]
print("=" * 70)
print("総合判断")
print("=" * 70)
if len(non_normal) == 0:
    print("全ての項目で正規分布に従うと判定されました。")
    print("→ パラメトリック検定（反復測定ANOVAなど）が使用可能です。")
else:
    print(f"{len(non_normal)}つの項目で正規分布に従わないと判定されました:")
    for item in non_normal:
        print(f"  - {item['label']}（p = {item['p']:.6f}）")
    print()
    print("→ ノンパラメトリック検定（Friedman検定など）の使用を推奨します。")

# --- Q-Qプロット作成 ---
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes = axes.flatten()

for i, (label, vals) in enumerate(col_values.items()):
    ax = axes[i]
    res = stats.probplot(vals, dist="norm", plot=None)
    theoretical = res[0][0]
    ordered = res[0][1]

    ax.scatter(theoretical, ordered, color='#4C72B0', s=40, zorder=5)
    slope, intercept = res[1][0], res[1][1]
    x_line = np.array([theoretical.min(), theoretical.max()])
    ax.plot(x_line, slope * x_line + intercept, 'r--', linewidth=1.5)

    ax.set_title(label, fontsize=13)
    ax.set_xlabel('理論分位数')
    ax.set_ylabel('実測値')

    r_item = results[i]
    ax.text(0.05, 0.95, f'W = {r_item["stat"]:.4f}\np = {r_item["p"]:.4f}',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.grid(True, alpha=0.3)

plt.suptitle('チーム40 Q-Qプロット（正規確率プロット）', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('team40_QQプロット.png', dpi=150)
plt.show()
print("\n[Q-Qプロット画像を保存しました]")
