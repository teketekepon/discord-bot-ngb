# ナイトガーデン用ディスコードbot
このソフトウェアは、ゲーム「プリンセスコネクト!Re:Dive」のクラン「ナイトガーデン」専用Discordサーバーで運用するBotの為に作られました。
## Ngbについて
ナイトガーデンでは現在、王宮、宮殿、城下町の3つのクランに分かれており、それぞれ専用のチャットルームが用意されています。
そのチャットルームへアクセスするための権限を、ユーザーがいつでも自由に取得できるように作られました。
## SaveResultについて
作業チャンネル上にクラバトログのスクショを張り付けると、Botが[tesseractOCR](https://github.com/tesseract-ocr)を使用して解析し、Excelに自動で書き込む他、凸数をカウントしたりします。
**※注意**
- あらかじめ設定した作業チャンネル以外では動作しません。
- クラバトログのスクショは、被り、漏れを考慮していません。
- 読み取り精度の問題で、現状6割ぐらいしか正しく書き込めません。
## ディスコ上でのコマンド
### Ngb
`/bot`
このコマンドを実行したユーザーに 1:王宮 or 2:宮殿 or 3:城下町 のいずれかの 役職を付与します。
botからレスポンスがあるので、その後 1 2 3 いずれかの半角数字をチャットしてください。
`/role (member ,role)`
引数で指定したメンバーに引数で指定したロールを付与します。
### SaveResult
`/totu`
その日の残凸数を返します。
`/day (day)`
引数で指定した数字の日にExcelの記録位置をセットします。
このコマンドを実行すると記録位置が一律書き換えられるので、元の日に戻して記録をしようとしても、その日の1凸目からになってしまいます。
`/clear (day)`
引数で指定した数字の日、または'day1'～'day6'と'all'のExcelの記録を消去します。
消去が成功すればExcelの記録位置と残凸数もリセットされます。
`/pull`
このコマンドを実行したチャンネル上にExcelファイルをアップロードします。
`/append`
このコマンドを実行したチャンネルを作業チャンネルとします。
`/remove`
作業チャンネルでこのコマンドを実行すると作業チャンネルから除外されます。
`/member (op, *member)`
引数opに対応した操作をExcelのメンバー一覧に適用します。引数memberはスペース区切りで複数指定できます。
op一覧
1. add            メンバーを追加します。
2. remove         メンバーを削除します。
3. clear          すべてのメンバーを削除します。
4. delete         末尾のメンバーを削除します。
## Excel表記ルールについて
凸判定は〇
LA判定はボスごとに
1ボス△　2ボス◆　3ボス□　4ボス◎　5ボス☆
1凸消費でLAを2度行った場合、凸カウントされません。