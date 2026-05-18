# 第二回事後課題

## 課題Ⅰ＿Arduinoのシリアルモニタに正しく波形が表⽰しなさい

* Arduino側の処理
```
#define BAUD 921600 // ボーレート（速め）
#define PIN 0 // A0 アナログ出⼒
#define RESOLUTION 10 // 量⼦化10bit アナログ→デジタルに近似




void setup() {
// マイクのポートを指定
pinMode(PIN, INPUT);

// シリアル通信の速度を設定(bit per second)
Serial.begin(BAUD);

// アナログ読み込みの量⼦化精度
analogReadResolution(RESOLUTION);
}


void loop() {
// A0から読み込み
int d = analogRead(PIN);

// 読み込んだ値を量⼦化精度で規格化し，電圧を取得
float a = (float) d / (pow(2, RESOLUTION)-1)*5.0;

/*
読み取ったアナログ値を1023(10bitで表現できる数値)で割って0/1に変換(規圧化)
→その後電圧5.0Vをかける=電圧値
*/

//波形の中心を0にする
float maxa = 3.3/2.0; // 振幅最⼤値
a = a - maxa; // 中⼼を0にする
float mina = -maxa; // 振幅最⼩値

// シリアルモニタに出⼒
Serial.print("実測値:");
Serial.print(d);
Serial.print(",振幅:");
Serial.print(a);
Serial.print(",最⼤振幅:");
Serial.print(maxa);
Serial.print(",最⼩振幅:");
Serial.println(mina);
}

```

内容
  
```
float a = (float) d / (pow(2, RESOLUTION)-1)*5.0;

pow(10,1.5) //10の1.5乗を計算

・引数
base: 底となる数値 (float)
exponent: 指数となる数値 (float)

・戻り値
べき乗の計算の結果 (double)
```


### 検証

* マイクで音を拾っているのだから物理的距離も関係しているよバーカ

* 量子化する際の電圧5.0→3.3へ  
  　波が小さくなるだけだった．変化無し．角はとれない  
  　Arduinoの動作電圧は5.0Vであるから変更しない方が電圧値の誤差は小さくなる

