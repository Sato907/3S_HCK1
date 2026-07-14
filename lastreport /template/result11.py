#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関数別フローチャート生成スクリプト（図35・図36の形式に統一した版）
- 端子：角丸，処理：矩形，入出力：平行四辺形，判定：ひし形
- 白地・影付きノード，Yes/Noはグレー地のラベル
- 各関数を独立した1図とし，主たる流れを縦一直線で表す
生成対象:
  flow_button, flow_acc_update, flow_acc_read(readAccMagnitude),
  flow_recoveri2c, flow_pot, flow_roundrobin,
  flow_startramp, flow_changebpm, flow_stopramp,
  flow_displaybpm, flow_detectlight, flow_siki(loop), flow_kan(loop)
※ 本スクリプトの出力は result10.py（旧様式）を置き換える．
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
EC = '#3b3a4e'      # 枠線色（濃紺）
SHADOW = '#c9c9d4'  # 影色
SDX, SDY = 0.06, -0.06


def _text(ax, x, y, text):
    ax.text(x, y, text, ha='center', va='center', fontsize=FS,
            fontproperties=jp, color='#2f2e41', zorder=4)


def pill(ax, x, y, w, h, text):
    for dx, dy, fc, z in ((SDX, SDY, SHADOW, 1), (0, 0, 'white', 2)):
        ax.add_patch(FancyBboxPatch((x - w / 2 + dx, y - h / 2 + dy), w, h,
                                    boxstyle='round,pad=0.02,rounding_size=0.3',
                                    fc=fc, ec='none' if z == 1 else EC, lw=1.2, zorder=z))
    _text(ax, x, y, text)


def proc(ax, x, y, w, h, text):
    for dx, dy, fc, z in ((SDX, SDY, SHADOW, 1), (0, 0, 'white', 2)):
        ax.add_patch(FancyBboxPatch((x - w / 2 + dx, y - h / 2 + dy), w, h,
                                    boxstyle='square,pad=0.02',
                                    fc=fc, ec='none' if z == 1 else EC, lw=1.2, zorder=z))
    _text(ax, x, y, text)


def io(ax, x, y, w, h, text, skew=0.28):
    pts = [(x - w / 2 + skew, y + h / 2), (x + w / 2 + skew, y + h / 2),
           (x + w / 2 - skew, y - h / 2), (x - w / 2 - skew, y - h / 2)]
    ax.add_patch(Polygon([(px + SDX, py + SDY) for px, py in pts],
                         closed=True, fc=SHADOW, ec='none', zorder=1))
    ax.add_patch(Polygon(pts, closed=True, fc='white', ec=EC, lw=1.2, zorder=2))
    _text(ax, x, y, text)


def dec(ax, x, y, w, h, text):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    ax.add_patch(Polygon([(px + SDX, py + SDY) for px, py in pts],
                         closed=True, fc=SHADOW, ec='none', zorder=1))
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
dec(ax, CX, 9.1, 4.6, 1.9, '立下り検知？\n（前回HIGHかつ\n今回LOW）')
proc(ax, CX, 6.9, 5.4, 1.5, "isButtonPlayingに応じて\n'E'（演奏中）／'S'（停止中）\nを送信し，フラグを反転")
proc(ax, CX, 5.0, 4.6, 1.0, 'delay(300)：\nチャタリング防止')
proc(ax, CX, 3.3, 4.8, 1.0, '前回状態を更新\n(before_switch_status)')
pill(ax, CX, 1.7, 2.6, 0.7, '処理終了')
edge(ax, CX, 11.85, CX, 11.5)
edge(ax, CX, 10.5, CX, 10.05)
edge(ax, CX, 8.15, CX, 7.65); lab(ax, CX + 0.45, 7.9, 'Yes')
poly(ax, [(CX + 2.3, 9.1), (SX + 0.5, 9.1), (SX + 0.5, 3.3), (CX + 2.4, 3.3)])
lab(ax, SX - 0.9, 9.1, 'No')
edge(ax, CX, 6.15, CX, 5.5)
edge(ax, CX, 4.5, CX, 3.8)
edge(ax, CX, 2.8, CX, 2.05)
save(fig, 'flow_button')

