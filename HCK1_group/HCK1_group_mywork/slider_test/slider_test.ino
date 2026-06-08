/*
 * スライダー式可変抵抗器 動作検証プログラム
 *
 * 対象: Arduino UNO R4 WiFi (指揮デバイス)
 * 接続: スライダー → A0
 *       GND → スライダー端子1, 5V → スライダー端子3, ワイパー端子 → A0
 *
 * 検証内容:
 *   生の値(0〜1023)をそのままシリアルモニタに表示する．
 *   スライダーを動かして値が変化すれば正常に動作している．
 *   Aピンから正しく値を読み取れなかった場合は，その旨を表示する．
 *
 * シリアルモニタ(115200 bps)で値を確認する．
 */

// --- ピン定義 ---
const int SLIDER_PIN = A0;   // スライダー式可変抵抗器

// --- 正常範囲の定義 ---
const int ADC_MIN = 0;      // analogReadの最小値
const int ADC_MAX = 1023;   // analogReadの最大値(10bit)

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  Serial.println("=== スライダー式可変抵抗器 動作検証 ===");
  Serial.println("スライダー: A0");
  Serial.println("アナログピンの生の値(0〜1023)を表示します．");
  Serial.println("---------------------------------------------------");
}

void loop() {
  // アナログピンから値を読み取り，正しく読み取れたか確認する
  int sliderVal = readSlider(SLIDER_PIN, "A0");

  // 正常に読み取れた場合のみ値を表示
  if (sliderVal >= 0) {
    Serial.print("A0=");
    Serial.println(sliderVal);
  }

  delay(1000);
}

/*
 * アナログピンの値を読み取り，妥当性を検証する関数
 * 戻り値: 正常時は読み取り値(0〜1023)，異常時は -1
 */
int readSlider(int pin, const char* label) {
  int val = analogRead(pin);

  // 値が想定範囲(0〜1023)外の場合は読み取り異常とみなす
  if (val < ADC_MIN || val > ADC_MAX) {
    Serial.print("[エラー] ");
    Serial.print(label);
    Serial.print(" の値が異常です (取得値: ");
    Serial.print(val);
    Serial.println(")．配線または基板を確認してください．");
    return -1;
  }

  // 値が0に張り付いている場合: GND短絡または未接続の可能性
  if (val == ADC_MIN) {
    Serial.print("[警告] ");
    Serial.print(label);
    Serial.println(" の値が0です．GND側への短絡，または配線未接続の可能性があります．");
  }

  // 値が1023に張り付いている場合: 5V短絡または未接続の可能性
  if (val == ADC_MAX) {
    Serial.print("[警告] ");
    Serial.print(label);
    Serial.println(" の値が1023です．5V側への短絡，または配線未接続の可能性があります．");
  }

  return val;
}
