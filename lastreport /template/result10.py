#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関数別フローチャート生成スクリプト（付録のプログラム全文に基づく）
- flow_button.pdf      : button関数（指揮デバイス）
- flow_acc_update.pdf  : AccManager::update関数
- flow_acc_read.pdf    : AccManager::readAccMagnitude / recoverI2C関数
- flow_pot.pdf         : PotManager::update / bpmUpdatePotentiometers関数
- flow_roundrobin.pdf  : SyncManager::packetRoundRobin関数
- flow_motor.pdf       : MotorControl::startRamp / changeBPM / stopRamp関数
- flow_displaybpm.pdf  : displayBPM関数
- flow_detectlight.pdf : 楽器デバイスのdetectLight関数
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


def rounded(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle='round,pad=0.02,rounding_size=0.12',
                                fc='white', ec='black', lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=FS, fontproperties=jp)


def rect(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle='square,pad=0.02', fc='white', ec='black', lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=FS, fontproperties=jp)


def diamond(ax, x, y, w, h, text):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
                         closed=True, fc='white', ec='black', lw=1))
    ax.text(x, y, text, ha='center', va='center', fontsize=FS, fontproperties=jp)


def arrow(ax, x1, y1, x2, y2, label=None, lx=0.12, ly=0.0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=1))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label,
                fontsize=FS - 1, fontproperties=jp)


def poly(ax, pts, label=None, lpos=None):
    for i in range(len(pts) - 2):
        ax.add_line(Line2D([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                           color='black', lw=1))
    ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='->', lw=1))
    if label and lpos:
        ax.text(lpos[0], lpos[1], label, fontsize=FS - 1, fontproperties=jp)


def new_ax(w, h, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, ymax)
    ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUTDIR, name + '.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(OUTDIR, name + '.png'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(name, 'saved')


# ============================================================
# 1. button関数
# ============================================================
fig, ax = new_ax(7.8, 7.2, 12.0)
Cx = 4.4
rounded(ax, Cx, 11.5, 3.0, 0.7, 'button() 開始')
rect(ax, Cx, 10.3, 5.2, 0.8, 'switch_status =\ndigitalRead(input_PIN)')
diamond(ax, Cx, 8.7, 5.2, 1.6, '立下り検知？（前回HIGH\nかつ今回LOW）')
diamond(ax, Cx, 6.8, 3.8, 1.3, 'isButtonPlaying\n== true？')
rect(ax, 2.0, 5.0, 3.4, 0.9, "sendEnd()：'E'送信\nisButtonPlaying = false")
rect(ax, 7.2, 5.0, 4.2, 1.3, "step = pot.getBpmStep()\nsendStart(step)：'S'送信\nisButtonPlaying = true")
rect(ax, Cx, 3.3, 4.6, 0.7, 'delay(300)：チャタリング防止')
rect(ax, Cx, 2.1, 5.2, 0.7, 'before_switch_status = switch_status')
rounded(ax, Cx, 0.9, 3.0, 0.7, 'button() 終了')
arrow(ax, Cx, 11.15, Cx, 10.7)
arrow(ax, Cx, 9.9, Cx, 9.4)
arrow(ax, Cx, 8.0, Cx, 7.45, label='yes')
poly(ax, [(Cx + 2.6, 8.7), (9.6, 8.7), (9.6, 2.1), (Cx + 2.6, 2.1)])
ax.text(Cx + 2.6, 8.9, 'no', fontsize=FS - 1, fontproperties=jp)
poly(ax, [(Cx - 1.9, 6.8), (2.0, 6.8), (2.0, 5.45)])
ax.text(2.2, 7.15, 'yes（演奏中）', fontsize=FS - 1, fontproperties=jp)
poly(ax, [(Cx + 1.9, 6.8), (7.2, 6.8), (7.2, 5.45)])
ax.text(6.3, 7.15, 'no（停止中）', fontsize=FS - 1, fontproperties=jp)
poly(ax, [(2.0, 4.55 - 0.0), (2.0, 3.3), (Cx - 2.3, 3.3)])
poly(ax, [(7.2, 4.35), (7.2, 3.3), (Cx + 2.3, 3.3)])
arrow(ax, Cx, 2.95, Cx, 2.45)
arrow(ax, Cx, 1.75, Cx, 1.25)
save(fig, 'flow_button')

