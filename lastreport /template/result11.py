#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関数別フローチャート生成スクリプト（図35・図36の形式，影なし）
- 端子：角丸，処理：矩形，入出力：平行四辺形，判定：ひし形
- 白地ノード（影なし），Yes/Noはグレー地のラベル
- 各関数を独立した1図とし，主たる流れを縦一直線で表す
- 文字が図形内に収まるよう各ノードの寸法を設定
生成対象（Arduino側のみ．Processing関連の既存図は対象外）:
  flow_button, flow_acc_update, flow_acc_read(readAccMagnitude),
  flow_recoveri2c, flow_pot, flow_roundrobin,
  flow_startramp, flow_changebpm, flow_stopramp,
  flow_displaybpm, flow_detectlight, flow_siki(loop), flow_kan(loop)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.lines import Line2D
import os

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
font_candidates = ['/System/Library/Fonts/ヒラギノ角ゴシック W2.ttc',
                   '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf']
font_path = next((fp for fp in font_candidates if os.path.exists(fp)), None)
from matplotlib.font_manager import FontProperties
jp = FontProperties(fname=font_path) if font_path else None

FS = 9
EC = '#3b3a4e'  # 枠線色（濃紺）


def _text(ax, x, y, text):
    ax.text(x, y, text, ha='center', va='center', fontsize=FS,
            fontproperties=jp, color='#2f2e41', zorder=4)


def pill(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle='round,pad=0.02,rounding_size=0.3',
                                fc='white', ec=EC, lw=1.2, zorder=2))
    _text(ax, x, y, text)


def proc(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle='square,pad=0.02',
                                fc='white', ec=EC, lw=1.2, zorder=2))
    _text(ax, x, y, text)


def io(ax, x, y, w, h, text, skew=0.28):
    pts = [(x - w / 2 + skew, y + h / 2), (x + w / 2 + skew, y + h / 2),
           (x + w / 2 - skew, y - h / 2), (x - w / 2 - skew, y - h / 2)]
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec=EC, lw=1.2, zorder=2))
    _text(ax, x, y, text)


def dec(ax, x, y, w, h, text):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec=EC, lw=1.2, zorder=2))
    _text(ax, x, y, text)


def lab(ax, x, y, text):
    ax.text(x, y, text, ha='center', va='center', fontsize=FS - 1,
            fontproperties=jp, color='#2f2e41', zorder=5,
            bbox=dict(facecolor='#d9d9d9', edgecolor='none',
                      boxstyle='square,pad=0.15'))


def edge(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.1, color=EC))


def poly(ax, pts):
    for i in range(len(pts) - 2):
        ax.add_line(Line2D([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                           color=EC, lw=1.1))
    ax.annotate('', xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle='->', lw=1.1, color=EC))


def line(ax, pts):
    for i in range(len(pts) - 1):
        ax.add_line(Line2D([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                           color=EC, lw=1.1))


def new_ax(w_in, h_in, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w_in, h_in))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUTDIR, name + '.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(OUTDIR, name + '.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(name, 'saved')


CX = 3.4   # 主流れのx座標
SX = 7.2   # 右側分岐のx座標

# ============================================================
# 1. button関数
# ============================================================
fig, ax = new_ax(6.2, 7.2, 9.0, 12.8)
pill(ax, CX, 12.2, 2.6, 0.7, '開始')
io(ax, CX, 11.0, 4.2, 1.0, 'input_PINの状態を\n読み取り')
dec(ax, CX, 9.1, 5.2, 2.3, '立下り検知？\n（前回HIGHかつ\n今回LOW）')
proc(ax, CX, 6.9, 5.4, 1.5, "isButtonPlayingに応じて\n'E'（演奏中）／'S'（停止中）\nを送信し，フラグを反転")
proc(ax, CX, 5.0, 4.6, 1.0, 'delay(300)：\nチャタリング防止')
proc(ax, CX, 3.3, 4.8, 1.0, '前回状態を更新\n(before_switch_status)')
pill(ax, CX, 1.7, 2.6, 0.7, '処理終了')
edge(ax, CX, 11.85, CX, 11.5)
edge(ax, CX, 10.5, CX, 10.05)
edge(ax, CX, 8.15, CX, 7.65); lab(ax, CX + 0.45, 7.9, 'Yes')
poly(ax, [(CX + 2.6, 9.1), (SX + 0.6, 9.1), (SX + 0.6, 3.3), (CX + 2.4, 3.3)])
lab(ax, SX - 0.9, 9.1, 'No')
edge(ax, CX, 6.15, CX, 5.5)
edge(ax, CX, 4.5, CX, 3.8)
edge(ax, CX, 2.8, CX, 2.05)
save(fig, 'flow_button')

