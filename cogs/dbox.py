import os
import dropbox

class TransferData():
    '''
    Dropboxからファイルをダウンロード、アップロードする。
    '''
    ACCESS_TOKEN = os.environ["DROPBOX_TOKEN"]
    def __init__(self):
        self.dbx = dropbox.Dropbox(self.ACCESS_TOKEN)

    def get_files(self):
        '''
        rootディレクトリのファイル一覧を取得する
        '''
        res = []
        i = self.dbx.files_list_folder('', recursive=True)
        for entry in i.entries:
            ins = type(entry)
            if ins is dropbox.files.FileMetadata:
                #ファイル以外はスキップ
                res.append(entry)
        return res

    def upload_file(self, file_from, file_to):
        '''
        upload_file(ローカルファイル,Dropbox上の保存先)
        WriteMode=overwrite を使用してファイルは毎度更新されるようにする
        '''
        with open(file_from, 'rb') as f:
            self.dbx.files_upload(f.read(), file_to,
                mode=dropbox.files.WriteMode.overwrite, mute=True)

    def download_file(self, file_from, file_to):
        '''
        download_file(Dropbox上のファイル,保存先)
        files_fromがdropboxに無い場合Falseが返る
        files_download_to_file(file_to, file_from) でもいい
        '''
        files = self.get_files()
        target = file_from.replace('/', '')
        if target not in files:
            return False
        else:
            with open(file_to, 'wb') as f:
                metadata, res = self.dbx.files_download(path=file_from)
                f.write(res.content)
            return True
