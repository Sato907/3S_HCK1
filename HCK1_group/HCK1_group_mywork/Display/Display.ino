#include "Display.h"

// -------------------------
// Display.ino（計画書 3.5.7.1）
// 本来は中継機からの通信管理（UDP受信）を担当するが，
// 現段階では通信部をコメントアウトし，与えたBPM値をLEDマトリクスに
// 描画する動作確認用のプログラムのみを残している．
// -------------------------

// ===== 通信部（未実装のためコメントアウト） =====
/*
// UDP通信オブジェクト（Display.h で extern 宣言，checkUDP() から参照される）
WiFiUDP Udp;

// Wi-Fi接続情報（実機運用時に中継機と同一ネットワークの値を設定すること）
const char SSID[] = "";   // Wi-Fiネットワーク名
const char PASS[] = "";   // Wi-Fiパスワード
*/

// 描画するBPM値（60 / 90 / 120 / 150 / 180 のいずれかを指定）
const int DISPLAY_BPM = 150;

// setup() : 起動時に1回だけ実行される初期化処理
void setup() {
  // LEDマトリクスの初期化
  matrix.begin();

  // begin() 後の最初の loadFrame は反映されない場合があるため，
  // ウォームアップとして全点灯フレームを一度描画してから待機する．
  // （起動時に一瞬だけ全LEDが点灯する）
  uint32_t warmUp[3] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF};
  matrix.loadFrame(warmUp);
  delay(300);

  // ===== 通信部の初期化（未実装のためコメントアウト） =====
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
// 表示を確実に保持するため，与えられたBPM値を継続的に再描画する．
void loop() {
  displayBPM(DISPLAY_BPM);
  delay(500);

  // ===== 通信部（未実装のためコメントアウト） =====
  // checkUDP();   // 本来は中継機からのBPMパケットを監視して描画を更新する
}
