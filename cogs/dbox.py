import os
import dropbox
class TransferData():
    '''
    Dropboxからファイルをダウンロード、アップロードする。
    '''
    def __init__(self):
        self.access_token = os.environ["DROPBOX_TOKEN"]
        self.dbx = dropbox.Dropbox(self.access_token)

    def upload_file(self, file_from, file_to):
        '''
        upload_file(ローカルファイル,Dropbox上の保存先)
        '''
        with open(file_from, 'rb') as f:
            self.dbx.files_upload(f.read(), file_to)

    def download_file(self, file_from, file_to):
        '''
        download_file(Dropbox上のファイル,保存先)
        '''
        if file_from in get_files():
            with open(file_to, 'wb') as f:
                metadata, res = self.dbx.files_download(path=file_from)
                f.write(res.content)

    def get_files(self):
        res = []
        i = self.dbx.files_list_folder('', recursive=True)
        for entry in i.entries:
            ins = type(entry)
            if ins is dropbox.files.FileMetadata:
                res.append(entry)
                #ファイル以外はスキップ
        return res
