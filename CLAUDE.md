# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

千葉工業大学 ハッカソン1 (HCK1) のプロジェクト。「指揮デバイス」— 指揮者の動作・操作をArduinoで検知し、観覧車型の演奏デバイス群をリアルタイムに制御するシステム。

## Running the Code

**Arduino スケッチ（.ino）:**
- Arduino IDE でボード「Arduino UNO R4 WiFi」を選択してコンパイル・書き込み
- シリアルモニタのボーレートはスケッチごとに異なる（`cds_test`: 9600 bps, `slider_test`: 115200 bps）

**Processing スケッチ（.pde）:**
- Processing IDE で開いて Run（Ctrl+R / ⌘+R）
- `HCK02_02.pde` はシリアルポートが `/dev/cu.usbmodem34B7DA6320602` にハードコードされているため、実行環境に合わせて変更が必要

## System Architecture

3種類のArduino UNO R4 WiFiデバイスが連携する：

```
[指揮デバイス]                    [表示デバイス]
  スライダー(A0=BPM, A1=音量)   ←UDP(port 2390)← 
  加速度センサ(I2C: A4=SDA, A5=SCL, D2=INT1)

[楽器デバイス]                    [PC: Processing]
  光センサ(LM393, D2=割り込み)  →シリアル(USB)→ Minim音声出力
  BLE受信(音量, ESP32-S3内蔵)
```

### 通信プロトコル

**UDP（指揮→表示デバイス）:** 固定長2バイト `[ヘッダ 1byte][ペイロード 1byte]`
- ヘッダ `'B'` (0x42) = BPMデータ、ペイロード = 段階番号 1〜5
- ヘッダ `'E'` = 演奏終了（LEDマトリクス消灯）

**BPM 5段階設定値:**
| 段階 | BPM |
|------|-----|
| 1    | 60  |
| 2    | 90  |
| 3    | 120 |
| 4    | 150 |
| 5    | 180 |

## Key Source Files

| パス | 内容 |
|------|------|
| `HCK1_group/HCK1_group_mywork/Display/Display.ino` | 表示デバイスのメインスケッチ（UDP受信→LEDマトリクス表示） |
| `HCK1_group/HCK1_group_mywork/Display/Display.cpp` | BPM表示ロジック・独自3×5フォント定義 |
| `HCK1_group/HCK1_group_mywork/Display/Display.h` | 定数定義（ポート番号・BPM段階・フォントサイズ） |
| `HCK_Processing/Processing_ver2/HCK02_02/HCK02_02.pde` | 最新Processingスケッチ（シリアル受信+Minim音声+マイク波形表示） |
| `HCK1_group/HCK1_group_mywork/cds_test/cds_test.ino` | CdS光センサ検証（A0のアナログ値をシリアル出力） |
| `HCK1_group/HCK1_group_mywork/slider_test/slider_test.ino` | スライダー式可変抵抗器の動作検証 |

## Git Workflow

ファイルを新規作成・編集した場合、作業完了後に必ず以下を実行する：

1. 作成・変更したファイルを `git add` でステージング
2. 作業内容を日本語で説明するコミットメッセージを付けて `git commit`
3. `git push` でリモート（GitHub）に反映

コミットメッセージの形式：
```
<作業の概要（1行）>

- <変更点1>
- <変更点2>
```

## Response Guidelines

- 専門用語・技術の説明は大学生を対象とする（「中高生向けに説明して」と指示があった場合はそれに従う）
- 出力は客観的事実のみとし、根拠のない評価や過度な称賛を含めない
- 絵文字は使用しない

## Important Notes

- `Display.cpp` の `checkUDP()` 内の通信部はコメントアウト済み（描画動作確認用の状態）。UDP受信を有効化する際はコメントを外す。
- Processing の Minim ライブラリは `HCK_Processing/libraries/minim/` にローカルで同梱。
- KiCad 回路図ファイル（`.kicad_sch`, `.kicad_pro`）は `概要/` ディレクトリに置いてある。
- `概要/` 以下に LaTeX 形式の計画書・設計書ソース（`.tex`）がある。コンパイルは `platex` または `lualatex` を使用。
