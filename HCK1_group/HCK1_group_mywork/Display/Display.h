#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include "Arduino_LED_Matrix.h"  // Arduino UNO R4 WiFi 内蔵LEDマトリクス用ライブラリ
#include <WiFiS3.h> //UDP通信

// BPM定数定義
#define BPM_STEP_1  60
#define BPM_STEP_2  90
#define BPM_STEP_3  120
#define BPM_STEP_4  150
#define BPM_STEP_5  180

// 通信定数
#define LOCAL_PORT     2390   // UDP受信に利用するポート番号
#define HEADER_BPM     'B'    // BPMデータ受信の識別ヘッダ
#define HEADER_END     'E'    // 演奏終了の識別ヘッダ（LEDマトリクス消灯）

// 文字フォントの寸法
#define FONT_WIDTH   3   // 1文字の横ドット数
#define FONT_HEIGHT  5   // 1文字の縦ドット数

// LEDマトリクスの寸法（Arduino UNO R4 WiFi 内蔵：8行×12列）
#define MATRIX_ROWS  8
#define MATRIX_COLS  12

// 関数宣言

// LEDマトリクスの初期化（matrix.begin()を本関数経由で呼ぶ。
void displaySetup();

// 中継機からのUDPパケット確認，BPM値の受信処理
void checkUDP();

// 受信したBPM値をLEDマトリクスに数値表示する（引数：int bpm）
void displayBPM(int bpm);

// LEDマトリクスを全消灯する（演奏終了時に使用）
void clearDisplay();

// 指定された1桁の数字を，共有フレームバッファの x_offset 列から描画する
void drawDigit(int digit, int x_offset);

// 外部参照

// 3×5（横3×縦5）の独自数字フォント（0〜9）
extern const uint8_t font3x5[10][15];

// LEDマトリクスインスタンス（Display.cpp で定義，.ino の setup() で begin() を呼ぶ）
extern ArduinoLEDMatrix matrix;

// UDP通信オブジェクト
extern WiFiUDP Udp;

#endif