# ============================================================
# 2. AccManager::update関数
# ============================================================
fig, ax = new_ax(7.8, 7.4, 12.4)
Cx = 4.6
rounded(ax, Cx, 11.9, 3.4, 0.7, 'acc.update() 開始')
diamond(ax, Cx, 10.4, 4.4, 1.3, '前回サンプリングから\nACC_SAMPLE_INTERVAL経過？')
rect(ax, Cx, 8.8, 5.2, 0.8, 'currentAccVal =\nreadAccMagnitude()')
rect(ax, Cx, 7.5, 5.2, 0.7, 'diff = |currentAccVal - lastAccVal|')
diamond(ax, Cx, 5.8, 4.8, 1.4, 'diff > accThreshold かつ\n前回検知からshakeInterval経過？')
rect(ax, Cx, 3.9, 5.6, 0.9, 'lastDetectTime更新・isStarted反転\nupdateShakedInfo()でフラグ確認・送信')
rect(ax, Cx, 2.4, 4.8, 0.7, 'lastAccVal = currentAccVal')
rounded(ax, Cx, 1.1, 3.4, 0.7, 'acc.update() 終了')
arrow(ax, Cx, 11.55, Cx, 11.05)
arrow(ax, Cx, 9.75, Cx, 9.2, label='yes')
poly(ax, [(Cx + 2.2, 10.4), (Cx + 3.6, 10.4), (Cx + 3.6, 1.1), (Cx + 1.7, 1.1)])
ax.text(Cx + 2.7, 10.6, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 8.4, Cx, 7.85)
arrow(ax, Cx, 7.15, Cx, 6.5)
arrow(ax, Cx, 5.1, Cx, 4.35, label='yes')
poly(ax, [(Cx - 2.4, 5.8), (Cx - 3.6, 5.8), (Cx - 3.6, 2.4), (Cx - 2.4, 2.4)])
ax.text(Cx - 3.45, 6.0, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 3.45, Cx, 2.75)
arrow(ax, Cx, 2.05, Cx, 1.45)
save(fig, 'flow_acc_update')

# ============================================================
# 3. readAccMagnitude / recoverI2C（2パネル）
# ============================================================
fig, ax = new_ax(9.4, 6.6, 11.0)
# 左: readAccMagnitude
Lx = 2.7
rounded(ax, Lx, 10.5, 4.0, 0.7, 'readAccMagnitude() 開始')
rect(ax, Lx, 9.3, 4.4, 0.7, 'DATAX0レジスタのアドレスを送信')
diamond(ax, Lx, 7.9, 3.8, 1.3, 'endTransmission\n≠ 0（バス異常）？')
rect(ax, Lx, 6.4, 4.2, 0.7, '6バイトの読み出しを要求')
diamond(ax, Lx, 5.0, 3.6, 1.3, '6バイト\n読み出せた？')
rect(ax, Lx, 3.5, 4.4, 0.8, 'X・Y・Z軸の値を復元し\n合成加速度√(x²+y²+z²)を算出')
rounded(ax, Lx, 2.2, 4.0, 0.7, '合成加速度を返す')
rect(ax, Lx, 0.8, 4.6, 0.8, 'recoverI2C()を実行し\n直前値lastAccValを返す')
arrow(ax, Lx, 10.15, Lx, 9.65)
arrow(ax, Lx, 8.95, Lx, 8.55)
arrow(ax, Lx, 7.25, Lx, 6.75, label='no')
poly(ax, [(Lx + 1.9, 7.9), (Lx + 2.4, 7.9), (Lx + 2.4, 1.2), (Lx + 2.3, 1.2)])
ax.text(Lx + 2.0, 8.1, 'yes', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Lx, 6.05, Lx, 5.65)
arrow(ax, Lx, 4.35, Lx, 3.9, label='yes')
poly(ax, [(Lx - 1.8, 5.0), (Lx - 2.35, 5.0), (Lx - 2.35, 1.0), (Lx - 2.3, 1.0)])
ax.text(Lx - 2.25, 5.2, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Lx, 3.1, Lx, 2.55)
# 右: recoverI2C
Rx = 7.6
rounded(ax, Rx, 10.5, 3.6, 0.7, 'recoverI2C() 開始')
rect(ax, Rx, 9.3, 4.0, 0.7, 'Wire.end()でI2Cを停止')
rect(ax, Rx, 8.0, 4.2, 0.9, 'SCL線を9回トグルし，スレーブに\n握られたSDA線を解放（バスクリア）')
rect(ax, Rx, 6.6, 4.0, 0.8, 'STOP条件を生成\n（SCL=HIGH中にSDAをLOW→HIGH）')
rect(ax, Rx, 5.2, 4.0, 0.8, 'Wire.begin()で再初期化し\nADXL345を再設定')
rounded(ax, Rx, 3.9, 3.6, 0.7, 'recoverI2C() 終了')
arrow(ax, Rx, 10.15, Rx, 9.65)
arrow(ax, Rx, 8.95, Rx, 8.45)
arrow(ax, Rx, 7.55, Rx, 7.0)
arrow(ax, Rx, 6.2, Rx, 5.6)
arrow(ax, Rx, 4.8, Rx, 4.25)
save(fig, 'flow_acc_read')

