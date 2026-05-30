#include "Display.h"

// setup() : Arduino起動時に1回だけ実行される初期化処理
// matrix.begin() でLEDマトリクスを有効化する
// （matrix は Display.cpp で定義，Display.h で extern 宣言済み）
void setup() {
  matrix.begin();
}

// loop() : 繰り返し実行されるメインループ
// checkUDP() で中継機からのBPM受信を監視し，受信時に displayBPM() が呼ばれる（実装予定）
void loop() {
  checkUDP();
}