# ============================================================
# 2. AccManager::update関数
# ============================================================
fig, ax = new_ax(6.2, 7.6, 9.0, 13.6)
pill(ax, CX, 13.0, 2.6, 0.7, '開始')
dec(ax, CX, 11.3, 5.4, 2.3, '前回サンプリングから\nACC_SAMPLE_INTERVAL\n経過？')
io(ax, CX, 9.4, 4.6, 1.0, 'readAccMagnitude()で\n合成加速度を取得')
proc(ax, CX, 8.0, 4.8, 1.0, '前回値との差分\ndiffを算出')
dec(ax, CX, 6.2, 5.6, 2.3, 'diff > accThreshold\nかつshakeInterval\n経過？')
proc(ax, CX, 4.2, 5.6, 1.4, '検知時刻を更新し，isStartedを反転．\nupdateShakedInfo()で\nフラグの立つ項目を送信')
proc(ax, CX, 2.7, 4.6, 0.7, '前回値lastAccValを更新')
pill(ax, CX, 1.2, 2.6, 0.7, '処理終了')
edge(ax, CX, 12.65, CX, 12.3)
edge(ax, CX, 10.35, CX, 9.95); lab(ax, CX + 0.45, 10.15, 'Yes')
poly(ax, [(CX + 2.7, 11.3), (SX + 0.7, 11.3), (SX + 0.7, 1.2), (CX + 1.4, 1.2)])
lab(ax, SX - 0.4, 11.3, 'No')
edge(ax, CX, 8.9, CX, 8.55)
edge(ax, CX, 7.5, CX, 7.2)
edge(ax, CX, 5.25, CX, 4.95); lab(ax, CX + 0.45, 5.1, 'Yes')
poly(ax, [(CX + 2.8, 6.2), (SX + 0.1, 6.2), (SX + 0.1, 2.7), (CX + 2.3, 2.7)])
lab(ax, SX - 0.9, 6.2, 'No')
edge(ax, CX, 3.5, CX, 3.1)
edge(ax, CX, 2.35, CX, 1.55)
save(fig, 'flow_acc_update')

# ============================================================
# 3. readAccMagnitude関数
# ============================================================
fig, ax = new_ax(6.6, 6.8, 9.4, 12.2)
pill(ax, CX, 11.6, 2.6, 0.7, '開始')
io(ax, CX, 10.4, 4.6, 1.0, 'DATAX0レジスタの\nアドレスを送信')
dec(ax, CX, 8.7, 4.2, 1.6, 'バス異常\n（NACK等）？')
io(ax, CX, 7.1, 4.6, 0.8, '6バイトの読み出しを要求')
dec(ax, CX, 5.4, 4.0, 1.6, '6バイト\n読み出せた？')
proc(ax, CX, 3.6, 5.2, 1.0, 'X・Y・Z軸の値を復元し\n合成加速度√(x²+y²+z²)を算出')
pill(ax, CX, 2.0, 3.4, 0.7, '合成加速度を返す')
proc(ax, SX + 0.3, 5.4, 3.4, 1.0, 'recoverI2C()で\nバスを復旧')
pill(ax, SX + 0.3, 2.0, 3.6, 0.9, '直前値lastAccVal\nを返す')
edge(ax, CX, 11.25, CX, 10.9)
edge(ax, CX, 9.9, CX, 9.5)
edge(ax, CX, 7.9, CX, 7.5); lab(ax, CX + 0.4, 7.7, 'No')
poly(ax, [(CX + 2.1, 8.7), (SX + 0.3, 8.7), (SX + 0.3, 5.9)])
lab(ax, SX - 0.9, 8.7, 'Yes')
edge(ax, CX, 6.7, CX, 6.2)
edge(ax, CX, 4.6, CX, 4.1); lab(ax, CX + 0.45, 4.35, 'Yes')
poly(ax, [(CX + 2.0, 5.4), (CX + 2.9, 5.4), (SX - 1.4, 5.4)])
lab(ax, CX + 2.5, 5.65, 'No')
edge(ax, CX, 3.1, CX, 2.35)
edge(ax, SX + 0.3, 4.9, SX + 0.3, 2.45)
save(fig, 'flow_acc_read')

