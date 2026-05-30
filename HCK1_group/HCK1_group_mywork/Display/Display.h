#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include "Arduino_LED_Matrix.h"  // Arduino UNO R4 WiFi 内蔵LEDマトリクス用ライブラリ

// -------------------------
// BPM定数定義
// スライド式可変抵抗器による五段階設定値（単位：BPM）
// -------------------------
#define BPM_STEP_1  60
#define BPM_STEP_2  90
#define BPM_STEP_3  120
#define BPM_STEP_4  150
#define BPM_STEP_5  180

// -------------------------
// 関数宣言
// -------------------------

// 中継機からのUDPパケット確認，BPM値の受信処理（通信実装予定）
void checkUDP();

// 受信したBPM値をLEDマトリクスに数値表示する
void displayBPM(int bpm);

// 指定された1桁の数字を，共有フレームバッファの x_offset 列から描画する
void drawDigit(int digit, int x_offset);

// -------------------------
// 外部参照
// -------------------------

// 3×5ピクセルの独自数字フォント（0〜9）
extern const uint8_t font3x5[10][15];

// LEDマトリクスインスタンス（Display.cpp で定義，.ino の setup() から begin() を呼ぶ）
extern ArduinoLEDMatrix matrix;

#endif
