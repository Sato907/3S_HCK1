/*
 * CdSセル 受光動作検証プログラム（LEDを光源として使用）
 *
 * 対象: Arduino UNO (楽器デバイス受光部 / 計画書 図3.4)
 * 目的: CdS セル(GL5516) が光を正しく検知できるかを検証する．
 *       検証用の光源として LED を用い，LED を消灯/点灯させたときに
 *       CdS セルのアナログ値が変化するかを比較することで判定する．
 *       （LED は検知結果の表示用ではなく，CdS に当てる「光源」として使う）
 *
 * 配線（計画書 図3.4 の分圧回路に準拠）:
 *   5V  ── CdS セル(GL5516) ──┬── A0       … 明るいほど A0 の値が大きくなる
 *                              └── 10kΩ ── GND
 *   検証用光源 LED: D13 ── 220Ω ── LED ── GND   … CdS セルに向けて配置する
 *
 * 検証の考え方:
 *   LED 消灯時(暗)と点灯時(明)で CdS の値を測定し，その差が一定以上あれば
 *   「CdS セルは光を検知できている」と判定する．
 *
 * シリアルモニタ(115200 bps)で各値と判定結果を確認する．
 */

// --- ピン定義 ---
const int CDS_PIN = A0;           // CdS セルの分圧出力
const int LED_PIN = 13;           // CdS に光を当てる検証用LED（外付け推奨）

// --- 測定パラメータ ---
const int SETTLE_MS = 200;        // LED 切替後，CdS が安定するまでの待ち時間[ms]
const int MEASURE_SAMPLES = 20;   // 1回の測定で平均するサンプル数

// --- 判定パラメータ ---
// LED 点灯時と消灯時の CdS 値の差が，この値以上あれば「光を検知できた」と判定する．
// 環境光や LED の明るさ・距離に応じて調整する．
const int DETECT_DIFF = 50;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("=== CdSセル 受光動作検証（LED光源） ===");
  Serial.println("LED を消灯/点灯させ，CdS の値変化で受光できるか判定します．");
  Serial.print("判定基準: 点灯時と消灯時の差 >= ");
  Serial.print(DETECT_DIFF);
  Serial.println(" で「検知OK」");
  Serial.println("---------------------------------------------------");
}

void loop() {
  // --- (1) LED 消灯時（暗）の CdS 値を測定 ---
  digitalWrite(LED_PIN, LOW);
  delay(SETTLE_MS);
  int darkValue = readCdsAverage();

  // --- (2) LED 点灯時（明）の CdS 値を測定 ---
  digitalWrite(LED_PIN, HIGH);
  delay(SETTLE_MS);
  int brightValue = readCdsAverage();

  // --- (3) 差分から受光できているかを判定 ---
  // CdS は 5V 側に接続されているため，明るいほど A0 の値は大きくなる．
  int diff = brightValue - darkValue;

  Serial.print("消灯時(暗)=");
  Serial.print(darkValue);
  Serial.print("  点灯時(明)=");
  Serial.print(brightValue);
  Serial.print("  差=");
  Serial.print(diff);

  if (diff >= DETECT_DIFF) {
    Serial.println("  => 検知OK：CdSセルは光を検知できています");
  } else if (diff <= -DETECT_DIFF) {
    Serial.println("  => 要確認：明暗が逆です（CdSの接続向きを確認）");
  } else {
    Serial.println("  => 検知NG：値が変化しません（配線/光源の向きを確認）");
  }

  // 消灯に戻して次の測定まで待機
  digitalWrite(LED_PIN, LOW);
  delay(1000);
}

// CdS セルの値を複数回読み取り，平均値を返す（ノイズ低減）
int readCdsAverage() {
  long sum = 0;
  for (int i = 0; i < MEASURE_SAMPLES; i++) {
    sum += analogRead(CDS_PIN);
    delay(2);
  }
  return (int)(sum / MEASURE_SAMPLES);
}