# ============================================================
# 4. recoverI2C関数
# ============================================================
fig, ax = new_ax(5.4, 6.4, 8.0, 11.2)
Cx2 = 4.0
pill(ax, Cx2, 10.6, 2.6, 0.7, '開始')
proc(ax, Cx2, 9.4, 4.4, 0.8, 'Wire.end()でI2Cを停止')
proc(ax, Cx2, 7.9, 5.2, 1.0, 'SCL線を9回トグルし，スレーブ\nに握られたSDA線を解放')
proc(ax, Cx2, 6.4, 5.2, 1.0, 'STOP条件を生成（SCL=HIGH\n中にSDAをLOW→HIGH）')
proc(ax, Cx2, 4.9, 5.2, 1.0, 'Wire.begin()で再初期化し，\nADXL345を再設定')
pill(ax, Cx2, 3.5, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 10.25, Cx2, 9.8)
edge(ax, Cx2, 9.0, Cx2, 8.4)
edge(ax, Cx2, 7.4, Cx2, 6.9)
edge(ax, Cx2, 5.9, Cx2, 5.4)
edge(ax, Cx2, 4.4, Cx2, 3.85)
save(fig, 'flow_recoveri2c')

# ============================================================
# 5. PotManager::update関数（BPM系統）
# ============================================================
fig, ax = new_ax(6.6, 8.6, 9.4, 16.4)
pill(ax, CX, 15.8, 2.6, 0.7, '開始')
dec(ax, CX, 14.1, 5.4, 2.3, '前回サンプリングから\nSAMPLE_INTERVAL\n経過？')
io(ax, CX, 12.1, 5.0, 1.4, 'analogReadで新しい値を\n取得し，最古のサンプルと\n差し替え（移動合計を更新）')
proc(ax, CX, 10.7, 4.6, 0.7, '書き込み位置を更新')
dec(ax, CX, 9.2, 4.2, 1.6, 'バッファが一巡\n（満杯）した？')
proc(ax, CX, 7.6, 4.8, 1.0, '移動平均 =\n移動合計 / sampleSize')
proc(ax, CX, 6.1, 5.2, 1.0, 'calcStep()：4つの境界値と\nの比較で段階1〜5を算出')
dec(ax, CX, 4.5, 4.2, 1.6, '段階が前回から\n変化した？')
proc(ax, CX, 2.9, 4.6, 0.8, 'bpmFrag = true（送信予約）')
proc(ax, SX + 0.3, 2.9, 2.8, 1.0, '音量系統も\n同様に処理')
pill(ax, SX + 0.3, 1.2, 2.8, 0.7, '処理終了')
edge(ax, CX, 15.45, CX, 15.1)
edge(ax, CX, 13.15, CX, 12.8); lab(ax, CX + 0.45, 13.0, 'Yes')
poly(ax, [(CX + 2.7, 14.1), (SX + 1.9, 14.1), (SX + 1.9, 1.2), (SX + 1.75, 1.2)])
lab(ax, SX - 0.3, 14.1, 'No')
edge(ax, CX, 11.4, CX, 11.05)
edge(ax, CX, 10.35, CX, 10.0)
edge(ax, CX, 8.4, CX, 8.1); lab(ax, CX + 0.45, 8.25, 'Yes')
poly(ax, [(CX + 2.1, 9.2), (SX + 0.3, 9.2), (SX + 0.3, 3.4)])
lab(ax, SX - 0.8, 9.2, 'No')
edge(ax, CX, 7.1, CX, 6.6)
edge(ax, CX, 5.6, CX, 5.3)
edge(ax, CX, 3.7, CX, 3.3); lab(ax, CX + 0.45, 3.5, 'Yes')
poly(ax, [(CX - 2.1, 4.5), (0.6, 4.5), (0.6, 1.2), (SX - 1.1, 1.2)])
lab(ax, 1.0, 4.5, 'No')
poly(ax, [(CX + 2.3, 2.9), (SX - 1.3, 2.9)])
edge(ax, SX + 0.3, 2.4, SX + 0.3, 1.55)
save(fig, 'flow_pot')

