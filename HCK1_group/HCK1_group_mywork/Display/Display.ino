#include "Display.h"

// -------------------------
// Display.ino（計画書 3.5.7.1）
// 中継機からの通信管理を担当する．高速通信を目的としてUDP形式で
// BPM情報を受信し，Display.cpp の描画処理（checkUDP / displayBPM）を利用する．
// -------------------------

// UDP通信オブジェクト（Display.h で extern 宣言，checkUDP() から参照される）
WiFiUDP Udp;

// Wi-Fi接続情報（実機運用時に中継機と同一ネットワークの値を設定すること）
// ※通信部の詳細実装は通信担当と連携して確定する（プレースホルダ）
const char SSID[] = "";   // Wi-Fiネットワーク名
const char PASS[] = "";   // Wi-Fiパスワード

// setup() : 起動時に1回だけ実行される初期化処理
void setup() {
  // LEDマトリクスの初期化
  matrix.begin();

  // Wi-Fi接続（SSID/PASS設定時のみ接続を試行）
  if (SSID[0] != '\0') {
    while (WiFi.begin(SSID, PASS) != WL_CONNECTED) {
      delay(1000);  // 接続確立まで待機
    }
  }

  // UDP受信開始（計画書 表3.23 の LOCAL_PORT で待ち受け）
  Udp.begin(LOCAL_PORT);
}

// loop() : メインループ
// checkUDP() で中継機からのBPMパケットを監視し，
// 値が更新された場合に内部で displayBPM() が呼ばれて表示が更新される．
void loop() {
  checkUDP();
}
