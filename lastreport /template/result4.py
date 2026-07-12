import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import json

# ============================================================
# Data extracted from the uploaded screenshot
# 【ボタン押下から回転開始時間(ms)】
# If any values are incorrect, please correct them here.
# ============================================================

data = {
    60:  [1380, 1370, 1280, 880, 1850, 1150, 960, 1020, 1460, 1390, 890, 1080, 840, 1050, 1160, 1950],
    90:  [850, 670, 790, 950, 750, 1050, 1020, 820, 660, 810, 920, 850, 1140, 1140, 940, 1100, 1120, 880],
    120: [860, 910, 1150, 900, 910, 880, 630, 750, 780, 890, 720, 510, 570, 740, 970, 890, 1220, 1050, 1030, 820, 1040, 1050, 1080],
    150: [780, 900, 1710, 870, 730, 1070, 780, 2030, 850, 870, 950, 750, 1300, 1160],
    180: [740, 780, 890, 950, 990, 990, 1100, 1150, 970, 850, 1410, 990, 1250, 1160],
}

# User info: 160 total presses, 2 failures
total_presses = 160
total_failures = 2
total_successes = total_presses - total_failures
measured_count = sum(len(v) for v in data.values())

print(f"=== Data Summary ===")
print(f"Total presses (user-reported): {total_presses}")
print(f"Failures: {total_failures}")
print(f"Successes: {total_successes}")
print(f"Data points extracted from image: {measured_count}")
print(f"Note: {total_successes - measured_count} data points may be unread from image")
print()

# Per-BPM statistics
print(f"{'BPM':>5} | {'N':>3} | {'Mean':>8} | {'SD':>8} | {'SEM':>8} | {'Median':>8} | {'Min':>6} | {'Max':>6}")
print("-" * 75)

stats = {}
for bpm in sorted(data.keys()):
    vals = np.array(data[bpm])
    n = len(vals)
    mean = np.mean(vals)
    sd = np.std(vals, ddof=1)
    sem = sd / np.sqrt(n)
    median = np.median(vals)
    vmin = np.min(vals)
    vmax = np.max(vals)
    stats[bpm] = {
        'n': n, 'mean': mean, 'sd': sd, 'sem': sem, 'median': median,
        'min': vmin, 'max': vmax
    }
    print(f"{bpm:>5} | {n:>3} | {mean:>8.1f} | {sd:>8.1f} | {sem:>8.1f} | {median:>8.1f} | {vmin:>6} | {vmax:>6}")

# Overall statistics
all_vals = np.concatenate([np.array(v) for v in data.values()])
all_sd = np.std(all_vals, ddof=1)
all_sem = all_sd / np.sqrt(len(all_vals))
print("-" * 75)
print(f"{'All':>5} | {len(all_vals):>3} | {np.mean(all_vals):>8.1f} | {all_sd:>8.1f} | {all_sem:>8.1f} | {np.median(all_vals):>8.1f} | {np.min(all_vals):>6} | {np.max(all_vals):>6}")

# Check: all within 10 seconds?
threshold_ms = 10000
over_threshold = sum(1 for v in all_vals if v > threshold_ms)
print(f"\n10秒(10000ms)超過: {over_threshold}/{len(all_vals)} 試行")
print(f"全試行が10秒以内: {'Yes' if over_threshold == 0 else 'No'}")
print(f"最大応答時間: {np.max(all_vals)} ms = {np.max(all_vals)/1000:.2f} s")

# ============================================================
# Create bar chart: Mean response time per BPM with error bars
# ============================================================

# Japanese font setup (macOS: Hiragino Sans is bundled with the OS)
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'IPAGothic', 'IPAPGothic', 'Noto Sans CJK JP', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(8, 5))

bpms = sorted(data.keys())
means = [stats[b]['mean'] for b in bpms]
sems = [stats[b]['sem'] for b in bpms]
x = np.arange(len(bpms))

bars = ax.bar(x, means, width=0.5, color='#4472C4', edgecolor='black', linewidth=0.5,
              yerr=sems, capsize=5, error_kw={'linewidth': 1.0, 'color': 'black'})

# Add value labels on bars
for i, (m, s) in enumerate(zip(means, sems)):
    ax.text(i, m + s + 30, f'{m:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('BPM', fontsize=12)
ax.set_ylabel('応答時間 [ms]', fontsize=12)
ax.set_title('BPM別ボタン押下から回転開始までの平均応答時間', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([str(b) for b in bpms], fontsize=11)
ax.set_ylim(0, max(means) + max(sems) + 300)

# Add 10-second threshold line
ax.axhline(y=10000, color='red', linestyle='--', linewidth=1.0, label='許容閾値 (10,000 ms)')
ax.legend(fontsize=9, loc='upper right')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()

import os
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUTDIR, exist_ok=True)
plt.savefig(os.path.join(OUTDIR, 'button_response_chart.pdf'), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(OUTDIR, 'button_response_chart.png'), dpi=300, bbox_inches='tight')
print(f"\nChart saved to {OUTDIR}")