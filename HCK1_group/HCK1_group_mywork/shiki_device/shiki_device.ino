/*
 * 指揮デバイス 
 *
 *
 
 
 *   ★現段階の実装状況★
 *     通信部（WiFi / UDP 送信）はコメントアウトしている。
 *     まずは「可変抵抗器の値を移動平均→5段階へ写像する」部分を，
 *     シリアルモニタ(115200 bps)で確認できるようにしている。
 *     本来 UDP 送信するタイミングでは，送る内容をシリアルに出力して代替する。
 *     通信を有効化する際は、各所の「通信部」コメントを外すこと。
 *
 * ハードウェア構成:
 *   - 加速度センサ GY-291(ADXL345): I2C 接続, アドレス 0x53,
 *       SDA=A4 / SCL=A5（UNO R4 WiFi の既定 I2C ピン）, INT1 → D2
 *   - ボタン: D3, 外部 10kΩ プルアップ, 押下時 LOW（演奏開始/終了トリガー）
 *   - スライド式可変抵抗器 2 本(10kΩ): BPM 変更用 / 音量変更用
 *
 * 使用ライブラリ:
 *   - Wire.h   : I2C 通信。ADXL345 はレジスタを直接読み書きするため外部ライブラリ不要。
 *   - WiFiS3.h : UNO R4 WiFi の WiFi / UDP 通信（※通信部実装時に有効化）
 */

// ===== 通信部（未実装のためコメントアウト） =====
// #include <WiFiS3.h>   // UNO R4 WiFi 用 WiFi / UDP ライブラリ
// #include <WiFiUdp.h>  // WiFiUDP クラス
#include <Wire.h>     // I2C（ADXL345 用）
#include <math.h>     // sqrt()

// =====================================================================
// 設定値（ピン番号・閾値・送信先・WiFi情報）
//   ★印 と TODO が付いた箇所は実環境に合わせてユーザが設定すること
// =====================================================================

// ===== 通信部の設定（未実装のためコメントアウト） =====
/*
// ----- WiFi 接続情報 -----
// TODO(ユーザ設定): 中継機・楽器デバイスと同一ネットワークの SSID / パスワードを入力する
const char WIFI_SSID[] = "YOUR_SSID";      // ★仮値: WiFi ネットワーク名
const char WIFI_PASS[] = "YOUR_PASSWORD";  // ★仮値: WiFi パスワード

// ----- 送信先（UDP） -----
// TODO(ユーザ設定): 各デバイスの実 IP アドレスとポート番号を確定して設定する
// 観覧車（中継機 / 表示デバイス）: BPM と 演奏開始/終了 の送信先
IPAddress      RELAY_IP(192, 168, 1, 50);      // ★仮値: 中継機の IP アドレス
const uint16_t RELAY_PORT      = 2390;          // 中継機の UDP 受信ポート（計画書 表3.23）
// 楽器デバイス用 Arduino: 音量データの送信先
IPAddress      INSTRUMENT_IP(192, 168, 1, 51);  // ★仮値: 楽器デバイスの IP アドレス
const uint16_t INSTRUMENT_PORT = 2390;          // ★仮値: 楽器デバイスの UDP 受信ポート（TODO 確認）
// 本機（指揮デバイス）が UDP 送受信に使うローカルポート
const uint16_t LOCAL_UDP_PORT  = 2391;          // ★仮値（TODO 確認）
*/



// ----- ピン定義 -----
// TODO(ユーザ設定): bpmPin / volPin は計画書で未指定のため A0 / A1 を仮採用。確定後に変更する
const int bpmPin       = A0;  // ★仮値: BPM 変更用 可変抵抗器（アナログ）
const int volPin       = A5;  // ★仮値: 音量変更用 可変抵抗器（アナログ）
const int BUTTON_PIN   = 3;   // ボタン: D3（外部 10kΩ プルアップ, 押下で LOW）
const int ACC_INT_PIN  = 2;   // ADXL345 INT1 → D2（本実装はポーリング方式。割り込み化する場合に使用）

