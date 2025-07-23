import os
import tempfile

from dotenv import load_dotenv
from flask import request
from flask_restful import Resource
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from werkzeug.datastructures import FileStorage

load_dotenv()

GOOGLE_CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")


class DocsResource(Resource):

    def authenticate_google_drive(self) -> GoogleDrive:
        """
        Função que autentica com o Google Drive.

        Busca um arquivo "my_credentials.json" que contém os dados para autenticação.
        Caso esse arquivo não exista, busca pelo arquivo "client_secrets.json",
        que contém a credencial original retirada do console do GCP.

        ## Retorno 
            Instância da classe GoogleDrive do módulo pydrive.
        """
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(GOOGLE_CREDENTIALS_PATH)

        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            try:
                gauth.Refresh()
            except Exception as e:
                print("Token refresh failed. Re-authenticating...")
                gauth.LocalWebserverAuth()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile(GOOGLE_CREDENTIALS_PATH)
        return GoogleDrive(gauth)

    def upload_to_google_drive(self, file: FileStorage) -> str | None:
        """
        Faz o upload de um arquivo para o Google Drive.

        ## Parâmetros
            **file** : *FileStorage*.
            Arquivo passado na requisição do front.

        ## Retorno
            Uma *str* contendo a URL do arquivo no Google Drive, caso o processo seja bem-sucedido.

            *None* caso não consiga realizar o upload.
        """
        if not file or file.filename == "":
            return None

        file_suffix = file.filename[file.filename.rfind(".") :]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
            temp_path = temp_file.name
            file.save(temp_path)

        drive = self.authenticate_google_drive()
        gfile = drive.CreateFile({"parents": [{"id": GDRIVE_FOLDER_ID}]})
        gfile.SetContentFile(temp_path)
        gfile.Upload()

        try:
            os.remove(temp_path)
        except:
            print("It was not possible to delete the file")

        return f"https://drive.google.com/file/d/{gfile['id']}/view?usp=sharing"

    def post(self) -> dict:
        if "file" not in request.files:
            return {"error": "Nenhum arquivo enviado."}, 400

        file = request.files["file"]

        uploaded_url = self.upload_to_google_drive(file)

        if uploaded_url:
            return {"message": "Arquivo enviado com sucesso", "url": uploaded_url}, 201
        else:
            return {"error": "Falha ao enviar o arquivo"}, 500