# ============================================================
# 4. PotManager::update / bpmUpdatePotentiometers
# ============================================================
fig, ax = new_ax(8.0, 7.8, 13.2)
Cx = 4.6
rounded(ax, Cx, 12.7, 3.4, 0.7, 'pot.update() 開始')
diamond(ax, Cx, 11.2, 4.2, 1.3, '前回サンプリングから\nSAMPLE_INTERVAL経過？')
rect(ax, Cx, 9.7, 5.6, 0.9, '最も古いサンプルを移動合計から減算し，\nanalogRead(PIN_BPM)の新しい値を加算')
rect(ax, Cx, 8.4, 5.2, 0.7, '書き込み位置bpmReadIndexを更新')
diamond(ax, Cx, 7.0, 3.8, 1.3, 'バッファが一巡\n（満杯）した？')
rect(ax, Cx, 5.5, 5.2, 0.7, '移動平均 = 移動合計 / sampleSize')
rect(ax, Cx, 4.2, 5.6, 0.9, 'calcStep()：4つの境界値との比較で\n段階1〜5を算出')
diamond(ax, Cx, 2.6, 3.8, 1.3, '段階が前回から\n変化した？')
rect(ax, Cx, 1.1, 4.4, 0.7, 'bpmFrag = true（送信予約）')
rounded(ax, 8.9, 1.1, 2.0, 0.9, '音量系統も\n同様に処理')
arrow(ax, Cx, 12.35, Cx, 11.85)
arrow(ax, Cx, 10.55, Cx, 10.15, label='yes')
poly(ax, [(Cx + 2.1, 11.2), (8.9, 11.2), (8.9, 1.55)])
ax.text(Cx + 2.5, 11.4, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 9.25, Cx, 8.75)
arrow(ax, Cx, 8.05, Cx, 7.65)
arrow(ax, Cx, 6.35, Cx, 5.85, label='yes')
poly(ax, [(Cx + 1.9, 7.0), (8.6, 7.0), (8.9, 7.0), (8.9, 1.55)])
ax.text(Cx + 2.3, 7.2, 'no（蓄積中）', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 5.15, Cx, 4.65)
arrow(ax, Cx, 3.75, Cx, 3.25)
arrow(ax, Cx, 1.95, Cx, 1.45, label='yes')
poly(ax, [(Cx - 1.9, 2.6), (Cx - 3.2, 2.6), (Cx - 3.2, 0.5), (Cx, 0.5), (7.9, 0.5), (7.9, 0.75)])
ax.text(Cx - 3.05, 2.8, 'no', fontsize=FS - 1, fontproperties=jp)
poly(ax, [(Cx + 2.2, 1.1), (7.9, 1.1)])
save(fig, 'flow_pot')

