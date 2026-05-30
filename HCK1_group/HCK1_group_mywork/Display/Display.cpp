#include "Display.h"
#include "Arduino_LED_Matrix.h"

// -------------------------
// 独自フォント定義（計画書 3.5.7.1）
// 「1文字を縦5横3で再定義」する仕様に基づき，1文字 = 横3×縦5 = 15要素で表現する．
// font3x5[digit][row*FONT_WIDTH + col] : 1=点灯, 0=消灯
// 計画書に示された数字0の例と同一のレイアウトを採用している．
// -------------------------
const uint8_t font3x5[10][15] = {
  // 0
  {1, 1, 1,
   1, 0, 1,
   1, 0, 1,
   1, 0, 1,
   1, 1, 1},
  // 1
  {0, 1, 0,
   1, 1, 0,
   0, 1, 0,
   0, 1, 0,
   1, 1, 1},
  // 2
  {1, 1, 1,
   0, 0, 1,
   1, 1, 1,
   1, 0, 0,
   1, 1, 1},
  // 3
  {1, 1, 1,
   0, 0, 1,
   0, 1, 1,
   0, 0, 1,
   1, 1, 1},
  // 4
  {1, 0, 1,
   1, 0, 1,
   1, 1, 1,
   0, 0, 1,
   0, 0, 1},
  // 5
  {1, 1, 1,
   1, 0, 0,
   1, 1, 1,
   0, 0, 1,
   1, 1, 1},
  // 6
  {1, 1, 1,
   1, 0, 0,
   1, 1, 1,
   1, 0, 1,
   1, 1, 1},
  // 7
  {1, 1, 1,
   0, 0, 1,
   0, 0, 1,
   0, 0, 1,
   0, 0, 1},
  // 8
  {1, 1, 1,
   1, 0, 1,
   1, 1, 1,
   1, 0, 1,
   1, 1, 1},
  // 9
  {1, 1, 1,
   1, 0, 1,
   1, 1, 1,
   0, 0, 1,
   1, 1, 1}
};

// 段階番号(1〜5)からBPM設定値へ変換するテーブル（計画書 表3.27）
// bpmTable[stage-1] で対応するBPMを得る
static const int bpmTable[5] = {
  BPM_STEP_1,  // 段階1 → 60
  BPM_STEP_2,  // 段階2 → 90
  BPM_STEP_3,  // 段階3 → 120
  BPM_STEP_4,  // 段階4 → 150
  BPM_STEP_5   // 段階5 → 180
};

// LEDマトリクスのインスタンス（8行×12列）
// Display.h で extern 宣言し，.ino の setup() で matrix.begin() を呼ぶこと
ArduinoLEDMatrix matrix;

// 描画用共有フレームバッファ（MATRIX_ROWS行 × MATRIX_COLS列，1=点灯 / 0=消灯）
// drawDigit() がここに書き込み，displayBPM() がまとめてレンダリングする
static uint8_t frameBuffer[MATRIX_ROWS][MATRIX_COLS];

// 直近に表示中のBPM値（更新検知用：値が変化した時だけ再描画する）
static int currentBPM = -1;

// -------------------------
// checkUDP（計画書 3.5.7.3）
// 中継機からのパケット確認とBPM値確認を行う．引数・返り値なし．
// 処理概要：
//   1. Udp.parsePacket() でパケット到達を監視
//   2. 到達していれば2バイトのペイロード（ヘッダ + 段階番号）を読み込む
//   3. ヘッダが規定の 'B'(BPMデータ) であるかを確認
//   4. 段階番号(1〜5)を bpmTable で BPM設定値へ変換し数値として保持
//   5. 値が更新されていれば displayBPM() で描画更新する
// -------------------------
void checkUDP() {
  int packetSize = Udp.parsePacket();
  if (packetSize <= 0) return;  // パケット未到達

  // ペイロードを読み込む（計画書 表3.28/3.29：ヘッダ1byte + データ1byte の固定長）
  uint8_t buffer[2] = {0};
  int len = Udp.read(buffer, sizeof(buffer));
  if (len < 2) return;  // 規定長に満たないパケットは破棄

  char header = (char)buffer[0];
  uint8_t stage = buffer[1];

  // 規定のBPMヘッダか確認
  if (header != HEADER_BPM) return;
  // 段階番号の範囲チェック（1〜5）
  if (stage < 1 || stage > 5) return;

  // 段階番号 → BPM設定値へ変換
  int bpm = bpmTable[stage - 1];

  // 値が更新された時だけ再描画（帯域・描画処理の無駄を抑制）
  if (bpm != currentBPM) {
    currentBPM = bpm;
    displayBPM(bpm);
  }
}

