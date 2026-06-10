/*
 * タクトスイッチ 動作検証プログラム
 */

// ピン定義
const int BUTTON_PIN = 3;            // タクトスイッチ: D3（shiki_device.ino と同じ）

// チャタリング除去
const unsigned long debounceDelay = 50;  // ボタン状態確定までの待ち[ms]

// 状態変数
int           lastButtonReading = HIGH;  // 直近に読み取った生の入力（プルアップなので既定 HIGH）
int           buttonState       = HIGH;  // 確定したボタン状態
unsigned long lastDebounceTime  = 0;     // 最後に入力変化を観測した時刻[ms]

// 押下回数のカウンタ
unsigned long pressCount = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  pinMode(BUTTON_PIN, INPUT);  // 外部 10kΩ プルアップを使用（押下で LOW）

  Serial.println("=== タクトスイッチ 動作検証 ===");
  Serial.println("タクトスイッチ: D3（押下=LOW / 離し=HIGH）");
  Serial.print("起動時の生レベル: ");
  Serial.println(digitalRead(BUTTON_PIN) == LOW ? "LOW(押下)" : "HIGH(離し)");
  Serial.println("ボタンを押す/離すと状態と押下回数を表示します．");
  Serial.println("---------------------------------------------------");
}

void loop() {
  int reading = digitalRead(BUTTON_PIN);

  // 入力が変化したらタイマをリセット（チャタリング除去の起点）
  if (reading != lastButtonReading) {
    lastDebounceTime = millis();
    // 生レベルの変化を表示（配線確認用）
    Serial.print("[生レベル変化] -> ");
    Serial.println(reading == LOW ? "LOW(押下)" : "HIGH(離し)");
  }

  // 一定時間変化がなければ，その値を確定状態として採用
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;

      if (buttonState == LOW) {
        // 確定状態が「押下（LOW）」に変化した瞬間だけカウントする
        pressCount++;
        Serial.print("[確定] 押下 (LOW)  押下回数=");
        Serial.println(pressCount);
      } else {
        Serial.println("[確定] 離し (HIGH)");
      }
    }
  }

  lastButtonReading = reading;
}
