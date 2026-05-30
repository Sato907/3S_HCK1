/*
 * CdSセル 受光動作検証（A0値のシリアル出力）
 *
 * 配線（計画書 図3.4 の分圧回路に準拠）:
 *   5V  ── CdS セル(GL5516) ──┬── A0       … 明るいほど A0 の値が大きくなる
 *                              └── 10kΩ ── GND
 *
 * 検証の手順:
 *   1. Arduino に書き込み，シリアルモニタ(9600 bps)を開く
 *   2. 手で CdS セルを覆う/外すと A0 の値が変化することを確認する
 */

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println(analogRead(A0));
  delay(100);
}
