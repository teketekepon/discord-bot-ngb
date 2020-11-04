# ナイトガーデン用ディスコードBOT

このプロジェクトは、ゲーム「プリンセスコネクト!Re:Dive」のクラン「ナイトガーデン」Discordサーバーで運用するBotの為に作られました。

## 動かし方

[install.md](./install.md) を参照

## 機能説明

### Reserveについて

簡易的な凸予約ツールです。BOSSES変数にボスの名称を入れて使ってください。
Reserveを機能させるためには、チャット埋め込み作成権限が必要です。

#### Reserve コマンド一覧

- `/yoyaku` `/予約` `/凸予約` `/予定`
現在の予約状況をチャットします。
- `/(ボス名)` `/b(ボス番号)` `/boss(ボス番号)`
このコマンドを実行したユーザーを、ボス名の予約キューに追加します。
コメントを入れることも可能です。
- `/clear` `/凸完了` `/完了` `/クリア`
このコマンドを実行したユーザーの予約を削除します。

#### Reserve 使い方

`/(ボス名)`コマンドをチャットして凸りたいボスを宣言します。コメントで予想ダメージや、持ち越しかどうかなどを明記することもできます。
`/yoyaku`コマンドをチャットすると現在予約している人が表示されます。
凸り終わったときや、予約をキャンセルしたいときは`/clear`コマンドをチャットします。

##### Reserve スクリーンショット

![Reserveの使い方](https://user-images.githubusercontent.com/60592959/90522030-33512c80-e1a6-11ea-845c-1b69341399f5.png)

### TotuCountについて

あらかじめ設定した作業チャンネル上にクラバトログのスクショを張り付けると、Botが[tesseractOCR](https://github.com/tesseract-ocr)を使用して解析し、凸カウントします。トリミングされている等の理由で、規定の解像度から外れるとエラーになります。
チャンネルごとにカウントされるため、1つのクランのバトルログは1つのチャンネルに集約してください。
**※1 クラバトログのスクショは被り、漏れを考慮していません。**
**※2 「ダメージ」というユーザー名、または「で」で終わるユーザー名があるとカウントがズレます。**

#### TotuCount コマンド一覧

- `/register`
機能を有効にするチャンネルとして登録するコマンドです。
このコマンドは、manage_channels(チャンネルを編集)できるユーザーのみが使えます。
- `/unregister`
機能を無効にするチャンネルとして登録するコマンドです。
このコマンドは、manage_channels(チャンネルを編集)できるユーザーのみが使えます。
- `/totu` `/zanntotu` `/残凸` `/残り`
残凸数をチャットします。
- `/reset`
残凸数をクリアします。日付が変わったときに使用してください。
- `/add`
凸カウントを増やすコマンドです。
例えば `/add 1` とすると1凸増やします。
- `/sub`
凸カウントを減らすコマンドです。
例えば `/sub 1` とすると1凸減らします。

#### TotuCount 使い方

あらかじめスクショを貼るチャンネルを作り、そのチャンネルで`/register`コマンドをチャットします。
以下の操作はチャンネルごとに動作することに注意してください。
もしも間違えてしまった場合`/unregister`コマンドをチャットして、登録を解除できます。
クラバトログのスクリーンショットをアップロードします。
`/totu`コマンドをチャットし、残りの凸数を確認します。
午前5時を過ぎたら`/reset`コマンドをチャットしてカウントをクリアします。

##### TotuCount スクリーンショット

![TotuCountの使い方](https://user-images.githubusercontent.com/60592959/90522080-4106b200-e1a6-11ea-8987-b1eaec31b03a.png)

##### 対応している解像度

| 解像度(横) | 解像度(縦) | 機種例 |
|-----:|-----:|:---------------------|
| 1280 |  760 | DMM版 windows枠あり   |
| 1280 |  720 | DMM版 windows枠なし   |
| 1123 |  628 |                      |
| 1000 |  565 |                      |
| 1334 |  750 | iPhone 6,7,8         |
| 1920 | 1080 | iPhone 6,7,8 Plus    |
| 2560 | 1440 |                      |
| 2048 | 1536 | iPad Mini            |
| 2224 | 1668 | iPad Pro 10.5inch    |
| 2338 | 1668 | iPad Pro 11inch      |
| 2732 | 2048 | iPad Pro 12.9inch    |
| 2880 | 1440 | Android              |
| 2160 | 1023 |                      |
| 3040 | 1440 | Galaxy系 (左黒帯あり) |
| 1792 |  828 | iPhone XR,11         |
| 2436 | 1125 | iPhone X,XS,11pro    |
| 2688 | 1242 | iPhone XSmax,11Promax|

### Prilogについて

各コマンドの引数にYoutubeのクランバトル動画を渡すことで、[PriLog](https://prilog.jp/)から取得したタイムラインテキストをチャットします。

#### Prilog コマンド一覧

- `/log`
  通常のUBタイミングが書かれたタイムラインテキストをチャットします。
  解析に失敗した場合、エラーメッセージをチャットします。
- `/logb`
  通常のUBタイミングに加え、敵UBのタイミングが書かれたタイムラインテキストをチャットします。
  敵UBのタイミングが読み取れなかった場合、通常のタイムラインテキストになります。
  解析に失敗した場合、エラーメッセージをチャットします。

#### Prilog 使い方

任意のテキストチャンネルで `/log <YoutubeURL>` とチャットします。

### Count_chatについて

`/chat_start`を実行したチャンネルに、朝5時にチャットします。
そのチャットにリアクションで残りの凸数を入力することで、残凸数を数えます。

#### Count_chat コマンド一覧

- `/chat_start`
  このコマンドを実行したチャンネルでチャットカウントを実行します
- `/chat_stop`
  このコマンドを実行したチャンネルでチャットカウントを停止します
- `/count`
  このコマンドを実行したチャンネルのその日のリアクション数から、残り凸数を数えます
- `/count_users`
  このコマンドを実行したチャンネルのその日のリアクションしたユーザーを集計します

### Ngbについて

ナイトガーデンには、王宮、宮殿、城下町の3つの姉妹クランが存在し、それぞれ専用のチャットルームが用意されています。
そのチャットルームへアクセスするための権限を、ユーザーがいつでも自由に取得できるように作られました。
Ngbを動作させるためには役職を編集できる権限が必要です。

#### Ngb コマンド一覧

- `/bot`
このコマンドを実行したユーザーに `1:王宮` `2:宮殿` `3:城下町` のいずれかの役職を付与します。
botからレスポンスがあるので、その後 1 2 3 いずれかの半角数字をチャットしてください。

#### Ngb 使い方

`/bot`とチャットすると、レスポンスが返るので、欲しい役職の数字を半角数字でチャットしてください。

##### Ngb スクリーンショット

![NGBの使い方](https://user-images.githubusercontent.com/60592959/90521898-06047e80-e1a6-11ea-89cd-2c930b07cff2.png)

### LICENSE

Copyright (c) 2020 Takahiro Furukawa

This software is released under the MIT License, see [LICENSE.md](/LICENSE.md).

This software includes the work that is distributed in the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0 "Apache License Version 2.0").