# ============================================================
# 5. packetRoundRobin
# ============================================================
fig, ax = new_ax(7.2, 5.8, 9.6)
Cx = 4.6
rounded(ax, Cx, 9.1, 4.2, 0.7, 'packetRoundRobin() 開始')
rect(ax, Cx, 7.9, 3.4, 0.7, 'round = 0')
rect(ax, Cx, 6.5, 5.6, 0.9, '全ターゲットへ1回ずつパケットを送信\n（beginPacket → write → endPacket）')
diamond(ax, Cx, 4.8, 3.6, 1.3, 'round < 2？\n（3周目以外）')
rect(ax, Cx, 3.1, 4.6, 0.8, 'delay(20)：20 ms待機\nround = round + 1')
rounded(ax, Cx, 1.0, 4.2, 0.7, 'packetRoundRobin() 終了')
arrow(ax, Cx, 8.75, Cx, 8.25)
arrow(ax, Cx, 7.55, Cx, 6.95)
arrow(ax, Cx, 6.05, Cx, 5.45)
arrow(ax, Cx, 4.15, Cx, 3.5, label='yes')
poly(ax, [(Cx - 2.3, 3.1), (Cx - 3.3, 3.1), (Cx - 3.3, 6.5), (Cx - 2.8, 6.5)])
poly(ax, [(Cx + 1.8, 4.8), (Cx + 3.3, 4.8), (Cx + 3.3, 1.0), (Cx + 2.1, 1.0)])
ax.text(Cx + 2.3, 5.0, 'no（3周完了）', fontsize=FS - 1, fontproperties=jp)
save(fig, 'flow_roundrobin')

# ============================================================
# 6. MotorControl（3列）
# ============================================================
fig, ax = new_ax(9.8, 5.6, 9.2)
xs = [1.9, 5.0, 8.1]
# startRamp
rounded(ax, xs[0], 8.7, 2.9, 0.7, 'startRamp() 開始')
rect(ax, xs[0], 7.4, 3.2, 0.9, 'stepToNumber()：\nLUTからpwmValue等を取得')
rect(ax, xs[0], 5.9, 3.2, 1.1, 'PWM出力を0から\npwmValueまで5刻みで増加\n（各ステップ40 ms待機）')
rect(ax, xs[0], 4.4, 3.2, 0.7, 'pwmValueを出力')
rounded(ax, xs[0], 3.2, 2.9, 0.7, '終了')
arrow(ax, xs[0], 8.35, xs[0], 7.85)
arrow(ax, xs[0], 6.95, xs[0], 6.45)
arrow(ax, xs[0], 5.35, xs[0], 4.75)
arrow(ax, xs[0], 4.05, xs[0], 3.55)
# changeBPM
rounded(ax, xs[1], 8.7, 2.9, 0.7, 'changeBPM() 開始')
rect(ax, xs[1], 7.4, 3.2, 0.9, 'stepToNumber()：\nLUTからpwmValue等を取得')
rect(ax, xs[1], 5.9, 3.2, 1.1, 'updateStatus()：\n角速度ωと平均電圧\nV_averageを算出')
rect(ax, xs[1], 4.4, 3.2, 0.7, 'pwmValueを出力')
rounded(ax, xs[1], 3.2, 2.9, 0.7, '終了')
arrow(ax, xs[1], 8.35, xs[1], 7.85)
arrow(ax, xs[1], 6.95, xs[1], 6.45)
arrow(ax, xs[1], 5.35, xs[1], 4.75)
arrow(ax, xs[1], 4.05, xs[1], 3.55)
# stopRamp
rounded(ax, xs[2], 8.7, 2.9, 0.7, 'stopRamp() 開始')
rect(ax, xs[2], 7.4, 3.2, 1.1, 'PWM出力をpwmValueから\n0まで5刻みで減少\n（各ステップ40 ms待機）')
rect(ax, xs[2], 5.9, 3.2, 0.7, '0を出力（停止）')
rounded(ax, xs[2], 4.7, 2.9, 0.7, '終了')
arrow(ax, xs[2], 8.35, xs[2], 7.95)
arrow(ax, xs[2], 6.85, xs[2], 6.25)
arrow(ax, xs[2], 5.55, xs[2], 5.05)
save(fig, 'flow_motor')