# ============================================================
# 2. AccManager::update関数
# ============================================================
fig, ax = new_ax(6.2, 7.0, 9.0, 12.6)
pill(ax, CX, 12.0, 2.6, 0.7, '開始')
dec(ax, CX, 10.4, 4.6, 1.5, '前回サンプリングから\nACC_SAMPLE_INTERVAL\n経過？')
io(ax, CX, 8.6, 4.6, 0.8, 'readAccMagnitude()で\n合成加速度を取得')
proc(ax, CX, 7.2, 4.8, 0.8, '前回値との差分\ndiffを算出')
dec(ax, CX, 5.4, 4.8, 1.5, 'diff > accThreshold\nかつshakeInterval\n経過？')
proc(ax, CX, 3.5, 5.4, 1.0, '検知時刻を更新し，isStartedを反転．\nupdateShakedInfo()でフラグの\n立つ項目を送信')
proc(ax, CX, 2.1, 4.6, 0.7, '前回値lastAccValを更新')
pill(ax, CX, 0.8, 2.6, 0.7, '処理終了')
edge(ax, CX, 11.65, CX, 11.15)
edge(ax, CX, 9.65, CX, 9.0); lab(ax, CX + 0.45, 9.35, 'Yes')
poly(ax, [(CX + 2.3, 10.4), (SX + 0.4, 10.4), (SX + 0.4, 0.8), (CX + 1.4, 0.8)])
lab(ax, SX - 0.8, 10.4, 'No')
edge(ax, CX, 8.2, CX, 7.6)
edge(ax, CX, 6.8, CX, 6.15)
edge(ax, CX, 4.65, CX, 4.0); lab(ax, CX + 0.45, 4.35, 'Yes')
poly(ax, [(CX + 2.4, 5.4), (SX, 5.4), (SX, 2.1), (CX + 2.3, 2.1)])
lab(ax, SX - 1.0, 5.4, 'No')
edge(ax, CX, 3.0, CX, 2.45)
edge(ax, CX, 1.75, CX, 1.15)
save(fig, 'flow_acc_update')

# ============================================================
# 3. readAccMagnitude関数
# ============================================================
fig, ax = new_ax(6.6, 6.6, 9.4, 11.6)
pill(ax, CX, 11.0, 2.6, 0.7, '開始')
io(ax, CX, 9.8, 4.6, 0.8, 'DATAX0レジスタの\nアドレスを送信')
dec(ax, CX, 8.2, 4.2, 1.4, 'バス異常\n（NACK等）？')
io(ax, CX, 6.6, 4.4, 0.7, '6バイトの読み出しを要求')
dec(ax, CX, 5.0, 4.0, 1.4, '6バイト\n読み出せた？')
proc(ax, CX, 3.2, 5.0, 0.9, 'X・Y・Z軸の値を復元し\n合成加速度√(x²+y²+z²)を算出')
pill(ax, CX, 1.7, 3.4, 0.7, '合成加速度を返す')
proc(ax, SX + 0.3, 5.0, 3.4, 0.9, 'recoverI2C()で\nバスを復旧')
pill(ax, SX + 0.3, 1.7, 3.6, 0.8, '直前値lastAccVal\nを返す')
edge(ax, CX, 10.65, CX, 10.2)
edge(ax, CX, 9.4, CX, 8.9)
edge(ax, CX, 7.5, CX, 6.95); lab(ax, CX + 0.4, 7.25, 'No')
poly(ax, [(CX + 2.1, 8.2), (SX + 0.3, 8.2), (SX + 0.3, 5.45)])
lab(ax, SX - 0.9, 8.2, 'Yes')
edge(ax, CX, 6.25, CX, 5.7)
edge(ax, CX, 4.3, CX, 3.65); lab(ax, CX + 0.45, 4.0, 'Yes')
poly(ax, [(CX + 2.0, 5.0), (CX + 2.9, 5.0), (SX - 1.4, 5.0)])
lab(ax, CX + 2.5, 5.25, 'No')
edge(ax, CX, 2.75, CX, 2.05)
edge(ax, SX + 0.3, 4.55, SX + 0.3, 2.1)
save(fig, 'flow_acc_read')