// ----- 移動平均（ノイズ対策） -----
// TODO(ユーザ設定): sampleSize は計画書で未指定のため 10 を仮採用。応答性とノイズ除去のバランスで調整する
const int sampleSize = 10;    // ★仮値: 移動平均のサンプル数

// ----- 加速度センサ（振り動作検知） -----
// TODO(ユーザ設定): accThreshold / shakeInterval は実機で振って調整する
const int          accThreshold  = 120;   // ★仮値: 「振った」と判定する加速度変化量[LSB]
const unsigned long shakeInterval = 400;  // ★仮値: 連続検知防止のための最小間隔[ms]

// ----- ボタンのチャタリング除去 -----
const unsigned long debounceDelay = 50;   // ボタン状態確定までの待ち[ms]

// ----- ADXL345 レジスタ定義 -----
const uint8_t ADXL345_ADDR        = 0x53;  // I2C アドレス（SDO=GND のとき 0x53）
const uint8_t ADXL345_REG_POWER   = 0x2D;  // POWER_CTL
const uint8_t ADXL345_REG_FORMAT  = 0x31;  // DATA_FORMAT
const uint8_t ADXL345_REG_DATAX0  = 0x32;  // X/Y/Z データ先頭（0x32〜0x37 の 6 バイト）
const uint8_t ADXL345_REG_DEVID   = 0x00;  // DEVID（接続確認用, 期待値 0xE5）

// ===== 通信部の識別ヘッダ（未実装のためコメントアウト） =====
/*
// ----- UDP 識別ヘッダ（パケット先頭 1 バイト） -----
const char HEADER_BPM   = 'B';  // 0x42: BPM データ
const char HEADER_VOL   = 'V';  // 0x56: 音量データ
const char HEADER_START = 'S';  // 0x53: 演奏開始
const char HEADER_END   = 'E';  // 0x45: 演奏終了
*/

// ----- 段階→設定値の変換テーブル（計画書 表3.27 ほか） -----
// 段階 1〜5 を配列添字 0〜4 に対応させる
const int bpmStepValues[5] = { 60, 90, 120, 150, 180 };  // 段階→BPM
const int volStepValues[5] = { 0, 64, 128, 192, 255 };   // 段階→音量(0〜255)

// ----- デバッグ出力 -----
const bool DEBUG = true;  // true でシリアルに状態を出力（115200 bps）

// =====================================================================
// グローバル状態変数
// =====================================================================

// ===== 通信部（未実装のためコメントアウト） =====
// WiFiUDP Udp;  // UDP 通信オブジェクト

// 移動平均用リングバッファ（仕様で指定された変数名）
int bpmSamples[sampleSize];  // BPM 用可変抵抗器のサンプル
int volSamples[sampleSize];  // 音量用可変抵抗器のサンプル
int readIndex = 0;           // リングバッファの書き込み位置（最古要素を上書き）
int bpmTotal = 0;            // bpmSamples の合計
int volTotal = 0;            // volSamples の合計
int averageBpmVal = 0;       // BPM 用の移動平均値（0〜1023）
int averageVolVal = 0;       // 音量用の移動平均値（0〜1023）
int currentBpmStep = 0;      // 現在の BPM 段階（1〜5, 0 は未確定）
int currentVolStep = 0;      // 現在の音量段階（1〜5, 0 は未確定）

// 直近に確定した段階（段階が変化したときだけ処理するための記録, 0 は未処理）
int lastSentBpmStep = 0;
int lastSentVolStep = 0;

// 演奏状態（false=停止, true=演奏中）
bool isPlaying = false;

// ボタンのエッジ検出・チャタリング除去用
int           lastButtonReading = HIGH;          // 直近に読み取った生の入力（プルアップなので既定 HIGH）
int           buttonState       = HIGH;          // 確定したボタン状態
unsigned long lastDebounceTime  = 0;             // 最後に入力変化を観測した時刻[ms]

// 加速度の振り動作検知用
float         prevAccMagnitude  = -1.0f;         // 直前の加速度ベクトルの大きさ（-1 は未初期化）
unsigned long lastShakeTime     = 0;             // 最後に「振った」と判定した時刻[ms]


