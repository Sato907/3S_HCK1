#include "Display.h"

// -------------------------
// Display.ino（計画書 3.5.7.1）
// 本来は中継機からの通信管理（UDP受信）を担当するが，
// 現段階では通信部をコメントアウトし，与えたBPM値をLEDマトリクスに
// 描画する動作確認用のプログラムのみを残している．
// -------------------------

// UDP通信オブジェクト（Display.h で extern 宣言）
// 通信部が有効化されるまでここで定義だけ置いておく
WiFiUDP Udp;

// ===== 通信部（未実装のためコメントアウト） =====
/*

// Wi-Fi接続情報（実機運用時に中継機と同一ネットワークの値を設定すること）
const char SSID[] = "";   // Wi-Fiネットワーク名
const char PASS[] = "";   // Wi-Fiパスワード
*/

// 描画するBPM値（60 / 90 / 120 / 150 / 180 のいずれかを指定）
const int DISPLAY_BPM = 120;

// setup() : 起動時に1回だけ実行される初期化処理
void setup() {
  // LEDマトリクスの初期化
  matrix.begin();

  // ===== 通信部の初期化（未実装のためコメントアウト） =====
  /*
  // Wi-Fi接続（SSID/PASS設定時のみ接続を試行）
  if (SSID[0] != '\0') {
    while (WiFi.begin(SSID, PASS) != WL_CONNECTED) {
      delay(1000);  // 接続確立まで待機
    }
  }
  // UDP受信開始（計画書 表3.23 の LOCAL_PORT で待ち受け）
  Udp.begin(LOCAL_PORT);
  */

  // 与えられたBPM値をLEDマトリクスに描画する
  displayBPM(DISPLAY_BPM);
}

// loop() : メインループ
void loop() {
  // ===== 通信部（未実装のためコメントアウト） =====
  // checkUDP();   // 本来は中継機からのBPMパケットを監視して描画を更新する
}