# ============================================================
# 4. recoverI2C関数
# ============================================================
fig, ax = new_ax(5.4, 6.2, 8.0, 10.8)
Cx2 = 4.0
pill(ax, Cx2, 10.2, 2.6, 0.7, '開始')
proc(ax, Cx2, 9.0, 4.2, 0.7, 'Wire.end()でI2Cを停止')
proc(ax, Cx2, 7.6, 5.0, 0.9, 'SCL線を9回トグルし，スレーブに\n握られたSDA線を解放')
proc(ax, Cx2, 6.1, 5.0, 0.9, 'STOP条件を生成（SCL=HIGH中に\nSDAをLOW→HIGH）')
proc(ax, Cx2, 4.6, 5.0, 0.9, 'Wire.begin()で再初期化し，\nADXL345を再設定')
pill(ax, Cx2, 3.2, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 9.85, Cx2, 9.35)
edge(ax, Cx2, 8.65, Cx2, 8.05)
edge(ax, Cx2, 7.15, Cx2, 6.55)
edge(ax, Cx2, 5.65, Cx2, 5.05)
edge(ax, Cx2, 4.15, Cx2, 3.55)
save(fig, 'flow_recoveri2c')

# ============================================================
# 5. PotManager::update関数（BPM系統）
# ============================================================
fig, ax = new_ax(6.6, 8.0, 9.4, 14.6)
pill(ax, CX, 14.0, 2.6, 0.7, '開始')
dec(ax, CX, 12.4, 4.6, 1.5, '前回サンプリングから\nSAMPLE_INTERVAL\n経過？')
io(ax, CX, 10.6, 4.8, 0.9, 'analogReadで新しい値を取得し，\n最古のサンプルと差し替え\n（移動合計を更新）')
proc(ax, CX, 9.2, 4.6, 0.7, '書き込み位置を更新')
dec(ax, CX, 7.7, 4.2, 1.4, 'バッファが一巡\n（満杯）した？')
proc(ax, CX, 6.1, 4.8, 0.8, '移動平均 =\n移動合計 / sampleSize')
proc(ax, CX, 4.7, 5.0, 0.8, 'calcStep()：4つの境界値との\n比較で段階1〜5を算出')
dec(ax, CX, 3.1, 4.0, 1.4, '段階が前回から\n変化した？')
proc(ax, CX, 1.5, 4.4, 0.7, 'bpmFrag = true（送信予約）')
proc(ax, SX + 0.3, 1.5, 3.2, 0.8, '音量系統も\n同様に処理')
pill(ax, SX + 0.3, 0.2, 2.6, 0.6, '処理終了')
edge(ax, CX, 13.65, CX, 13.15)
edge(ax, CX, 11.65, CX, 11.05); lab(ax, CX + 0.45, 11.35, 'Yes')
poly(ax, [(CX + 2.3, 12.4), (SX + 1.6, 12.4), (SX + 1.6, 0.2), (SX + 1.6, 0.2), (SX + 1.6 - 0.0, 0.2), (SX + 1.3, 0.2)])
lab(ax, SX - 0.5, 12.4, 'No')
edge(ax, CX, 10.15, CX, 9.55)
edge(ax, CX, 8.85, CX, 8.4)
edge(ax, CX, 7.0, CX, 6.5); lab(ax, CX + 0.45, 6.75, 'Yes')
poly(ax, [(CX + 2.1, 7.7), (SX + 0.3, 7.7), (SX + 0.3, 1.9)])
lab(ax, SX - 0.8, 7.7, 'No')
edge(ax, CX, 5.7, CX, 5.1)
edge(ax, CX, 4.3, CX, 3.8)
edge(ax, CX, 2.4, CX, 1.85); lab(ax, CX + 0.45, 2.15, 'Yes')
poly(ax, [(CX - 2.0, 3.1), (0.6, 3.1), (0.6, 0.2), (SX - 0.7, 0.2)])
lab(ax, 1.0, 3.1, 'No')
poly(ax, [(CX + 2.2, 1.5), (SX - 1.3, 1.5)])
edge(ax, SX + 0.3, 1.1, SX + 0.3, 0.5)
save(fig, 'flow_pot')

# ============================================================
# 6. packetRoundRobin関数
# ============================================================
fig, ax = new_ax(6.0, 5.4, 8.8, 9.4)
pill(ax, CX, 8.8, 2.6, 0.7, '開始')
proc(ax, CX, 7.7, 3.0, 0.7, 'round = 0')
io(ax, CX, 6.3, 5.2, 0.9, '全ターゲットへ1回ずつ\nパケットを送信')
dec(ax, CX, 4.5, 4.0, 1.4, 'round < 2？\n（3周目以外）')
proc(ax, CX, 2.8, 4.4, 0.8, 'delay(20)：20 ms待機\nround = round + 1')
pill(ax, CX, 1.2, 2.6, 0.7, '処理終了')
edge(ax, CX, 8.45, CX, 8.05)
edge(ax, CX, 7.35, CX, 6.75)
edge(ax, CX, 5.85, CX, 5.2)
edge(ax, CX, 3.8, CX, 3.2); lab(ax, CX + 0.45, 3.5, 'Yes')
poly(ax, [(CX - 2.2, 2.8), (0.7, 2.8), (0.7, 6.3), (CX - 2.6, 6.3)])
poly(ax, [(CX + 2.0, 4.5), (SX, 4.5), (SX, 1.2), (CX + 1.4, 1.2)])
lab(ax, SX - 1.1, 4.5, 'No')
save(fig, 'flow_roundrobin')