void setup() {
  if (DEBUG) {
    Serial.begin(115200);
    // シリアル接続を待ちすぎないよう一定時間で打ち切る（USB 未接続でも動作させる）
    unsigned long t0 = millis();
    while (!Serial && (millis() - t0 < 2000)) {}
    Serial.println(F("=== 指揮デバイス 起動（可変抵抗器→5段階 写像テスト） ==="));
    Serial.println(F("可変抵抗器を動かすと、段階(1〜5)と設定値が表示されます。"));
  }

  // ピンモード設定
  pinMode(BUTTON_PIN, INPUT);    // 外部 10kΩ プルアップを使用（押下で LOW）
  pinMode(ACC_INT_PIN, INPUT);   // ADXL345 INT1。本実装ではポーリングのため参照のみ

  // I2C・加速度センサ初期化
  Wire.begin();
  initAccelerometer();

  // 可変抵抗器の移動平均バッファを初期値で満たす（起動直後から有効な平均を得るため）
  initPots();

  // ===== 通信部の初期化（未実装のためコメントアウト） =====
  // connectWiFi();
  // Udp.begin(LOCAL_UDP_PORT);

  if (DEBUG) Serial.println(F("初期化完了"));
}


void loop() {
  // 1. ボタン入力判定（演奏開始/終了）
  checkButton();

  // 2. 可変抵抗器の読み取り（移動平均→5段階化）。段階が変化したら表示
  readPots();

  // 3. 加速度センサの振り動作検知。振ったタイミングで最新 BPM 段階を表示
  if (checkShake()) {
    // 段階が変化したときだけ処理（無駄を避ける）
    if (currentBpmStep != lastSentBpmStep) {
      // ===== 通信部（未実装のためコメントアウト） =====
      // sendPacket(RELAY_IP, RELAY_PORT, HEADER_BPM, (uint8_t)bpmStepValues[currentBpmStep - 1]);
      lastSentBpmStep = currentBpmStep;
      if (DEBUG) {
        Serial.print(F("[BPM確定/送信予定] 段階="));
        Serial.print(currentBpmStep);
        Serial.print(F(" 値="));
        Serial.println(bpmStepValues[currentBpmStep - 1]);
      }
    }
  }

  delay(20);  // サンプリング間隔の確保とシリアル出力過多の抑制（テスト用）
}


void checkButton() {
  int reading = digitalRead(BUTTON_PIN);

  // 入力が変化したらタイマをリセット（チャタリング除去の起点）
  if (reading != lastButtonReading) {
    lastDebounceTime = millis();
  }

  // 一定時間変化がなければ，その値を確定状態として採用
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;

      // 確定状態が「押下（LOW）」に変化した瞬間だけトリガーする
      if (buttonState == LOW) {
        isPlaying = !isPlaying;  // 演奏状態をトグル

        if (isPlaying) {
          // ===== 通信部（未実装のためコメントアウト） =====
          // sendPacket(RELAY_IP, RELAY_PORT, HEADER_START, 0);
          if (DEBUG) Serial.println(F("[演奏開始/送信予定] 'S'"));
        } else {
          // ===== 通信部（未実装のためコメントアウト） =====
          // sendPacket(RELAY_IP, RELAY_PORT, HEADER_END, 0);
          if (DEBUG) Serial.println(F("[演奏終了/送信予定] 'E'"));
        }
      }
    }
  }

  lastButtonReading = reading;
}


