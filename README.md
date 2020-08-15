# ナイトガーデン用ディスコードBOT

このソフトウェアは、ゲーム「プリンセスコネクト!Re:Dive」のクラン「ナイトガーデン」専用Discordサーバーで運用するBotの為に作られました。
このドキュメントでは、各スクリプトの動作説明をします。

## Ngbについて
ナイトガーデンでは現在、王宮、宮殿、城下町の3つのクランに分かれており、それぞれ専用のチャットルームが用意されています。
そのチャットルームへアクセスするための権限を、ユーザーがいつでも自由に取得できるように作られました。
Ngbを動作させるためには役職を編集できる権限が必要です。
#### コマンド一覧
- `/bot`
このコマンドを実行したユーザーに `1:王宮` `2:宮殿` `3:城下町` のいずれかの役職を付与します。
botからレスポンスがあるので、その後 1 2 3 いずれかの半角数字をチャットしてください。
- `/role (member ,role)`
引数で指定したメンバーに引数で指定したロールを付与します。
#### 使い方
`/bot`とチャットすると、レスポンスが返るので、欲しい役職の数字を半角数字でチャットしてください。

##### スクリーンショット
![NGBの使い方](src/ngb-1.png)

## Reserveについて
簡易的な凸予約ツールです。ソースのBOSSES変数にボスの名称を入れて使ってください。
#### コマンド一覧
- `/yoyaku` `/予約` `/凸予約` `/予定`
現在の予約状況を返します。
- `/(ボス名)` `/b(ボス番号)` `/boss(ボス番号)`
このコマンドを実行したユーザーを、ボス名の予約キューに追加します。
コメントを入れることも可能です。
- `/clear` `/凸完了` `/完了` `/クリア`
このコマンドを実行したユーザーの予約を削除します。
#### 使い方
`/(ボス名)`コマンドをチャットして凸りたいボスを宣言します。コメントで予想ダメージや、持ち越しかどうかなどを明記することもできます。
`/yoyaku`コマンドをチャットすると現在予約している人が表示されます。
凸り終わったときや、予約をキャンセルしたいときは`/clear`コマンドをチャットします。
##### スクリーンショット
![Reserveの使い方](src/reserve-1.png)

## TotuCountについて
あらかじめ設定した作業チャンネル上にクラバトログのスクショを張り付けると、Botが[tesseractOCR](https://github.com/tesseract-ocr)を使用して解析し、凸カウントします。トリミングされている等の理由で、規定の解像度から外れるとエラーになります。
チャンネルごとにカウントされるため、1つのクランのバトルログは1つのチャンネルに集約してください。
**※1 クラバトログのスクショは被り、漏れを考慮していません。**
**※2 「ダメージ」というユーザー名、または「で」で終わるユーザー名があるとカウントがズレます。**
#### コマンド一覧
- `/register`
機能を有効にするチャンネルとして登録するコマンドです。
このコマンドは、manage_channels(チャンネルを編集)できるユーザーのみが使えます。
- `/unregister`
機能を無効にするチャンネルとして登録するコマンドです。
このコマンドは、manage_channels(チャンネルを編集)できるユーザーのみが使えます。
- `/totu` `/zanntotu` `/残凸` `/残り`
残凸数をメッセージで返します。
- `/reset`
残凸数をクリアします。日付が変わったときに使用してください。
- `/add`
凸カウントを増やすコマンドです。
例えば `/add 1` とすると1凸増やします。
- `/sub`
凸カウントを減らすコマンドです。
例えば `/sub 1` とすると1凸減らします。
#### 使い方
あらかじめスクショを貼るチャンネルを作り、そのチャンネルで`/register`コマンドをチャットします。
以下の操作はチャンネルごとに動作することに注意してください。
もしも間違えてしまった場合`/unregister`コマンドをチャットして、登録を解除できます。
クラバトログのスクリーンショットをアップロードします。
`/totu`コマンドをチャットし、残りの凸数を確認します。
午前5時を過ぎたら`/reset`コマンドをチャットしてカウントをクリアします。

##### スクリーンショット
![TotuCountの使い方](src/totu-1.png)
##### 対応している解像度
| 解像度(縦) | 解像度(横) | 機種例 |
|-----:|-----:|:--------------------|
| 760  | 1280 | DMM版 windows枠あり   |
| 720  | 1280 | DMM版 windows枠なし   |
| 750  | 1334 | iPhone 6,7,8         |
| 1080 | 1920 | Full HD              |
| 1536 | 2048 | iPad Mini            |
| 1668 | 2224 | iPad Pro 10.5inch    |
| 2048 | 2732 | iPad Pro 12.9inch    |
| 1440 | 2880 | Android              |
| 1440 | 3040 | Galaxy系 (左黒帯あり)     |
| 828  | 1792 | iPhone XR,11         |
| 1125 | 2436 | iPhone X,XS,11pro    |
| 1242 | 2688 | iPhone XSmax,11Promax|

***
LICENSE
This software includes the work that is distributed in the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0, "Apache License Version 2.0").
