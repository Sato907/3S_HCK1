# 実装メモ

## LEDMatrix制御について 

* フレームバッファ  
  　LEDMatrix全体を表示するためのデータ形式 

* マジックナンバー  
  　ソースコードに直接記述された具体的な数値のうち、その意図や意味が他のプログラマに伝わりにくいもの． 

* extern  
  　他ファイルで定義されたグローバル変数や関数を，現在のファイルから参照するための修飾子．二重定義エラーを防ぐ．


## 指揮デバイスのデザイン  
寸法  
* Arduino UNO R4  
  　長編68.85mm × 短辺53.34mm  
* GY-291  
  　20×15×3mm  
* スライド式可変抵抗器  [https://akizukidenshi.com/catalog/g/g109238/]  
  　長辺60mm ×　短辺9mm × 高さ5.5mm
* タクトスイッチ  [https://akizukidenshi.com/catalog/g/g103651/]  
・長さ：7mm  　　
・長辺：6.2mm   
・短辺：6.2mm  
・操作部長さ：3.5mm  
・端子間ピッチ：4.5mmピッチ  
・端子外形：0.7×0.3mm 
* 9V電池  
  　幅 26.5 mm × 奥行 17.5 mm × 高さ 48.5 mm  
* 10kΩ抵抗器  
  　長さ約6.3mm、直径約2.3mm　　

* ブレッドボードの大きさ測る　＋10cmくらいが全体

ブレッドボードの上にArduino載せる

内部全体で高さ15mm  

実際に組まないとサイズわからなくないですか？？？？詰み


* 筐体の穴  
  スライド :  高さ15.5mm,  

  タクトスイッチ : 高さ10mm

  BPMは 60 / 90 / 120 / 150 / 180 ですね。コメント追加・定数定義・変更詳細まとめをまとめて行います。




---

## 変更内容の詳細

### [Display.h](HCK1_group/HCK1_group_mywork/Display/Display.h)

| 変更箇所 | 変更前 | 変更後 | 理由 |
|---|---|---|---|
| プリプロセッサ指令 | `# ifndef`, `# include`（`#`後にスペース） | `#ifndef`, `#include` | スペースがあるとコンパイルエラーになるため修正 |
| BPM定数 | なし | `BPM_STEP_1〜5`（60/90/120/150/180）定義追加 | 五段階BPM値をマジックナンバーにしないため |
| `extern ArduinoLEDMatrix matrix` | なし | 追加 | `matrix`は`Display.cpp`で定義されるため、`.ino`から`matrix.begin()`を呼ぶには外部参照宣言が必要 |
| コメント | 最小限 | 各宣言に日本語コメント追加 | |

---

### [Display.cpp](HCK1_group/HCK1_group_mywork/Display/Display.cpp)

| 変更箇所 | 変更前 | 変更後 | 理由 |
|---|---|---|---|
| `# include`スペース | `# include` | `#include` | コンパイルエラー修正 |
| `frameBuffer` | なし（各関数がローカル`uint32_t frame[]`を保持） | `static uint8_t frameBuffer[8][12]`をファイルスコープで定義 | `drawDigit`が複数回呼ばれても1枚の画面に桁を合成するには共有バッファが必要。ローカルバッファでは各桁が独立してレンダリングされ上書きされてしまう |
| `displayBPM` | `drawDigit(bpm, 0)`を1回呼ぶのみ（1桁のみ対応） | 1〜3桁に分解し、中央寄せでX座標を計算して各桁を`drawDigit`に渡す。最後に`renderBitmap`で一括描画 | BPMが2〜3桁（60〜180）のため |
| `drawDigit` | ローカル`uint32_t frame[4]`にビット計算（未完成・中身なし） | 共有`frameBuffer`の該当セルに`font3x5`の値を直接書き込む。境界チェックあり | `uint32_t`のビット演算は不要。`uint8_t`の2次元配列で`renderBitmap`に渡す方がシンプルで可読性が高い |
| `renderBitmap`の引数 | `matrix.renderBitmap(frame, 12, 8)` / `(frame, 8, 12)`が混在（不整合） | `matrix.renderBitmap(frameBuffer, 8, 12)`に統一 | Arduino UNO R4のLEDマトリクスは**8行×12列**であり、引数順は`(bitmap, rows, cols)` |
| `checkUDP` | なし | スタブ定義＋TODOコメント追加 | 通信未実装だが関数宣言は`Display.h`にあるためリンクエラー防止 |
| コメント | 最小限 | 各関数の処理概要・引数説明・計算根拠をブロックコメントで記載 | |

---

### [Display.ino](HCK1_group/HCK1_group_mywork/Display/Display.ino)

| 変更箇所 | 変更前 | 変更後 |
|---|---|---|
| ファイル内容 | 空（1行のみ） | `setup()`で`matrix.begin()`、`loop()`で`checkUDP()`を呼ぶ最小構成を実装。各処理にコメント追加 |

---

## 計画書の不足点（添付資料とのリンク）

添付資料は「変更履歴 Version 1.2」のため、以下は変更履歴に記載された項目と対応付けています。

| # | 不足内容 | 対応する資料箇所 |
|---|---|---|
| 1 | **`matrix.begin()`の呼び出し場所が未定義**。`setup()`で呼ぶ必要があるが、設計書に記載なし | **1.1.3 その他，追記事項** — 「引数なしとなっている関数が実装の際には引数が必要なのではないか」と議論されているが、同様に初期化フローについても設計書への記載が必要 |
| 2 | **`checkUDP()`のパケットフォーマット・BPM取り出し手順が未定義**。受信データからどうBPM値を取り出し`displayBPM()`に渡すかのフローがない | **1.1.2 システムの計画書の変更内容** — 「中継機について使用機材，設計の変更」が記載されているが、Display側が受け取るデータ仕様（フォーマット・プロトコル）に言及がない |
| 3 | **`frameBuffer`（共有バッファ）の設計が計画書に存在しない**。`drawDigit`が`displayBPM`と状態を共有する構造は設計書の関数一覧に表れておらず、実装者が独自判断を迫られる | **1.1.3 その他，追記事項** — グローバル変数の実装に言及があるが、Displayモジュール固有の共有バッファについての記述がない |
| 4 | **BPM値の想定範囲が設計書に未記載**（今回ユーザーへの確認で60/90/120/150/180と判明）。`displayBPM`の入力仕様として桁数・表示フォーマットの定義が必要 | 変更履歴資料には記載なし — 元の計画書（設計書本体）への追記が必要な項目 |



# `matrix.begin()` 関数仕様

## 概要

`matrix.begin()` は Arduino UNO R4 WiFi に内蔵された 12×8 LEDマトリクスを初期化する関数である．
この関数を `setup()` 内で1回呼び出すことで，以降の描画関数が使用可能になる．

## 基本仕様

| 項目 | 内容 |
|---|---|
| ライブラリ | `Arduino_LED_Matrix.h` |
| クラス | `ArduinoLEDMatrix` |
| 関数名 | `begin()` |
| 引数 | なし |
| 戻り値 | なし（`void`） |
| 呼び出し場所 | `setup()` 内で1回のみ |
| 対応ボード | Arduino UNO R4 WiFi（12×8 LEDマトリクス内蔵） |

## 最小構成コード

```cpp
#include "Arduino_LED_Matrix.h"

ArduinoLEDMatrix matrix;

void setup() {
    matrix.begin();  // LEDマトリクスの初期化（必須）
}

void loop() {
    // ここで描画処理を行う
}
```

## `begin()` の後に使用可能な主な関数

| 関数 | 引数 | 用途 |
|---|---|---|
| `loadFrame(data)` | `uint32_t[3]` | 16進数形式のフレームデータを表示 |
| `renderBitmap(frame, rows, cols)` | `byte[8][12]`, `int`, `int` | 2次元配列形式のフレームデータを表示 |
| `play()` | なし | アニメーションを再生 |
| `beginDraw()` / `endDraw()` | なし | ArduinoGraphicsライブラリと組み合わせた描画 |

## フレームデータの形式

### 形式1：2次元配列（直感的）

8行×12列の `byte` 配列で，各要素が `1` ならLED点灯，`0` なら消灯を表す．

```cpp
byte frame[8][12] = {
    { 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0 },
    { 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0 },
    { 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0 },
    { 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 },
    { 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }
};
matrix.renderBitmap(frame, 8, 12);
```

### 形式2：16進数配列（省メモリ）

96ビット分のデータを `uint32_t` × 3個に圧縮した形式．Arduino公式のLED Matrix Editorで自動生成できる．

```cpp
const uint32_t heart[] = { 0x3184a444, 0x44042081, 0x100a0040 };
matrix.loadFrame(heart);
```

### 形式の比較

| 比較項目 | 2次元配列（`byte[8][12]`） | 16進数配列（`uint32_t[3]`） |
|---|---|---|
| 可読性 |  高い（0と1で直感的） | △ 低い（16進数） |
| メモリ使用量 | △ 96バイト |  12バイト |
| 編集のしやすさ |  手作業で編集可能 | △ エディタ推奨 |
| 使用関数 | `renderBitmap()` | `loadFrame()` |




# `UDP.parsePacket()` 関数仕様

## 概要

`UDP.parsePacket()` は受信バッファ内の次に利用可能なUDPパケットの存在を確認し，
パケットが存在する場合はそのサイズ（バイト数）を返す関数である．
`UDP.read()` でパケットの内容を読み取る前に，必ずこの関数を呼び出す必要がある．

## 基本仕様

| 項目 | 内容 |
|---|---|
| ライブラリ | `WiFi.h` / `WiFiNINA.h` / `WiFiS3.h`（ボードにより異なる） |
| クラス | `WiFiUDP` |
| 関数名 | `parsePacket()` |
| 引数 | なし |
| 戻り値 | `int`（パケットサイズ：バイト数） |
| パケットなしの場合 | `0` を返す |

## 戻り値の意味

| 戻り値 | 意味 |
|---|---|
| `0` | 受信パケットなし |
| `1以上` | 受信したパケットのサイズ（バイト数） |

## 呼び出し順序

`parsePacket()` はUDP通信の受信処理において以下の順序で使用する．

1. `Udp.begin(port)` — 指定ポートでUDP通信を開始
2. `Udp.parsePacket()` — 受信パケットの有無を確認
3. `Udp.read()` — パケットの内容を読み取る
4. `Udp.remoteIP()` — 送信元のIPアドレスを取得
5. `Udp.remotePort()` — 送信元のポート番号を取得

**重要：** `parsePacket()` を呼ばずに `read()` を呼んでもデータは読み取れない．

## 最小構成コード

```cpp
#include <WiFiS3.h>  // Arduino UNO R4 WiFi の場合

WiFiUDP Udp;
unsigned int localPort = 4210;
char incomingPacket[256];

void setup() {
    Serial.begin(115200);

    // Wi-Fi接続処理（省略）

    Udp.begin(localPort);  // UDPの受信開始
}

void loop() {
    int packetSize = Udp.parsePacket();  // パケットの有無を確認

    if (packetSize) {
        // パケットが存在する場合
        Serial.print("受信サイズ: ");
        Serial.print(packetSize);
        Serial.print(" bytes, 送信元: ");
        Serial.print(Udp.remoteIP());
        Serial.print(":");
        Serial.println(Udp.remotePort());

        // パケットの内容を読み取る
        int len = Udp.read(incomingPacket, 255);
        if (len > 0) {
            incomingPacket[len] = '\0';  // 文字列終端
        }
        Serial.print("内容: ");
        Serial.println(incomingPacket);
    }
}
```

## `parsePacket()` の後に使用可能な主な関数

| 関数 | 引数 | 戻り値 | 用途 |
|---|---|---|---|
| `read()` | なし | `int`（1バイト） | 1文字ずつ読み取る |
| `read(buffer, len)` | `char*`, `int` | `int`（読み取りバイト数） | バッファに一括読み取り |
| `remoteIP()` | なし | `IPAddress` | 送信元のIPアドレスを取得 |
| `remotePort()` | なし | `int` | 送信元のポート番号を取得 |
| `available()` | なし | `int` | バッファ内の残りバイト数を取得 |
| `peek()` | なし | `int`（1バイト） | 次の1バイトを消費せずに確認 |

## 今回のシステムでの使用例

観覧車デバイス（中継機）がBPM・音量データをUDPで送信し，
楽器デバイスが受信する場合の例を示す．

```cpp
void loop() {
    int packetSize = Udp.parsePacket();

    if (packetSize) {
        char buffer[64];
        int len = Udp.read(buffer, 63);
        buffer[len] = '\0';

        // 受信データの解析（例："BPM:120" や "VOL:80"）
        if (strncmp(buffer, "BPM:", 4) == 0) {
            int bpm = atoi(buffer + 4);
            // BPMの反映処理
        } else if (strncmp(buffer, "VOL:", 4) == 0) {
            int volume = atoi(buffer + 4);
            // 音量の反映処理
        }
    }
}
```

## 注意事項

- `parsePacket()` は**ノンブロッキング**であり，パケットがなくても処理を止めずに `0` を返す
- UDPは**コネクションレス型**の通信であるため，パケットの到達は保証されない
- `read()` は `parsePacket()` が `0` より大きい値を返した場合にのみ有効である
- 複数パケットが蓄積している場合，`parsePacket()` は1回の呼び出しにつき1パケットのみ処理する

