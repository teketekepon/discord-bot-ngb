import os
import dropbox
TOKEN = os.environ["DROPBOX_TOKEN"]
class TransferData():
    '''
    Dropboxからファイルをダウンロード、アップロードする。
    '''
    def __init__(self, TOKEN):
        self.access_token = TOKEN

    def upload_file(self, file_from, file_to):
        '''
        upload_file(ローカルファイル,Dropbox上の保存先)
        '''
        dbx = dropbox.Dropbox(self.access_token)
        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)

    def download_file(self, file_from, file_to):
        '''
        download_file(Dropbox上のファイル,保存先)
        '''
        dbx = dropbox.Dropbox(self.access_token)
        with open(file_to, 'wb') as f:
            metadata, res = dbx.files_download(path=file_from)
            f.write(res.content)
