//仮 


#include "Display.h"
#include <WiFiS3.h>

// 通信
WiFiUDP Udp;
unsigned int localPort = 8888; // 受信ポート
char packetBuffer[255];

// 現在のBPMを保持する変数
int currentBpm = 0;

// Display.cppで実体が定義されているmatrixを呼び出すためのextern宣言
extern ArduinoLEDMatrix matrix;

void setup() {
  Serial.begin(9600);
  
  // LEDマトリクスの初期化
  matrix.begin();

  // WiFiの初期化（実際のネットワーク環境に合わせてSSIDとパスワードを設定してください）
  // WiFi.begin("SSID", "PASSWORD");
  // Udp.begin(localPort);
  
  Serial.println("Display System Initialized.");
}

void loop() {
  // 図3.18のフローチャートに従い、常にUDPパケットを確認
  checkUDP();
}

void checkUDP() {
  // パケットの確認
  int packetSize = Udp.parsePacket();
  
  // 2バイト（ヘッダ1byte + ペイロード1byte）の固定長通信の確認
  if (packetSize >= 2) { 
    Udp.read(packetBuffer, 2);
    
    char header = packetBuffer[0];
    uint8_t payload = packetBuffer[1];

    // ヘッダ確認: 'B'はBPMデータ
    if (header == 'B') {
      int receivedBpm = 0;
      
      // ペイロード(段階番号1〜5)を設定値へ変換
      switch(payload) {
        case 1: receivedBpm = 60; break;
        case 2: receivedBpm = 90; break;
        case 3: receivedBpm = 120; break;
        case 4: receivedBpm = 150; break;
        case 5: receivedBpm = 180; break;
        default: return; // 規定の段階番号以外は不正データとして破棄
      }

      // BPM更新確認: 値が更新されていれば描画処理を実行
      if (receivedBpm != currentBpm) {
        currentBpm = receivedBpm;
        displayBPM(currentBpm);
      }
    }
    // ヘッダ確認: 'E'は演奏終了
    else if (header == 'E') {
      // 終了合図を受信した場合の処理
      matrix.clear(); // マトリクスの表示を消去
      currentBpm = 0;
    }
  }
}