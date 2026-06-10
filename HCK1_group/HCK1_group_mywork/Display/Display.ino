#include "Display.h"

// 本来は中継機からの通信管理（UDP受信）を担当するが，
// 現段階では通信部をコメントアウトし，与えたBPM値をLEDマトリクスに
// 描画する動作確認用のプログラムのみを残している．
//
// 注：LEDマトリクスの表示バッファはライブラリのヘッダ内で翻訳単位ごとに
// 別実体となるため，matrix を直接操作せず，Display.cpp の関数
// （displaySetup / displayBPM）経由で扱うこと．

// 通信部
/*
// UDP通信オブジェクト（Display.h で extern 宣言，checkUDP() から参照される）
WiFiUDP Udp;

// Wi-Fi接続情報
const char SSID[] = "";   // Wi-Fiネットワーク名
const char PASS[] = "";   // Wi-Fiパスワード
*/

// 描画するBPM値(検証用)
const int DISPLAY_BPM = 150;

void setup() {
  // LEDマトリクスの初期化（Display.cpp 側で begin() を実行する）
  displaySetup();

  // 通信部の初期化
  /*
  if (SSID[0] != '\0') {
    while (WiFi.begin(SSID, PASS) != WL_CONNECTED) {
      delay(1000);  // 接続確立まで待機
    }
  }
  Udp.begin(LOCAL_PORT);  // UDP受信開始
  */

  // 与えられたBPM値をLEDマトリクスに描画する
  displayBPM(DISPLAY_BPM);
}

// loop() : メインループ
void loop() {
  // 通信部
  // checkUDP();   // 本来は中継機からのBPMパケットを監視して描画を更新する
}