// -------------------------
// displayBPM（計画書 3.5.7.3）
// 引数 bpm : 表示するBPM値（想定範囲：60 / 90 / 120 / 150 / 180）
// 処理概要：
//   1. フレームバッファを0でクリアし表示をリセット
//   2. BPM値を各桁に分解（1〜3桁対応）
//   3. 全桁の合計幅から左端X座標を算出し，横方向中央寄せ
//   4. 各桁を drawDigit() でフレームバッファに描画
//   5. matrix.renderBitmap() でLEDマトリクスに一括描画
// -------------------------
void displayBPM(int bpm) {
  // フレームバッファをすべて消灯にリセット
  memset(frameBuffer, 0, sizeof(frameBuffer));

  // BPM値を桁配列に分解
  int digits[3];   // 最大3桁分
  int numDigits;

  if (bpm >= 100) {
    numDigits = 3;
    digits[0] = bpm / 100;         // 百の位
    digits[1] = (bpm / 10) % 10;  // 十の位
    digits[2] = bpm % 10;          // 一の位
  } else if (bpm >= 10) {
    numDigits = 2;
    digits[0] = bpm / 10;          // 十の位
    digits[1] = bpm % 10;          // 一の位
  } else {
    numDigits = 1;
    digits[0] = bpm;               // 一の位のみ
  }

  // 横方向中央寄せの計算
  // 各桁は幅FONT_WIDTH(3)，桁間スペース1px → 合計幅 = numDigits*3 + (numDigits-1)*1
  int totalWidth = numDigits * FONT_WIDTH + (numDigits - 1) * 1;
  int startX = (MATRIX_COLS - totalWidth) / 2;  // 12列に対する左端オフセット

  // 各桁をフレームバッファに描画（桁ピッチ = 3px + 1px間隔 = 4px）
  for (int i = 0; i < numDigits; i++) {
    drawDigit(digits[i], startX + i * (FONT_WIDTH + 1));
  }

  // フレームバッファをLEDマトリクスに描画（8行×12列）
  matrix.renderBitmap(frameBuffer, MATRIX_ROWS, MATRIX_COLS);
}

// -------------------------
// drawDigit
// 引数 digit    : 描画する数字（0〜9）
//      x_offset : フレームバッファ上の描画開始列（0〜11）
// 処理概要：
//   font3x5[digit] の 横3×縦5 ビットマップを，frameBuffer の
//   (y_offset〜, x_offset〜) 領域に書き込む．
//   縦方向は (MATRIX_ROWS - FONT_HEIGHT)/2 行のオフセットで上下中央寄せ．
// -------------------------
void drawDigit(int digit, int x_offset) {
  // 範囲外の数字は無視
  if (digit < 0 || digit > 9) return;

  // 縦方向中央寄せオフセット：8行に5行フォントを配置 → (8-5)/2 = 1行余白
  const int y_offset = (MATRIX_ROWS - FONT_HEIGHT) / 2;

  for (int y = 0; y < FONT_HEIGHT; y++) {       // 縦5ドット
    for (int x = 0; x < FONT_WIDTH; x++) {      // 横3ドット
      int col = x_offset + x;
      int row = y_offset + y;
      // バッファ境界チェック（端に近い場合の範囲外アクセス防止）
      if (col >= 0 && col < MATRIX_COLS && row >= 0 && row < MATRIX_ROWS) {
        frameBuffer[row][col] = font3x5[digit][y * FONT_WIDTH + x];
      }
    }
  }
}
