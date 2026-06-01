#include "Display.h"

// -------------------------
// Display.ino（計画書 3.5.7.1）
// ※現在は無表示問題の切り分け用に，診断シーケンスを実行している．
//   通信部はコメントアウト中．
// -------------------------

const int DISPLAY_BPM = 120;

// 計算済みの「120」フレーム（displayBPMと同じフォント・同じパック方式で生成）
const uint32_t FRAME_120[3] = {0x0004eec2, 0xa4ea48ae, 0xee000000};

void setup() {
  Serial.begin(115200);
  matrix.begin();

  // --- テスト1：全点灯（1.5秒） ---
  Serial.println("TEST1: all on");
  uint32_t allOn[3] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF};
  matrix.loadFrame(allOn);
  delay(1500);

  // --- テスト2：計算済み「120」フレームを直接描画（1.5秒） ---
  // ここで「120」が出れば，2回目以降のloadFrameは正常に動作している．
  Serial.println("TEST2: hardcoded 120");
  matrix.loadFrame(FRAME_120);
  delay(1500);

  // --- テスト3：displayBPM() 経由で描画（以降保持） ---
  // ここで「120」が出れば displayBPM も正常．テスト2と変われば displayBPM 側の問題．
  Serial.println("TEST3: displayBPM(120)");
  displayBPM(DISPLAY_BPM);
}

void loop() {
  // 診断中は何もしない（テスト3の表示を保持）
}