void readPots() {
  // (a) リングバッファ更新（readIndex の位置の最古要素を上書きして合計を更新）
  bpmTotal -= bpmSamples[readIndex];
  volTotal -= volSamples[readIndex];

  bpmSamples[readIndex] = analogRead(bpmPin);
  volSamples[readIndex] = analogRead(volPin);

  bpmTotal += bpmSamples[readIndex];
  volTotal += volSamples[readIndex];

  readIndex = (readIndex + 1) % sampleSize;  // 次の書き込み位置へ（末尾で先頭へ戻る）

  // 移動平均値を算出
  averageBpmVal = bpmTotal / sampleSize;
  averageVolVal = volTotal / sampleSize;

  // ===== 一時デバッグ: 生値と移動平均を毎ループ表示（切り分け用） =====
  //   slider_test と同様に raw 値を確認するための出力。
  //   原因切り分けが済んだら、この DEBUG_RAW ブロックは削除してよい。
  if (DEBUG) {
    Serial.print(F("RAW A0(bpm)="));
    Serial.print(analogRead(bpmPin));
    Serial.print(F(" avg="));
    Serial.print(averageBpmVal);
    Serial.print(F("  |  A1(vol)="));
    Serial.print(analogRead(volPin));
    Serial.print(F(" avg="));
    Serial.println(averageVolVal);
  }

  // (b) 5段階化
  currentBpmStep = valueToStep(averageBpmVal);
  currentVolStep = valueToStep(averageVolVal);

  // (c) 段階が変化したときだけ表示（無駄な出力を避ける）
  //     ※通信実装時:
  //        ・BPM  は「振り動作検知時」に中継機へ UDP 送信する（loop() 側で処理）
  //        ・音量 は「段階変化時」に楽器デバイスへ UDP 送信する（下記で sendPacket を呼ぶ）

  // BPM 段階の変化を表示（可変抵抗器を回すと段階が変わることを確認するため）
  if (currentBpmStep != lastSentBpmStep) {
    if (DEBUG) {
      Serial.print(F("BPM  : 平均="));
      Serial.print(averageBpmVal);
      Serial.print(F(" → 段階="));
      Serial.print(currentBpmStep);
      Serial.print(F(" → "));
      Serial.print(bpmStepValues[currentBpmStep - 1]);
      Serial.println(F(" BPM"));
    }
    // 注: BPM の確定（lastSentBpmStep の更新）は振り動作検知時に行うため、ここでは更新しない
  }

  // 音量 段階の変化を表示（通信実装時はここで楽器デバイスへ送信）
  if (currentVolStep != lastSentVolStep) {
    // ===== 通信部（未実装のためコメントアウト） =====
    // sendPacket(INSTRUMENT_IP, INSTRUMENT_PORT, HEADER_VOL, (uint8_t)volStepValues[currentVolStep - 1]);
    lastSentVolStep = currentVolStep;
    if (DEBUG) {
      Serial.print(F("音量 : 平均="));
      Serial.print(averageVolVal);
      Serial.print(F(" → 段階="));
      Serial.print(currentVolStep);
      Serial.print(F(" → 値="));
      Serial.println(volStepValues[currentVolStep - 1]);
    }
  }
}


int valueToStep(int value) {
  if (value <= 204)      return 1;
  else if (value <= 409) return 2;
  else if (value <= 614) return 3;
  else if (value <= 819) return 4;
  else                   return 5;
}

// 起動時に移動平均バッファを初期化（現在の可変抵抗器値で満たす）
void initPots() {
  bpmTotal = 0;
  volTotal = 0;
  for (int i = 0; i < sampleSize; i++) {
    bpmSamples[i] = analogRead(bpmPin);
    volSamples[i] = analogRead(volPin);
    bpmTotal += bpmSamples[i];
    volTotal += volSamples[i];
  }
  readIndex = 0;
  averageBpmVal = bpmTotal / sampleSize;
  averageVolVal = volTotal / sampleSize;
  // 初期段階を算出（lastSent* は 0 のままにして，最初のループで現在値を 1 回表示させる）
  currentBpmStep = valueToStep(averageBpmVal);
  currentVolStep = valueToStep(averageVolVal);
}

// =====================================================================
// 加速度センサ制御（機能2）
//   上下の振り動作を検知する。加速度ベクトルの大きさの変化量が accThreshold を
//   超えたら「振った」と判定し true を返す。shakeInterval で連続検知を防止する。
//   （注: 大きさの変化で検知するため取り付け向きに依存しない。厳密に上下のみを
//     見たい場合は，読み取った Z 軸の変化量だけで判定するよう変更する → TODO）
// =====================================================================
bool checkShake() {
  int16_t x, y, z;
  if (!readAccel(x, y, z)) {
    return false;  // 読み取り失敗時は検知しない
  }

  // 加速度ベクトルの大きさ
  float magnitude = sqrt((float)x * x + (float)y * y + (float)z * z);

  // 初回は基準値を保存するだけで判定しない
  if (prevAccMagnitude < 0.0f) {
    prevAccMagnitude = magnitude;
    return false;
  }

  // 直前との変化量
  float delta = fabs(magnitude - prevAccMagnitude);
  prevAccMagnitude = magnitude;

  unsigned long now = millis();

  // 閾値超え かつ 前回検知から shakeInterval 以上経過しているときだけ「振った」と判定
  if (delta > accThreshold && (now - lastShakeTime) >= shakeInterval) {
    lastShakeTime = now;
    if (DEBUG) {
      Serial.print(F("[検知] 振り動作 delta="));
      Serial.println(delta);
    }
    return true;
  }
  return false;
}

