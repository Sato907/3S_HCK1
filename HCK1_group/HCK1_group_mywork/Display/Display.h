#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include "Arduino_LED_Matrix.h"  // Arduino UNO R4 WiFi 内蔵LEDマトリクス用ライブラリ
// #include <WiFiS3.h>           // 通信有効化時に取り込む（UDP受信用）

// BPM定数定義
// スライド式可変抵抗器による五段階設定値（単位：BPM）
#define BPM_STEP_1  60
#define BPM_STEP_2  90
#define BPM_STEP_3  120
#define BPM_STEP_4  150
#define BPM_STEP_5  180

// 通信定数
#define LOCAL_PORT     2390   // UDP受信に利用するポート番号
#define HEADER_BPM     'B'    // BPMデータの識別ヘッダ（ASCII 0x42）

// 文字フォントの寸法
#define FONT_WIDTH   3   // 1文字の横ドット数
#define FONT_HEIGHT  5   // 1文字の縦ドット数

// LEDマトリクスの寸法（Arduino UNO R4 WiFi 内蔵：8行×12列）
#define MATRIX_ROWS  8
#define MATRIX_COLS  12

// 関数宣言

// LEDマトリクスの初期化（matrix.begin()を本関数経由で呼ぶ。理由はDisplay.cpp参照）
void displaySetup();

// 中継機からのUDPパケット確認，BPM値の受信処理（引数・返り値なし）
void checkUDP();

// 受信したBPM値をLEDマトリクスに数値表示する（引数：int bpm）
void displayBPM(int bpm);

// 指定された1桁の数字を，共有フレームバッファの x_offset 列から描画する
void drawDigit(int digit, int x_offset);

// 外部参照

// 3×5（横3×縦5）の独自数字フォント（0〜9）
extern const uint8_t font3x5[10][15];

// LEDマトリクスインスタンス（Display.cpp で定義，.ino の setup() で begin() を呼ぶ）
extern ArduinoLEDMatrix matrix;

// UDP通信オブジェクト（通信有効化時に Display.ino で定義・宣言する）
// extern WiFiUDP Udp;

#endif