# ============================================================
# 7-9. MotorControl 3関数（各々独立の図）
# ============================================================
fig, ax = new_ax(5.4, 5.6, 8.0, 9.8)
Cx2 = 4.0
pill(ax, Cx2, 9.2, 2.6, 0.7, '開始')
proc(ax, Cx2, 8.0, 5.0, 0.9, 'stepToNumber()：LUTから\npwmValue等を取得')
proc(ax, Cx2, 6.4, 5.0, 1.1, 'PWM出力を0からpwmValueまで\n5刻みで増加\n（各ステップ40 ms待機）')
io(ax, Cx2, 4.9, 3.8, 0.7, 'pwmValueを出力')
pill(ax, Cx2, 3.5, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 8.85, Cx2, 8.45)
edge(ax, Cx2, 7.55, Cx2, 6.95)
edge(ax, Cx2, 5.85, Cx2, 5.25)
edge(ax, Cx2, 4.55, Cx2, 3.85)
save(fig, 'flow_startramp')

fig, ax = new_ax(5.4, 5.6, 8.0, 9.8)
pill(ax, Cx2, 9.2, 2.6, 0.7, '開始')
proc(ax, Cx2, 8.0, 5.0, 0.9, 'stepToNumber()：LUTから\npwmValue等を取得')
proc(ax, Cx2, 6.4, 5.0, 1.1, 'updateStatus()：角速度ωと\n平均電圧V_averageを算出')
io(ax, Cx2, 4.9, 4.6, 0.7, 'pwmValueを即座に出力')
pill(ax, Cx2, 3.5, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 8.85, Cx2, 8.45)
edge(ax, Cx2, 7.55, Cx2, 6.95)
edge(ax, Cx2, 5.85, Cx2, 5.25)
edge(ax, Cx2, 4.55, Cx2, 3.85)
save(fig, 'flow_changebpm')

fig, ax = new_ax(5.4, 5.0, 8.0, 8.6)
pill(ax, Cx2, 8.0, 2.6, 0.7, '開始')
proc(ax, Cx2, 6.7, 5.0, 1.1, 'PWM出力をpwmValueから0まで\n5刻みで減少\n（各ステップ40 ms待機）')
io(ax, Cx2, 5.2, 3.8, 0.7, '0を出力（停止）')
pill(ax, Cx2, 3.8, 2.6, 0.7, '処理終了')
edge(ax, Cx2, 7.65, Cx2, 7.25)
edge(ax, Cx2, 6.15, Cx2, 5.55)
edge(ax, Cx2, 4.85, Cx2, 4.15)
save(fig, 'flow_stopramp')

# ============================================================
# 10. displayBPM関数
# ============================================================
fig, ax = new_ax(6.2, 7.6, 9.0, 13.6)
pill(ax, CX, 13.0, 2.6, 0.7, '開始')
dec(ax, CX, 11.5, 4.0, 1.4, '段階番号が\n1〜5の範囲内？')
proc(ax, CX, 10.0, 4.8, 0.7, 'bpm = bpmTable[stepNumber-1]')
proc(ax, CX, 8.8, 4.4, 0.7, 'フレームバッファを初期化')
proc(ax, CX, 7.5, 5.0, 0.8, 'BPM値を各桁に分割\n（100以上：3桁，10以上：2桁）')
proc(ax, CX, 6.1, 5.0, 0.8, '表示幅（桁数×3+桁間1）から\n中央揃えの開始位置を算出')
proc(ax, CX, 4.7, 5.0, 0.8, '各桁をdrawDigit()で描画\n（3×5フォント配列と照合）')
io(ax, CX, 3.3, 4.8, 0.8, 'uint32_t[3]へビットパックし\nmatrix.loadFrame()で表示')
pill(ax, CX, 1.9, 2.6, 0.7, '処理終了')
edge(ax, CX, 12.65, CX, 12.2)
edge(ax, CX, 10.8, CX, 10.35); lab(ax, CX + 0.45, 10.6, 'Yes')
poly(ax, [(CX + 2.0, 11.5), (SX + 0.3, 11.5), (SX + 0.3, 1.9), (CX + 1.4, 1.9)])
lab(ax, SX - 0.8, 11.5, 'No')
edge(ax, CX, 9.65, CX, 9.15)
edge(ax, CX, 8.45, CX, 7.9)
edge(ax, CX, 7.1, CX, 6.5)
edge(ax, CX, 5.7, CX, 5.1)
edge(ax, CX, 4.3, CX, 3.7)
edge(ax, CX, 2.9, CX, 2.25)
save(fig, 'flow_displaybpm')

