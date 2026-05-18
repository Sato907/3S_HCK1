flowchart TD
    flowchart TD
    %% 開始・終了ノード
    Start(((開始)))
    End(((終了)))

    %% プロセスノード
    Init[初期化: Init]
    Idle[待機: Idle]
    VolumeControl[音量情報送信: VolumeControl]
    Transmitting[BPM情報送信: Transmitting]
    
    %% 分岐ノード
    Detecting{加速度 > 閾値 ?}

    %% フローの定義
    Start -->|電源投入| Init
    Init -->|セットアップ完了| Idle

    %% 音量制御のループ（待機状態からの常時分岐）
    Idle -->|常時実行 / つまみ操作| VolumeControl
    VolumeControl -->|送信完了| Idle

    %% 振り検知とBPM送信のフロー
    Idle -->|デバイスを振る| Detecting
    Detecting -->|No: 加速度 < 閾値| Idle
    Detecting -->|Yes: 加速度 > 閾値| Transmitting
    
    Transmitting -->|BPM情報送信完了 UDP| Idle

    %% 電源オフ
    Idle -->|電源オフ| End

flowchart TD
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]