# ============================================================
# 6. packetRoundRobin関数
# ============================================================
fig, ax = new_ax(6.0, 5.6, 8.8, 9.8)
pill(ax, CX, 9.2, 2.6, 0.7, '開始')
proc(ax, CX, 8.1, 3.0, 0.7, 'round = 0')
io(ax, CX, 6.7, 5.2, 1.0, '全ターゲットへ1回ずつ\nパケットを送信')
dec(ax, CX, 4.8, 4.0, 1.6, 'round < 2？\n（3周目以外）')
proc(ax, CX, 2.9, 4.6, 1.0, 'delay(20)：20 ms待機\nround = round + 1')
pill(ax, CX, 1.2, 2.6, 0.7, '処理終了')
edge(ax, CX, 8.85, CX, 8.45)
edge(ax, CX, 7.75, CX, 7.2)
edge(ax, CX, 6.2, CX, 5.6)
edge(ax, CX, 4.0, CX, 3.4); lab(ax, CX + 0.45, 3.7, 'Yes')
poly(ax, [(CX - 2.3, 2.9), (0.7, 2.9), (0.7, 6.7), (CX - 2.6, 6.7)])
poly(ax, [(CX + 2.0, 4.8), (SX, 4.8), (SX, 1.2), (CX + 1.4, 1.2)])
lab(ax, SX - 1.1, 4.8, 'No')
save(fig, 'flow_roundrobin')

# ============================================================
# 7-9. MotorControl 3関数（各々独立の図）
# ============================================================
fig, ax = new_ax(5.4, 5.8, 8.0, 10.2)
Cx2 = 4.0
pill(ax, Cx2, 9.6, 2.6, 0.7, '開始')
proc(ax, Cx2, 8.4, 5.0, 1.0, 'stepToNumber()：LUTから\npwmValue等を取得')
proc(ax, Cx2, 6.7, 5.2, 1.4, 'PWM出力を0からpwmValue\nまで5刻みで増加\n（各ステップ40 ms待機）')
io(ax, Cx2, 5.1, 3.8, 0.8, 'pwmValueを出力')
pill(ax, Cx2, 3.6, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 9.25, Cx2, 8.9)
edge(ax, Cx2, 7.9, Cx2, 7.4)
edge(ax, Cx2, 6.0, Cx2, 5.5)
edge(ax, Cx2, 4.7, Cx2, 3.95)
save(fig, 'flow_startramp')

fig, ax = new_ax(5.4, 5.8, 8.0, 10.2)
pill(ax, Cx2, 9.6, 2.6, 0.7, '開始')
proc(ax, Cx2, 8.4, 5.0, 1.0, 'stepToNumber()：LUTから\npwmValue等を取得')
proc(ax, Cx2, 6.8, 5.2, 1.0, 'updateStatus()：角速度ωと\n平均電圧V_averageを算出')
io(ax, Cx2, 5.3, 4.6, 0.8, 'pwmValueを即座に出力')
pill(ax, Cx2, 3.8, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 9.25, Cx2, 8.9)
edge(ax, Cx2, 7.9, Cx2, 7.3)
edge(ax, Cx2, 6.3, Cx2, 5.7)
edge(ax, Cx2, 4.9, Cx2, 4.15)
save(fig, 'flow_changebpm')

fig, ax = new_ax(5.4, 5.2, 8.0, 9.0)
pill(ax, Cx2, 8.4, 2.6, 0.7, '開始')
proc(ax, Cx2, 6.9, 5.2, 1.4, 'PWM出力をpwmValueから\n0まで5刻みで減少\n（各ステップ40 ms待機）')
io(ax, Cx2, 5.3, 3.8, 0.8, '0を出力（停止）')
pill(ax, Cx2, 3.8, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 8.05, Cx2, 7.6)
edge(ax, Cx2, 6.2, Cx2, 5.7)
edge(ax, Cx2, 4.9, Cx2, 4.15)
save(fig, 'flow_stopramp')

