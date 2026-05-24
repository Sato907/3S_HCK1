# ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
# include "Arduino_LED_Matrix.h" //Arduino付属マトリクス用ライブラリ

//関数定義 

//中継機からのパケット確認，BPMの値確認
void checkUDP();

//BPM数値の描画
void displayBPM(int bpm);

//各桁の独自フォント配列をフレームバッファに描画
void drawDigit(int digit, int x_offset);

//独自フォント定義
extern const uint8_t font3x5[10][15];

# endif



