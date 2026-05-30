#include "Display.h"
#include "Arduino_LED_Matrix.h"

// -------------------------
// 独自フォント定義
// font3x5[digit][row*3 + col] : 3列×5行のビットマップ（1=点灯, 0=消灯）
// 対象数字：0〜9（BPM表示用：60〜180の範囲で使用する桁）
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

// LEDマトリクスのインスタンス（12列×8行）
// Display.h で extern 宣言し，.ino の setup() から matrix.begin() を呼ぶこと
ArduinoLEDMatrix matrix;

// 描画用共有フレームバッファ（8行×12列，uint8_t: 1=点灯 / 0=消灯）
// drawDigit() がここに書き込み，displayBPM() がまとめてレンダリングする
static uint8_t frameBuffer[8][12];

// -------------------------
// displayBPM
// 引数 bpm : 表示するBPM値（想定範囲：60 / 90 / 120 / 150 / 180）
// 処理概要：
//   1. フレームバッファを全消灯にクリア
//   2. BPM値を各桁に分解（1〜3桁対応）
//   3. 全桁の合計幅から左端X座標を算出し，12列に対してX方向中央寄せ
//   4. 各桁について drawDigit() を呼び出してフレームバッファに書き込む
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

  // X方向中央寄せの計算
  // 各桁は幅3px，桁間スペース1px → 合計幅 = numDigits*3 + (numDigits-1)*1
  int totalWidth = numDigits * 3 + (numDigits - 1) * 1;
  int startX = (12 - totalWidth) / 2;  // 12列に対する左端オフセット

  // 各桁をフレームバッファに描画（桁ピッチ = 3px + 1px間隔 = 4px）
  for (int i = 0; i < numDigits; i++) {
    drawDigit(digits[i], startX + i * 4);
  }

  // フレームバッファをLEDマトリクスに描画（8行×12列）
  matrix.renderBitmap(frameBuffer, 8, 12);
}

// -------------------------
// drawDigit
// 引数 digit    : 描画する数字（0〜9）
//      x_offset : フレームバッファ上の描画開始列（0〜11）
// 処理概要：
//   font3x5[digit] の3×5ビットマップを，frameBuffer の
//   (y_offset〜y_offset+4, x_offset〜x_offset+2) 領域に書き込む
//   Y方向は (8-5)/2 = 1行オフセットで上下中央寄せ
// -------------------------
void drawDigit(int digit, int x_offset) {
  // 範囲外の数字は無視
  if (digit < 0 || digit > 9) return;

  // Y方向中央寄せオフセット：8行に5行フォントを配置 → 上下各1行余白
  const int y_offset = 1;

  for (int y = 0; y < 5; y++) {
    for (int x = 0; x < 3; x++) {
      int col = x_offset + x;
      int row = y_offset + y;
      // バッファ境界チェック（x_offsetが端に近い場合の範囲外アクセス防止）
      if (col >= 0 && col < 12 && row >= 0 && row < 8) {
        frameBuffer[row][col] = font3x5[digit][y * 3 + x];
      }
    }
  }
}

// -------------------------
// checkUDP
// 中継機からのUDPパケットを受信し，BPM値を確認する（通信実装予定）
// 現時点では通信モジュールの設計が確定していないためスタブとして定義
// -------------------------
void checkUDP() {
  // TODO: UDP受信処理・BPM値の取り出し・displayBPM() 呼び出しを実装する
}