// ---------------------------------------------------------------------
// ADXL345 を測定モードで初期化する
// ---------------------------------------------------------------------
void initAccelerometer() {
  // 接続確認（DEVID = 0xE5 が期待値）
  uint8_t devid = readRegister(ADXL345_REG_DEVID);
  if (DEBUG) {
    Serial.print(F("ADXL345 DEVID=0x"));
    Serial.println(devid, HEX);
    if (devid != 0xE5) {
      Serial.println(F("[警告] ADXL345 が検出できません。配線(I2C, アドレス0x53)を確認してください。"));
    }
  }

  // DATA_FORMAT: フルレゾリューション, ±2g（0x08）。感度を変えたい場合はここを変更
  writeRegister(ADXL345_REG_FORMAT, 0x08);
  // POWER_CTL: 測定モード開始（Measure ビット = 0x08）
  writeRegister(ADXL345_REG_POWER, 0x08);
}

// ---------------------------------------------------------------------
// ADXL345 から X/Y/Z の加速度を読み取る（成功で true）
//   データは 0x32〜0x37 の 6 バイト，各軸リトルエンディアンの符号付き16bit
// ---------------------------------------------------------------------
bool readAccel(int16_t &x, int16_t &y, int16_t &z) {
  Wire.beginTransmission(ADXL345_ADDR);
  Wire.write(ADXL345_REG_DATAX0);
  if (Wire.endTransmission(false) != 0) {  // リピートスタート
    return false;
  }
  uint8_t n = Wire.requestFrom((int)ADXL345_ADDR, 6);
  if (n < 6) {
    return false;
  }
  uint8_t buf[6];
  for (int i = 0; i < 6; i++) {
    buf[i] = Wire.read();
  }
  x = (int16_t)(buf[0] | (buf[1] << 8));
  y = (int16_t)(buf[2] | (buf[3] << 8));
  z = (int16_t)(buf[4] | (buf[5] << 8));
  return true;
}

// ---------------------------------------------------------------------
// ADXL345 レジスタ書き込み
// ---------------------------------------------------------------------
void writeRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(ADXL345_ADDR);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

// ---------------------------------------------------------------------
// ADXL345 レジスタ読み出し（1 バイト）
// ---------------------------------------------------------------------
uint8_t readRegister(uint8_t reg) {
  Wire.beginTransmission(ADXL345_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom((int)ADXL345_ADDR, 1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0;
}

// ===== 通信部（未実装のためコメントアウト） =====
/*
// =====================================================================
// WiFi 接続
// =====================================================================
void connectWiFi() {
  if (DEBUG) {
    Serial.print(F("WiFi 接続中: "));
    Serial.println(WIFI_SSID);
  }
  // 接続できるまで再試行（必要に応じてタイムアウト処理を追加すること → TODO）
  while (WiFi.begin(WIFI_SSID, WIFI_PASS) != WL_CONNECTED) {
    delay(1000);
    if (DEBUG) Serial.print(F("."));
  }
  if (DEBUG) {
    Serial.println();
    Serial.print(F("WiFi 接続完了 IP="));
    Serial.println(WiFi.localIP());
  }
}

// =====================================================================
// UDP 送信
//   パケット = [識別ヘッダ 1byte][値 1byte(uint8_t)]
// =====================================================================
void sendPacket(IPAddress ip, uint16_t port, char header, uint8_t value) {
  Udp.beginPacket(ip, port);
  Udp.write((uint8_t)header);
  Udp.write(value);
  Udp.endPacket();
}
*/