* 通信速度(#define BAUD 921600)を変えてみる  
  角はとれない，はやくなるだけ

* 実測値を消してみる(漢字の除去)  
  めちゃ近づいた．サンプリング周期が安定したから．  
  →余計なデータ量が減った

* サンプリング周期を固定する(gemini)  
  ジッター(デジタル信号・通信におけるタイミングの揺らぎ)  
  →1秒間に送るデータ量がばらついてしまう  
  →→ delayさせて一定にしようね！！！  

* ノンブロッキング処理(gemini) 
　　　ある処理が完了するまで次の処理を待機させて同期させる  
     点の数を増やす  
     analogRead()自体に100μsかかる →　５００

* 無音時の波形の不安定さ(claude)  
  floatを利用しているから


## 提出課題Ⅱ

* データのbitずれ  
  ```analogRead``` →マイクから読み取る値は10bit  
  ```Serial.write ``` →通信でおくれるサイズは1B  
  * ``` map() ```  map関数は整数。計算の結果、小数が生じる場合、小数部分は単純に切り捨て  

```
【パラメータ】

value: 変換したい数値  
fromLow: 現在の範囲の下限  
fromHigh: 現在の範囲の上限
toLow: 変換後の範囲の下限
toHigh: 変換後の範囲の上限

【戻り値】

変換後の数値 (long)

【ex】
アナログ入力の10ビットの値を8ビットに丸めます。

void setup() {}

void loop() {
  int val = analogRead(0);
  val = map(val, 0, 1023, 0, 255);
  analogWrite(9, val);
}

``` 
* ``` setup() ```は一回のみ 
* if文はマイクの遅延につながるからダメ



### 提出課題Ⅱ_processing_code

```

import processing.serial.*;
int d; 

import ddf.minim.*;
import ddf.minim.ugens.*;
import ddf.minim.ugens.*; //追加

Serial port; // シリアルポート
Minim minim;
AudioOutput out;
Waveform currentWaveform; // 音色格納用変数

// マイクの波形描画用 追加
int[] micData;
int micIndex = 0; //micDataに入っているデータのカウンター

//　楽曲

// 各音の高さ
String[] melody = {
  "C4", "C4", "G4", "G4", "A4", "A4", "G4", 
  "F4", "F4", "E4", "E4", "D4", "D4","C4"
};

// 各音の長さ(拍)
float[] duration = {
  0.9f, 0.9f, 0.9f, 0.9f, 0.9f, 0.9f, 1.8f,
  0.9f, 0.9f, 0.9f, 0.9f, 0.9f, 0.9f, 0.9f
};

// 各音の開始位置
float[] startTime = {
  0.0f, 1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f,
  8.0f, 9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f
};


// 音色を変更するために Instrument インタフェースを実装する
class HackInstrument implements Instrument
{
  Oscil wave;
  Line ampEnv;
  float maxAmp;

  HackInstrument(float frequency, float maxAmp, Waveform wf)
  { 
    // Oscilを使って音信号を作成(周波数, 振幅, 音色)
    wave = new Oscil(frequency, 0, wf);
    // 引数で渡された最大振幅をクラスの変数に代入
    this.maxAmp = maxAmp;
    // 振幅変調を与える(初期値は1から0への減衰)
    ampEnv = new Line();
    // 作成した音信号を振幅変調の出力に送る
    ampEnv.patch(wave.amplitude);
  }

  // コールバック関数: 再生開始
  void noteOn(float duration)
  { 
    // 振幅変調の開始(長さ、開始時の振幅、終了時の振幅)
    ampEnv.activate(duration, this.maxAmp, 0);
    // 音の再生
    wave.patch(out);
  }

  // コールバック関数: 再生停止
  void noteOff()
  { 
    // 再生の停止
    wave.unpatch(out);
  }
}

void setup()
{
  size(800,400);

  // ポートを初期化
  port = new Serial(this, "/dev/cu.usbmodem34B7DA6320602",115200);
  // シリアルポートの初期化
  port.clear();
  //追加
  micData = new int[width];　//マイクデータ保存用の空配列を用意
  
  // minimのインスタンスを用意
  minim = new Minim(this);
  // getLineOutメソッドを呼び出し, AudioOutputオブジェクトを受け取る
  out = minim.getLineOut();
  // テンポの設定、BPM=120
  out.setTempo(120);
  
  // 音色の初期値(正弦波)
  currentWaveform = Waves.SINE;

}

void playSong() 
{
  // 再生を停止
  out.pauseNotes();
  
  // 繰り返し処理を使って異なる音を追加
  for (int i = 0; i < melody.length; i++) {
    out.playNote(startTime[i], duration[i], 
      new HackInstrument(Frequency.ofPitch(melody[i]).asHz(), 0.5f, currentWaveform));
  }
  
  // 再生
  out.resumeNotes();

}

void draw()
{
  background(0);
  //   stroke(255);

  // マイク波形の描画（赤色）追加
  stroke(255, 100, 100); //線の色がアカ
  strokeWeight(2);
  
  //ウィンドウのY座標に変更，height→画面下，0→画面上
  for (int i = 0; i < width - 1; i++) {
    float y1 = map(micData[i], 0, 255, height, 0);
    float y2 = map(micData[i+1], 0, 255, height, 0);
    line(i, y1, i+1, y2);
  }
  
  // 左チャンネルと右チャンネルに入っている波形を描画_楽曲波形(緑)　加筆
  stroke(100,255,100); //線の色がミドリ
  strokeWeight(1);
  for (int i = 0; i < out.bufferSize() - 1; i++){
    line(i, 50 + out.left.get(i) * 50, i + 1, 50 + out.left.get(i + 1) * 50);
    line(i, 150 + out.right.get(i) * 50, i + 1, 150 + out.right.get(i + 1) * 50);
  }
}

//　Arduinoから読み込む　加筆
// データが送信されてきたら呼び出される関数 
void serialEvent(Serial p) 
{
    // ポートからデータを取得
    d = p.read();

    micData[micIndex] = d;
    micIndex++;
    
    //ウィンドウ右端までいったら左端まで戻ってくる
    if (micIndex >= width){
      micIndex = 0;
    }   
}





void keyPressed() 
{
  switch (key)
  {
    
    case 'p':
      // 作成した信号を出力
      playSong();
      break;
    
  }
}

```
* 内容  
  * どうして```width```は宣言なしで使えるの？  
　　システム変数(processingがあらかじめ持ってる変数)だから！  
　　他には```mouseX/Y```,```key```などある  

  * ```out.bufferSize```ってなに！  
  　Minimライブラリが持つ一瞬のデータの個数．widthの代わり