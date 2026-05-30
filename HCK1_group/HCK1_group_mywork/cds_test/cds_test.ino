/*
 * CdSセル + LED 受光部 動作検証プログラム
 *
 * 対象: Arduino UNO (楽器デバイス受光部 / 計画書 図3.4)
 * 目的: 観覧車のレーザー光（または手持ちの光源）が CdS セルを通過したことを
 *       検知し，反応の有無を「LED の点灯」と「シリアルモニタ出力」で確認する．
 *
 * 配線（計画書 図3.4 の分圧回路に準拠）:
 *   5V  ── CdS セル(GL5516) ──┬── A0       … 明るいほど A0 の値が大きくなる
 *                              └── 10kΩ ── GND
 *   確認用 LED ── D13(内蔵LED)            … 検知時に点灯
 *   （外付け LED を使う場合: D13 ── 220Ω ── LED ── GND）
 *
 * 検証項目:
 *   1. CdS セルのアナログ値(0〜1023)が明暗で変化するか
 *   2. 光の立ち上がり（レーザー通過）を閾値で検知できるか（計画書 3.5.6）
 *   3. 検知に同期して LED が点灯し，回路が反応するか
 *   4. 検知間隔から「生のBPM」を算出できるか（計画書 式3.8）
 *   5. 誤検知防止（デバウンス）が機能するか（計画書 3.5.6）
 *
 * シリアルモニタ(115200 bps)で各値を確認する．
 */

// --- ピン定義 ---
const int CDS_PIN = A0;           // CdS セルの分圧出力
const int LED_PIN = LED_BUILTIN;  // 検知確認用LED（内蔵LED = D13）

// --- 検知パラメータ ---
// 起動時の環境光（暗時）を基準値とし，そこから DELTA 以上明るくなった瞬間を
// 「レーザー光が通過した」と判定する．基準値は setup() で自動測定する．
const int DELTA = 150;            // 検知に必要な明るさの増分（環境に応じて調整）
const int CALIB_SAMPLES = 50;     // 起動時の基準値測定サンプル数

// --- 誤検知防止（デバウンス）パラメータ（計画書 3.5.6） ---
// 一度検知したら一定時間は次の検知を行わず，1回の通過での多重検知を防ぐ．
const unsigned long DEBOUNCE_MS = 100;

// --- BPM補正用：演奏に使用するBPMリスト（計画書 表3.27） ---
const int BPM_LIST[5] = {60, 90, 120, 150, 180};

// --- 状態変数 ---
int lightThreshold = 0;           // 検知閾値（基準値 + DELTA）
bool isLightDetected = false;     // 現在「光あり」状態か（立ち上がり検出用）
unsigned long lastDetectTime = 0; // 前回の検知時刻[ms]
unsigned long prevDetectTime = 0; // 前々回の検知時刻[ms]（間隔計算用）

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("=== CdSセル + LED 受光部 動作検証 ===");

  // --- 起動時の環境光を基準値として自動測定 ---
  // CdS セルに光を当てていない（暗い）状態で起動すること．
  long sum = 0;
  for (int i = 0; i < CALIB_SAMPLES; i++) {
    sum += analogRead(CDS_PIN);
    delay(5);
  }
  int baseline = sum / CALIB_SAMPLES;
  lightThreshold = baseline + DELTA;

  Serial.print("環境光(基準値): ");
  Serial.print(baseline);
  Serial.print("  検知閾値: ");
  Serial.println(lightThreshold);
  Serial.println("CdSセルに光を当てると LED が点灯します．");
  Serial.println("---------------------------------------------------");
}

void loop() {
  int rawValue = analogRead(CDS_PIN);
  unsigned long now = millis();

  // --- 生値のモニタ出力（常時） ---
  Serial.print("CdS生値=");
  Serial.print(rawValue);
  Serial.print(" / 閾値=");
  Serial.print(lightThreshold);

  // --- 閾値判定 + LED 反応 ---
  bool aboveThreshold = (rawValue >= lightThreshold);
  digitalWrite(LED_PIN, aboveThreshold ? HIGH : LOW);
  Serial.print(aboveThreshold ? "  [光あり]" : "  [光なし]");

  // --- 立ち上がり検知（光なし → 光あり）+ デバウンス ---
  if (aboveThreshold && !isLightDetected) {
    if (now - lastDetectTime > DEBOUNCE_MS) {
      isLightDetected = true;
      prevDetectTime = lastDetectTime;
      lastDetectTime = now;

      Serial.print("  >>> 光検知! ");

      // --- 検知間隔から生のBPMを算出（計画書 式3.8） ---
      if (prevDetectTime != 0) {
        unsigned long interval = lastDetectTime - prevDetectTime;
        long rawBpm = 30000L / (long)interval;     // 30000 / 間隔[ms]
        int snappedBpm = snapToNearestBpm(rawBpm);  // 最も近いBPMへ補正

        Serial.print("間隔=");
        Serial.print(interval);
        Serial.print("ms  生BPM=");
        Serial.print(rawBpm);
        Serial.print("  補正BPM=");
        Serial.print(snappedBpm);
      } else {
        Serial.print("(1回目の検知)");
      }
    }
  }
  // --- 光あり → 光なし（次の検知に備えてリセット） ---
  else if (!aboveThreshold && isLightDetected) {
    isLightDetected = false;
  }

  Serial.println();
  delay(20);
}

// 生のBPM値を，演奏に使用するBPMリストの中で最も近い値へ補正する（計画書 3.5.6）
int snapToNearestBpm(long rawBpm) {
  int nearest = BPM_LIST[0];
  long minDiff = labs(rawBpm - BPM_LIST[0]);
  for (int i = 1; i < 5; i++) {
    long diff = labs(rawBpm - BPM_LIST[i]);
    if (diff < minDiff) {
      minDiff = diff;
      nearest = BPM_LIST[i];
    }
  }
  return nearest;
}
