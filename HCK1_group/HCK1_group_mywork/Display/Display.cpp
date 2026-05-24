# include "Display.h"
# include "Arduino_LED_Matrix.h"

//フォント定義 
const uint8_t font3x5[10][15] = {
  // 0
  {1, 1, 1, 
   1, 0, 1,
   1, 0, 1, 
   1, 0, 1, 
   1, 1, 1},

  // 1
  {0, 1, 0,
   1, 1, 0,
   0, 1, 0,
   0, 1, 0,
   1, 1, 1},
  
  // 2
  {1, 1, 1,
   0, 0, 1,
   1, 1, 1,
   1, 0, 0,
   1, 1, 1},

  // 3
  {1, 1, 1,
   0, 0, 1,
   0, 1, 1,
   0, 0, 1,
   1, 1, 1},
  
  // 4
  {1, 0, 1,
   1, 0, 1,
   1, 1, 1,
   0, 0, 1,
   0, 0, 1},

  // 5
  {1, 1, 1,
   1, 0, 0,
   1, 1, 1,
   0, 0, 1,
   1, 1, 1},

  // 6
  {1, 1, 1,
   1, 0, 0,
   1, 1, 1,
   1, 0, 1,
   1, 1, 1},

  // 7
  {1, 1, 1,
   0, 0, 1,
   0, 0, 1,
   0, 0, 1,
   0, 0, 1},

  // 8
  {1, 1, 1,
   1, 0, 1,
   1, 1, 1,
   1, 0, 1,
   1, 1, 1},

  // 9
  {1, 1, 1,
   1, 0, 1,
   1, 1, 1,
   0, 0, 1,
   1, 1, 1}

};

//LEDMatrixのインスタンス化
ArduinoLEDMatrix matrix;


//関数

void displeyBPM(int bpm){
  //初期化
  uint32_t frame[12] = {0}; 
  matrix.renderBitmap(frame,12,8); 

  drawDugit(bpm,0);
}

void drawDigit(int digit, int x_offset){
  if (digit < 0 || digit > 9) return;  //範囲外

  //フレームバッファ 
  uint32_t frame[4] = {0};

  //font3x5[digit]をframeにマッピング
  for (int y = 0; y < 5; y++){
    for (int x = 0; x < 3; x++){
      if(font3x5[digit][y * 3 + x] == 1){
        //ビット計算
      }
    }
  }

  matrix.renderBitmap(frame,8,12)




}