# ============================================================
# 11. detectLight関数
# ============================================================
fig, ax = new_ax(7.6, 8.6, 11.0, 15.6)
pill(ax, CX, 15.0, 2.6, 0.7, '開始')
dec(ax, CX, 13.3, 4.0, 1.6, '起動時較正\n完了？')
dec(ax, CX, 11.2, 4.4, 1.6, '照射解除待ち\n(waitingForRelease)？')
proc(ax, CX, 9.2, 5.4, 1.2, '非照射中：baselineを追従更新\n（最小値，または31/32の\n重みで平滑化）')
dec(ax, CX, 7.1, 4.8, 1.6, '非照射中 かつ v が\nonThreshold以上？')
dec(ax, CX, 4.9, 4.8, 1.6, '照射中 かつ v が\noffThreshold以下？')
proc(ax, CX, 2.9, 5.4, 1.2, '立ち下がり：registerPeak()で\nピーク履歴としきい値を更新')
pill(ax, CX, 1.2, 3.2, 0.7, 'falseを返す')
proc(ax, 8.8, 13.3, 3.4, 1.5, '最小値を探索し\nbaselineを更新\n（1秒経過で較正完了）')
proc(ax, 8.8, 11.2, 3.4, 1.5, '非照射になったら\nbaselineを再設定し\n解除待ちを終了')
pill(ax, 8.8, 7.1, 3.4, 1.0, '立ち上がり検知：\ntrueを返す')
edge(ax, CX, 14.65, CX, 14.1)
edge(ax, CX, 12.5, CX, 12.0); lab(ax, CX + 0.4, 12.25, 'Yes')
poly(ax, [(CX + 2.0, 13.3), (7.05, 13.3)])
lab(ax, CX + 2.7, 13.55, 'No（較正中）')
edge(ax, CX, 10.4, CX, 9.8); lab(ax, CX + 0.4, 10.1, 'No')
poly(ax, [(CX + 2.2, 11.2), (7.05, 11.2)])
lab(ax, CX + 2.8, 11.45, 'Yes')
edge(ax, CX, 8.6, CX, 7.9)
edge(ax, CX, 6.3, CX, 5.7); lab(ax, CX + 0.4, 6.0, 'No')
poly(ax, [(CX + 2.4, 7.1), (7.05, 7.1)])
lab(ax, CX + 2.8, 7.35, 'Yes')
edge(ax, CX, 4.1, CX, 3.5); lab(ax, CX + 0.4, 3.8, 'Yes')
poly(ax, [(CX - 2.4, 4.9), (0.6, 4.9), (0.6, 1.2), (CX - 1.6, 1.2)])
lab(ax, 1.0, 4.9, 'No')
edge(ax, CX, 2.3, CX, 1.55)
# 右側の箱からの合流（縦の合流線1本にまとめる）
ax.add_line(Line2D([8.8, 8.8], [12.55, 12.3], color=EC, lw=1.1))
ax.add_line(Line2D([8.8, 10.6], [12.3, 12.3], color=EC, lw=1.1))
ax.add_line(Line2D([8.8, 8.8], [10.45, 10.2], color=EC, lw=1.1))
ax.add_line(Line2D([8.8, 10.6], [10.2, 10.2], color=EC, lw=1.1))
poly(ax, [(10.6, 12.3), (10.6, 1.2), (CX + 1.6, 1.2)])
save(fig, 'flow_detectlight')