# ============================================================
# 10. displayBPM関数
# ============================================================
fig, ax = new_ax(6.2, 8.0, 9.0, 14.6)
pill(ax, CX, 14.0, 2.6, 0.7, '開始')
dec(ax, CX, 12.5, 4.2, 1.6, '段階番号が\n1〜5の範囲内？')
proc(ax, CX, 11.1, 5.0, 0.8, 'bpm = bpmTable[stepNumber-1]')
proc(ax, CX, 9.9, 4.6, 0.8, 'フレームバッファを初期化')
proc(ax, CX, 8.6, 5.2, 1.0, 'BPM値を各桁に分割\n（100以上：3桁，10以上：2桁）')
proc(ax, CX, 7.1, 5.2, 1.0, '表示幅（桁数×3+桁間1）から\n中央揃えの開始位置を算出')
proc(ax, CX, 5.6, 5.2, 1.0, '各桁をdrawDigit()で描画\n（3×5フォント配列と照合）')
io(ax, CX, 4.1, 5.0, 1.0, 'uint32_t[3]へビットパックし\nmatrix.loadFrame()で表示')
pill(ax, CX, 2.5, 2.6, 0.7, '処理終了')
edge(ax, CX, 13.65, CX, 13.3)
edge(ax, CX, 11.7, CX, 11.5); lab(ax, CX + 0.45, 11.6, 'Yes')
poly(ax, [(CX + 2.1, 12.5), (SX + 0.5, 12.5), (SX + 0.5, 2.5), (CX + 1.4, 2.5)])
lab(ax, SX - 0.7, 12.5, 'No')
edge(ax, CX, 10.7, CX, 10.3)
edge(ax, CX, 9.5, CX, 9.1)
edge(ax, CX, 8.1, CX, 7.6)
edge(ax, CX, 6.6, CX, 6.1)
edge(ax, CX, 5.1, CX, 4.6)
edge(ax, CX, 3.6, CX, 2.85)
save(fig, 'flow_displaybpm')

# ============================================================
# 11. detectLight関数
# ============================================================
fig, ax = new_ax(7.6, 8.8, 11.0, 16.0)
pill(ax, CX, 15.4, 2.6, 0.7, '開始')
dec(ax, CX, 13.7, 4.0, 1.6, '起動時較正\n完了？')
dec(ax, CX, 11.6, 4.4, 1.6, '照射解除待ち\n(waitingForRelease)？')
proc(ax, CX, 9.5, 5.4, 1.4, '非照射中：baselineを追従更新\n（最小値，または31/32の\n重みで平滑化）')
dec(ax, CX, 7.3, 4.8, 1.6, '非照射中 かつ v が\nonThreshold以上？')
dec(ax, CX, 5.1, 4.8, 1.6, '照射中 かつ v が\noffThreshold以下？')
proc(ax, CX, 3.0, 5.4, 1.2, '立ち下がり：registerPeak()で\nピーク履歴としきい値を更新')
pill(ax, CX, 1.3, 3.2, 0.7, 'falseを返す')
proc(ax, 8.8, 13.7, 3.4, 1.5, '最小値を探索し\nbaselineを更新\n（1秒経過で較正完了）')
proc(ax, 8.8, 11.6, 3.4, 1.5, '非照射になったら\nbaselineを再設定し\n解除待ちを終了')
pill(ax, 8.8, 7.3, 3.4, 1.0, '立ち上がり検知：\ntrueを返す')
edge(ax, CX, 15.05, CX, 14.5)
edge(ax, CX, 12.9, CX, 12.4); lab(ax, CX + 0.4, 12.65, 'Yes')
poly(ax, [(CX + 2.0, 13.7), (7.05, 13.7)])
lab(ax, CX + 2.7, 13.95, 'No（較正中）')
edge(ax, CX, 10.8, CX, 10.2); lab(ax, CX + 0.4, 10.5, 'No')
poly(ax, [(CX + 2.2, 11.6), (7.05, 11.6)])
lab(ax, CX + 2.8, 11.85, 'Yes')
edge(ax, CX, 8.8, CX, 8.1)
edge(ax, CX, 6.5, CX, 5.9); lab(ax, CX + 0.4, 6.2, 'No')
poly(ax, [(CX + 2.4, 7.3), (7.05, 7.3)])
lab(ax, CX + 2.8, 7.55, 'Yes')
edge(ax, CX, 4.3, CX, 3.6); lab(ax, CX + 0.4, 3.95, 'Yes')
poly(ax, [(CX - 2.4, 5.1), (0.6, 5.1), (0.6, 1.3), (CX - 1.6, 1.3)])
lab(ax, 1.0, 5.1, 'No')
edge(ax, CX, 2.4, CX, 1.65)
# 右側の箱からの合流（縦の合流線1本にまとめる）
line(ax, [(8.8, 12.95), (8.8, 12.7), (10.6, 12.7)])
line(ax, [(8.8, 10.85), (8.8, 10.6), (10.6, 10.6)])
poly(ax, [(10.6, 12.7), (10.6, 1.3), (CX + 1.6, 1.3)])
save(fig, 'flow_detectlight')

