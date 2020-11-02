# 動かし方

かなり大雑把ですが書いておきます。

## Herokuにデプロイして動かす(基本)

1. Discord botアカウントの作成 APIアクセストークンの取得
    [qiitaの記事](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)で丁寧に解説してくださってます。
2. Dropbox 登録 APIアクセストークンの取得
    [Dropbox開発者向け情報](https://www.dropbox.com/developers)からアプリを作成したのち、appコンソールからトークンを取得できます。
3. PriLog APIアクセストークンの取得
    [PriLog](https://prilog.jp/)機能を利用したい場合、Twitterにて製作者[@PriLog_R](https://twitter.com/PriLog_R)さんにDMで問い合わせてください。
4. ターミナルでgitのインストール
5. Heroku cliのインストール
    手順3,4は[こちら](https://devcenter.heroku.com/articles/heroku-cli)を参照してください
6. 以下のコマンドを実行

    ```bash
    cd 任意のディレクトリ
    heroku login
    heroku create アプリ名
    heroku config:set ACCESS_TOKEN=["Botのアクセストークン"]
    heroku config:set DROPBOX_TOKEN=["Dropbox APIアクセストークン"]
    heroku config:set PRILOG_TOKEN=["PriLog APIアクセストークン"]
    heroku buildpacks:set https://github.com/teketekepon/heroku-buildpack-tesseract
    git clone https://github.com/teketekepon/discord-bot-ngb/tree/master
    git push heroku master
    ```

7. Heroku管理画面からdynoをonにする。

以上
1.で作成したbotを任意のサーバーに招待してお使いください。