# ============================================================
# 12. 指揮デバイス loop関数
# ============================================================
fig, ax = new_ax(5.6, 5.8, 8.0, 10.0)
Cx2 = 4.0
pill(ax, Cx2, 9.4, 2.8, 0.7, 'loop() 開始')
proc(ax, Cx2, 8.2, 5.2, 0.8, 'button()：ボタン入力の判定と\n演奏開始・終了信号の送信')
proc(ax, Cx2, 6.7, 5.2, 0.8, 'pot.update()：可変抵抗器の\nサンプリングと段階算出')
proc(ax, Cx2, 5.2, 5.2, 0.8, 'acc.update()：振り動作の検知と\nBPM・音量情報の送信')
pill(ax, Cx2, 3.8, 3.2, 0.7, 'loop() 先頭へ戻る')
edge(ax, Cx2, 9.05, Cx2, 8.6)
edge(ax, Cx2, 7.8, Cx2, 7.1)
edge(ax, Cx2, 6.3, Cx2, 5.6)
edge(ax, Cx2, 4.8, Cx2, 4.15)
save(fig, 'flow_siki')

# ============================================================
# 13. 中継機デバイス loop関数
# ============================================================
fig, ax = new_ax(7.4, 8.6, 10.8, 15.2)
pill(ax, CX, 14.6, 2.8, 0.7, 'loop() 開始')
dec(ax, CX, 13.0, 3.8, 1.6, 'UDPパケット\n到着？')
io(ax, CX, 11.2, 4.8, 1.0, 'ヘッダ（1バイト目）と\nペイロード（2バイト目）を読み取り')
dec(ax, CX, 9.5, 3.4, 1.3, "ヘッダ = 'S'？")
dec(ax, CX, 7.5, 3.4, 1.3, "ヘッダ = 'B'？")
dec(ax, CX, 5.5, 3.4, 1.3, "ヘッダ = 'E'？")
proc(ax, CX, 3.6, 4.6, 0.9, '想定外のヘッダを無視')
pill(ax, CX, 2.0, 3.4, 0.7, 'loop() 先頭へ戻る')
proc(ax, 8.2, 9.5, 3.0, 1.1, 'startRamp()\ndisplayBPM()')
proc(ax, 8.2, 7.5, 3.2, 1.4, '演奏中のみ\nchangeBPM()とdisplayBPM()\n（演奏前は無視）')
proc(ax, 8.2, 5.5, 3.0, 1.1, 'stopRamp()\nclearDisplay()')
edge(ax, CX, 14.25, CX, 13.8)
edge(ax, CX, 12.2, CX, 11.7); lab(ax, CX + 0.4, 11.95, 'Yes')
poly(ax, [(CX - 1.9, 13.0), (0.6, 13.0), (0.6, 2.0), (CX - 1.7, 2.0)])
lab(ax, 1.0, 13.0, 'No')
edge(ax, CX, 10.7, CX, 10.15)
edge(ax, CX, 8.85, CX, 8.15); lab(ax, CX + 0.4, 8.5, 'No')
poly(ax, [(CX + 1.7, 9.5), (6.7, 9.5)])
lab(ax, CX + 2.3, 9.75, 'Yes')
edge(ax, CX, 6.85, CX, 6.15); lab(ax, CX + 0.4, 6.5, 'No')
poly(ax, [(CX + 1.7, 7.5), (6.6, 7.5)])
lab(ax, CX + 2.3, 7.75, 'Yes')
edge(ax, CX, 4.85, CX, 4.05); lab(ax, CX + 0.4, 4.45, 'No')
poly(ax, [(CX + 1.7, 5.5), (6.7, 5.5)])
lab(ax, CX + 2.3, 5.75, 'Yes')
edge(ax, CX, 3.15, CX, 2.35)
# 右側3箱からの合流（縦の合流線1本にまとめる）
ax.add_line(Line2D([8.2, 8.2], [8.95, 8.7], color=EC, lw=1.1))
ax.add_line(Line2D([8.2, 10.2], [8.7, 8.7], color=EC, lw=1.1))
ax.add_line(Line2D([8.2, 8.2], [6.8, 6.6], color=EC, lw=1.1))
ax.add_line(Line2D([8.2, 10.2], [6.6, 6.6], color=EC, lw=1.1))
ax.add_line(Line2D([8.2, 8.2], [4.95, 4.75], color=EC, lw=1.1))
ax.add_line(Line2D([8.2, 10.2], [4.75, 4.75], color=EC, lw=1.1))
poly(ax, [(10.2, 8.7), (10.2, 2.0), (CX + 1.7, 2.0)])
save(fig, 'flow_kan')
