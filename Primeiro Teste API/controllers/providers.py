import os
import tempfile
from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
GDRIVE_FOLDER_ID = os.getenv('GDRIVE_FOLDER_ID')

db_connect = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

def authenticate_google_drive():
    """Autentica e retorna uma instância do Google Drive."""
    gauth = GoogleAuth()
    
    # Carregar credenciais do arquivo .json salvo
    gauth.LoadCredentialsFile(GOOGLE_CREDENTIALS_PATH)

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(GOOGLE_CREDENTIALS_PATH)

    return GoogleDrive(gauth)

def upload_to_google_drive(file):
    if not file or file.filename == '':
        return None
    
    file_suffix = file.filename[file.filename.rfind('.'):]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
        temp_path = temp_file.name
        file.save(temp_path)
    
    drive = authenticate_google_drive()
    gfile = drive.CreateFile({'parents': [{'id': GDRIVE_FOLDER_ID}]})
    gfile.SetContentFile(temp_path)
    gfile.Upload()
    
    try:
        os.remove(temp_path)
    except:
        print('It was not possible to delete the file')

    return f"https://drive.google.com/file/d/{gfile['id']}/view?usp=sharing"

class Providers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT Provider.cpf, Provider.name, Provider.email, Provider.phone, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()
        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())

        # Inserir fornecedor
        conn.execute(text("INSERT INTO Provider (cpf, name, email, password, phone, document) VALUES (:cpf, :name, :email, :password, :phone, :document)"),
            {
                "cpf": request.json['cpf'],
                "name": request.json['name'],
                "email": request.json['email'],
                "password": hashed_password.decode('utf-8'),
                "phone": request.json['phone'],
                "document": ''
            }
        )
        conn.connection.commit()

        # Inserir endereço
        conn.execute(text("INSERT INTO Address (cep, provider_cpf, neighborhood, street, city, state, number) VALUES (:cep, :provider_cpf, :neighborhood, :street, :city, :state, :number)"),
            {
                "cep": request.json['cep'],
                "provider_cpf": request.json['cpf'],
                "neighborhood": request.json['neighborhood'],
                "street": request.json['street'],
                "city": request.json['city'],
                "state": request.json['state'],
                "number": request.json['number']
            }
        )
        conn.connection.commit()

        # Inserir orçamentos
        for i in request.json['budget']:
            conn.execute(text("INSERT INTO Budget (cpf, state, amount) VALUES (:cpf, :state, :amount)"),
                {
                    "cpf": request.json['cpf'],
                    "state": i['state'],
                    "amount": i['amount']
                }
            )

        conn.connection.commit()

        # Retornar fornecedor inserido
        query = conn.execute(text('SELECT Provider.cpf, Provider.name, Provider.email, Provider.phone, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf WHERE Provider.cpf = :cpf'),
            {'cpf': request.json['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Upload do arquivo para o Google Drive (se houver)
        file_url = upload_to_google_drive(request.files.get('file'))

        # Atualizar fornecedor
        conn.execute(text("UPDATE Provider SET email = :email, phone = :phone, document = :document WHERE cpf = :cpf"),
            {
                "cpf": request.form['cpf'],
                "email": request.form['email'],
                "phone": request.form['phone'],
                "document": file_url
            }
        )
        conn.connection.commit()

        # Atualizar endereço
        conn.execute(text("UPDATE Address SET cep = :cep, neighborhood = :neighborhood, street = :street, city = :city, state = :state, number = :number WHERE provider_cpf = :cpf"),
            {
                "cep": request.form['cep'],
                "cpf": request.form['cpf'],
                "neighborhood": request.form['neighborhood'],
                "street": request.form['street'],
                "city": request.form['city'],
                "state": request.form['state'],
                "number": request.form['number']
            }
        )
        conn.connection.commit()

        # Retornar fornecedor atualizado
        query = conn.execute(text('SELECT Provider.cpf, Provider.name, Provider.email, Provider.phone, Provider.document, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf WHERE Provider.cpf = :cpf'),
            {'cpf': request.form['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)