# ============================================================
# 12. 指揮デバイス loop関数
# ============================================================
fig, ax = new_ax(5.6, 6.2, 8.0, 10.6)
Cx2 = 4.0
pill(ax, Cx2, 10.0, 2.8, 0.7, 'loop() 開始')
proc(ax, Cx2, 8.7, 5.4, 1.0, 'button()：ボタン入力の判定と\n演奏開始・終了信号の送信')
proc(ax, Cx2, 7.2, 5.4, 1.0, 'pot.update()：可変抵抗器の\nサンプリングと段階算出')
proc(ax, Cx2, 5.7, 5.4, 1.0, 'acc.update()：振り動作の検知\nとBPM・音量情報の送信')
pill(ax, Cx2, 4.3, 3.2, 0.7, 'loop() 先頭へ戻る')
edge(ax, Cx2, 9.65, Cx2, 9.2)
edge(ax, Cx2, 8.2, Cx2, 7.7)
edge(ax, Cx2, 6.7, Cx2, 6.2)
edge(ax, Cx2, 5.2, Cx2, 4.65)
save(fig, 'flow_siki')

# ============================================================
# 13. 中継機デバイス loop関数
# ============================================================
fig, ax = new_ax(7.4, 8.8, 10.8, 15.6)
pill(ax, CX, 15.0, 2.8, 0.7, 'loop() 開始')
dec(ax, CX, 13.4, 3.8, 1.6, 'UDPパケット\n到着？')
io(ax, CX, 11.5, 5.0, 1.1, 'ヘッダ（1バイト目）と\nペイロード（2バイト目）を\n読み取り')
dec(ax, CX, 9.7, 3.4, 1.3, "ヘッダ = 'S'？")
dec(ax, CX, 7.7, 3.4, 1.3, "ヘッダ = 'B'？")
dec(ax, CX, 5.7, 3.4, 1.3, "ヘッダ = 'E'？")
proc(ax, CX, 3.8, 4.6, 0.9, '想定外のヘッダを無視')
pill(ax, CX, 2.2, 3.4, 0.7, 'loop() 先頭へ戻る')
proc(ax, 8.2, 9.7, 3.2, 1.1, 'startRamp()\ndisplayBPM()')
proc(ax, 8.2, 7.7, 3.8, 1.6, '演奏中のみ\nchangeBPM()と\ndisplayBPM()を実行\n（演奏前は無視）')
proc(ax, 8.2, 5.7, 3.2, 1.1, 'stopRamp()\nclearDisplay()')
edge(ax, CX, 14.65, CX, 14.2)
edge(ax, CX, 12.6, CX, 12.1); lab(ax, CX + 0.4, 12.35, 'Yes')
poly(ax, [(CX - 1.9, 13.4), (0.6, 13.4), (0.6, 2.2), (CX - 1.7, 2.2)])
lab(ax, 1.0, 13.4, 'No')
edge(ax, CX, 10.9, CX, 10.35)
edge(ax, CX, 9.05, CX, 8.35); lab(ax, CX + 0.4, 8.7, 'No')
poly(ax, [(CX + 1.7, 9.7), (6.6, 9.7)])
lab(ax, CX + 2.3, 9.95, 'Yes')
edge(ax, CX, 7.05, CX, 6.35); lab(ax, CX + 0.4, 6.7, 'No')
poly(ax, [(CX + 1.7, 7.7), (6.3, 7.7)])
lab(ax, CX + 2.3, 7.95, 'Yes')
edge(ax, CX, 5.05, CX, 4.25); lab(ax, CX + 0.4, 4.65, 'No')
poly(ax, [(CX + 1.7, 5.7), (6.6, 5.7)])
lab(ax, CX + 2.3, 5.95, 'Yes')
edge(ax, CX, 3.35, CX, 2.55)
# 右側3箱からの合流（縦の合流線1本にまとめる）
line(ax, [(8.2, 9.15), (8.2, 8.9), (10.3, 8.9)])
line(ax, [(8.2, 6.9), (8.2, 6.7), (10.3, 6.7)])
line(ax, [(8.2, 5.15), (8.2, 4.95), (10.3, 4.95)])
poly(ax, [(10.3, 8.9), (10.3, 2.2), (CX + 1.7, 2.2)])
save(fig, 'flow_kan')