# ============================================================
# 7. displayBPM
# ============================================================
fig, ax = new_ax(7.8, 7.2, 12.0)
Cx = 4.6
rounded(ax, Cx, 11.5, 3.4, 0.7, 'displayBPM() 開始')
diamond(ax, Cx, 10.1, 3.8, 1.3, '段階番号が\n1〜5の範囲内？')
rect(ax, Cx, 8.6, 5.0, 0.7, 'bpm = bpmTable[stepNumber - 1]')
rect(ax, Cx, 7.4, 4.6, 0.7, 'フレームバッファを初期化')
rect(ax, Cx, 6.2, 5.2, 0.8, 'BPM値を各桁に分割\n（100以上：3桁，10以上：2桁）')
rect(ax, Cx, 4.8, 5.6, 0.8, '表示幅（桁数×3+桁間1）から\n中央揃えの開始位置を算出')
rect(ax, Cx, 3.4, 5.6, 0.8, '各桁をdrawDigit()で描画\n（3×5フォント配列と照合しバッファへ）')
rect(ax, Cx, 2.0, 5.6, 0.8, 'バッファをuint32_t[3]へビットパックし\nmatrix.loadFrame()で表示')
rounded(ax, Cx, 0.7, 3.4, 0.7, 'displayBPM() 終了')
arrow(ax, Cx, 11.15, Cx, 10.75)
arrow(ax, Cx, 9.45, Cx, 8.95, label='yes')
poly(ax, [(Cx + 1.9, 10.1), (Cx + 3.6, 10.1), (Cx + 3.6, 0.7), (Cx + 1.7, 0.7)])
ax.text(Cx + 2.3, 10.3, 'no（何もせず終了）', fontsize=FS - 1.5, fontproperties=jp)
arrow(ax, Cx, 8.25, Cx, 7.75)
arrow(ax, Cx, 7.05, Cx, 6.6)
arrow(ax, Cx, 5.8, Cx, 5.2)
arrow(ax, Cx, 4.4, Cx, 3.8)
arrow(ax, Cx, 3.0, Cx, 2.4)
arrow(ax, Cx, 1.6, Cx, 1.05)
save(fig, 'flow_displaybpm')

# ============================================================
# 8. detectLight（楽器デバイス受光検知）
# ============================================================
fig, ax = new_ax(8.4, 8.6, 14.4)
Cx = 4.6
rounded(ax, Cx, 13.9, 3.4, 0.7, 'detectLight() 開始')
diamond(ax, Cx, 12.5, 3.8, 1.3, '起動時較正\n完了？')
rect(ax, Cx, 10.9, 5.8, 0.9, '最小値を探索しbaselineを更新．\n1秒経過で較正完了（照射中なら解除待ちへ）')
diamond(ax, Cx, 9.3, 3.8, 1.3, '照射解除待ち\n（waitingForRelease）？')
rect(ax, Cx, 7.7, 5.8, 0.9, '非照射になったらbaselineを再設定し\n解除待ちを終了（検知はfalse）')
rect(ax, Cx, 6.2, 5.8, 0.9, '非照射中：baselineを追従更新\n（最小値，または31/32の重みで平滑化）')
diamond(ax, Cx, 4.5, 4.4, 1.4, '非照射中 かつ v が\nonThreshold以上？')
rect(ax, 2.0, 2.7, 3.4, 0.9, '立ち上がり検知：\nlaserOn = true（trueを返す）')
diamond(ax, 7.3, 2.7, 3.4, 1.3, '照射中かつ\nv が offThreshold以下？')
rect(ax, 7.3, 0.9, 4.4, 0.9, '立ち下がり：registerPeak()で\nピーク履歴としきい値を更新（false）')
arrow(ax, Cx, 13.55, Cx, 13.15)
arrow(ax, Cx, 11.85, Cx, 11.35, label='no（較正中）')
poly(ax, [(Cx + 1.9, 12.5), (Cx + 3.9, 12.5), (Cx + 3.9, 9.95)], )
ax.text(Cx + 2.4, 12.7, 'yes', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx + 3.9, 9.95, Cx + 1.5, 9.75)
arrow(ax, Cx, 8.65, Cx, 8.15, label='yes')
poly(ax, [(Cx - 1.9, 9.3), (Cx - 3.6, 9.3), (Cx - 3.6, 6.65), (Cx - 2.9, 6.65)])
ax.text(Cx - 3.45, 9.5, 'no', fontsize=FS - 1, fontproperties=jp)
arrow(ax, Cx, 5.75, Cx, 5.2)
arrow(ax, 2.9, 3.8, 2.0, 3.15, label='yes', lx=-0.8)
arrow(ax, 6.3, 3.8, 7.3, 3.35, label='no', lx=0.3)
arrow(ax, 7.3, 2.05, 7.3, 1.35, label='yes')
save(fig, 'flow_detectlight')
