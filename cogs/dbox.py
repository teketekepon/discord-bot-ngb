# -*- coding: utf-8 -*-
import os
import dropbox

class TransferData():
    """
    Dropboxからファイルをダウンロード、アップロードする。
    """
    # DROPBOX_TOKENはHeroku環境変数にしまっておく。
    ACCESS_TOKEN = os.environ["DROPBOX_TOKEN"]
    def __init__(self):
        self.dbx = dropbox.Dropbox(self.ACCESS_TOKEN)

    def upload_file(self, file_from, file_to):
        """
        upload_file(アップロードするファイル,Dropbox上の保存先)
        WriteMode.overwrite を使用してファイルは毎度更新されるようにする
        """
        mode = dropbox.files.WriteMode.overwrite
        with open(file_from, 'rb') as f:
            try:
                res = self.dbx.files_upload(f.read(), file_to,
                    mode=mode, mute=True)
            except dropbox.exceptions.ApiError as err:
                print(f'error {err}')
                return None
        return res

    def download_file(self, file_from, file_to):
        """
        download_file(Dropbox上のファイル,保存先)
        files_fromがdropboxに無い場合Falseが返る
        files_download_to_file(file_to, file_from) でもいい
        """
        with open(file_to, 'wb') as f:
            try:
                md, res = self.dbx.files_download(file_from)
                f.write(res.content)
            except dropbox.exceptions.ApiError as err:
                print(f'error {err}')
                return False
        return True
