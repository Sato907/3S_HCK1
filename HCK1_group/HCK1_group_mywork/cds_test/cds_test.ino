/*
 * CdSセル 受光動作検証プログラム（手による遮光方式）
 *
 * 対象: Arduino UNO (楽器デバイス受光部 / 計画書 図3.4)
 * 目的: CdS セル(GL5516) が光を正しく検知できるかを検証する．
 *       手で CdS セルを覆う（遮光）・外す操作を行い，A0 の値が変化すれば
 *       「CdS セルは光を検知できている」と判定する．
 *
 * 配線（計画書 図3.4 の分圧回路に準拠）:
 *   5V  ── CdS セル(GL5516) ──┬── A0       … 明るいほど A0 の値が大きくなる
 *                              └── 10kΩ ── GND
 *
 * 検証の手順:
 *   1. Arduino に書き込み，シリアルモニタ(115200 bps)を開く
 *   2. 起動後，CdS セルを覆わずに「明時基準値」を自動測定する（3秒間）
 *   3. 次に手で CdS セルを覆い，「暗時基準値」を自動測定する（3秒間）
 *   4. 以降はリアルタイムで A0 値と明暗判定を表示し続ける
 *      → 手で覆う/外すたびに値と判定が変化すれば「検知OK」
 *
 * シリアルモニタ(115200 bps)で各値と判定結果を確認する．
 */

// --- ピン定義 ---
const int CDS_PIN = A0;

// --- 測定パラメータ ---
const int CALIB_SAMPLES = 50;  // 基準値測定のサンプル数
const int CALIB_MS = 3000;     // 基準値測定にかける時間[ms]

// 明暗の境界値（明時と暗時の中間値として setup() で自動算出）
int threshold = 0;

// --- 判定パラメータ ---
// 明時と暗時の差がこの値以上あれば，CdS が正常に光を検知できていると判定する．
const int VALID_DIFF = 50;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  Serial.println("=== CdSセル 受光動作検証（手による遮光） ===");
  Serial.println();

  // --- (1) 明時基準値の測定（CdS を覆わない状態） ---
  Serial.println("[ステップ1] CdSセルを覆わずにそのまま待ってください...");
  delay(1000);
  int brightBase = measureAverage(CALIB_SAMPLES, CALIB_MS / CALIB_SAMPLES);
  Serial.print("  明時基準値: ");
  Serial.println(brightBase);
  Serial.println();

  // --- (2) 暗時基準値の測定（手で覆った状態） ---
  Serial.println("[ステップ2] 手でCdSセルを覆ってください...");
  delay(2000);
  int darkBase = measureAverage(CALIB_SAMPLES, CALIB_MS / CALIB_SAMPLES);
  Serial.print("  暗時基準値: ");
  Serial.println(darkBase);
  Serial.println();

  // --- 判定基準の評価 ---
  int diff = brightBase - darkBase;
  Serial.print("  明暗の差: ");
  Serial.print(diff);
  if (diff >= VALID_DIFF) {
    Serial.println("  => キャリブレーションOK：CdSセルは明暗を検知できています");
    // 閾値は明時と暗時の中間値
    threshold = (brightBase + darkBase) / 2;
    Serial.print("  判定閾値(明暗中間値): ");
    Serial.println(threshold);
  } else {
    Serial.println("  => 要確認：明暗の差が小さすぎます（配線を確認してください）");
    // 差が小さくても閾値を設定して以降の表示は続ける
    threshold = (brightBase + darkBase) / 2;
  }

  Serial.println();
  Serial.println("手でCdSセルを覆う/外す操作を繰り返してください．");
  Serial.println("出力形式: [A0生値]  [明/暗]");
  Serial.println("---------------------------------------------------");
}

void loop() {
  int value = analogRead(CDS_PIN);

  Serial.print("A0=");
  Serial.print(value);
  Serial.print("\t");

  if (value >= threshold) {
    Serial.println("明（光あり）");
  } else {
    Serial.println("暗（遮光中）");
  }

  delay(200);
}

// 指定サンプル数・間隔で A0 を読み取り，平均値を返す
int measureAverage(int samples, int intervalMs) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(CDS_PIN);
    delay(intervalMs);
  }
  return (int)(sum / samples);
}
