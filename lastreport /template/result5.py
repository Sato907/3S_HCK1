import numpy as np

# ============================================================
# 【ボタンを押してから演奏開始まで(ms)】
# 上：同期開始条件が遅延60ms以下の場合
# 下：同期開始条件が遅延50ms以下の場合
# ============================================================

data_60ms_condition = {
    60:  [8950, 6950, 8230, 7680, 7270],
    90:  [5870, 5070, 6770, 5540, 7250],
    120: [8650, 9700, 7830, 10910, 9710],
    150: [16500, 8630, 8130, 10580, 5000],
    180: [8700, 4920, 12210, 15170, 20130],
}

data_50ms_condition = {
    60:  [8330, 18930, 15090, 50110, 13600, 43660, 10110, 8690],
    90:  [10140, 29340, 12930, 21660, 21020, 13030, 58510, 23900, 11230],
    120: [9700, 16850, 9450, 23760, 19820, 8430, 8170, 16730, 38640, 10460, 7720],
    150: [13720, 8570, 24900, 52600, 14570],
    180: [14970, 6730, 28040, 7230, 31930, 6190, 15680, 6010, 7170, 21790, 9640, 28690],
}

# 1min（60秒）を超過した（=Tanらの60秒閾値を満たさなかった）試行数
# 「途中打ち消し」（計測ミスによる中断）は分析対象から除外する
over_1min_50ms = {60: 2, 90: 1, 120: 0, 150: 5, 180: 0}


def report(name, data, over_1min=None):
    print(f"\n=== {name} ===")
    print(f"{'BPM':>5} | {'N':>3} | {'Mean':>8} | {'SEM':>8} | {'Median':>8} | {'Min':>6} | {'Max':>6}"
          + ("" if over_1min is None else f" | {'1min超過':>8} | {'成功率':>8}"))
    print("-" * (65 if over_1min is None else 90))

    all_vals = []
    total_n = 0
    total_fail = 0
    for bpm in sorted(data.keys()):
        vals = np.array(data[bpm])
        all_vals.extend(vals.tolist())
        n = len(vals)
        mean = np.mean(vals)
        sd = np.std(vals, ddof=1)
        sem = sd / np.sqrt(n)
        median = np.median(vals)
        vmin = np.min(vals)
        vmax = np.max(vals)
        line = f"{bpm:>5} | {n:>3} | {mean:>8.1f} | {sem:>8.1f} | {median:>8.1f} | {vmin:>6} | {vmax:>6}"
        if over_1min is not None:
            fail = over_1min[bpm]
            trials = n + fail
            rate = n / trials * 100
            total_n += trials
            total_fail += fail
            line += f" | {fail:>8} | {rate:>7.1f}%"
        print(line)

    all_vals = np.array(all_vals)
    mean = np.mean(all_vals)
    sd = np.std(all_vals, ddof=1)
    sem = sd / np.sqrt(len(all_vals))
    median = np.median(all_vals)
    print("-" * (65 if over_1min is None else 90))
    line = f"{'全体':>5} | {len(all_vals):>3} | {mean:>8.1f} | {sem:>8.1f} | {median:>8.1f} | {np.min(all_vals):>6} | {np.max(all_vals):>6}"
    if over_1min is not None:
        total_trials = total_n
        rate = len(all_vals) / total_trials * 100
        line += f" | {total_fail:>8} | {rate:>7.1f}%"
    print(line)
    return {
        'n': len(all_vals), 'mean': mean, 'sem': sem, 'median': median,
        'min': np.min(all_vals), 'max': np.max(all_vals),
    }


s60 = report("同期開始条件：遅延60ms以下（全試行が60秒以内に演奏開始）", data_60ms_condition)
s50 = report("同期開始条件：遅延50ms以下（1min超過=Tanらの60秒閾値を超過し演奏未開始）",
             data_50ms_condition, over_1min_50ms)
