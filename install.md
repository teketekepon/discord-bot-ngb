# 動かし方
かなり大雑把ですが書いておきます。
### Herokuにデプロイして動かす(基本)
1. Discord botアカウントの作成 APIアクセストークンの取得
2. Dropbox 登録 APIアクセストークンの取得
3. gitのインストール
4. Heroku cliのインストール
5. 以下のコマンドを実行
```bash
cd 任意のディレクトリ
heroku login
heroku create アプリ名
heroku config:set ACCESS_TOKEN=["Botのアクセストークン"]
heroku config:set DROPBOX_TOKEN=["Dropbox APIアクセストークン"]
heroku buildpacks:set https://github.com/teketekepon/heroku-buildpack-tesseract
git clone https://github.com/teketekepon/discord-bot-ngb/tree/master
git push heroku master
```
6. Heroku管理画面からdynoをonにする。

おしまい

### Windows環境で動かす
ローカルで動くブランチを用意する予定。
