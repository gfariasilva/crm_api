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
        # Implementar tabela Budget_Provider no banco
        query = conn.execute(text("""
            SELECT Provider.name, Provider.phone, Provider.city, Credentials.email, Credentials.role, Budget_Provider.state, Budget_Provider.cost
            FROM Provider 
            JOIN Credentials ON Provider.credentials = Credentials.id
            JOIN Budget_Provider ON Provider.id = Budget_Provider.provider
        """))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()
        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())

        # Inserir credenciais
        credentials_id = conn.execute(text("INSERT INTO Credentials (email, password, role) VALUES (:email, :password, :role) RETURNING id"),
            {
                "email": request.json['email'],
                "password": hashed_password,
                "role": request.json['role']
            }
        )

        credentials_id = credentials_id.fetchone()[0]

        # Inserir fornecedor
        provider_id = conn.execute(text("INSERT INTO Provider (name, credentials, phone, document, city) VALUES (:name, :credentials, :phone, :document, :city) RETURNING id"),
            {
                "name": request.json['name'],
                "credentials": credentials_id,
                "phone": request.json['phone'],
                "document": '',
                "city": request.json['city']
            }
        )
        conn.connection.commit()

        provider_id = provider_id.fetchone()[0]

        # Inserir orçamentos
        for i in request.json['budget']:
            conn.execute(text("INSERT INTO Budget_Provider (provider, state, state_cost) VALUES (:provider, :state, :state_cost)"),
                {
                    "provider": provider_id,
                    "state": i['state'],
                    "state_cost": i['state_cost']
                }
            )

        conn.connection.commit()

        # Retornar fornecedor inserido
        query = conn.execute(text("""
            SELECT Provider.name, Provider.phone, Provider.city, Credentials.email, Credentials.role, Budget_Provider.state, Budget_Provider.cost
            FROM Provider 
            JOIN Credentials ON Provider.credentials = Credentials.id
            JOIN Budget_Provider ON Provider.id = Budget_Provider.provider
            WHERE Provider.id = :id
        """),
            {'id': provider_id}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Upload do arquivo para o Google Drive (se houver)
        file_url = upload_to_google_drive(request.files.get('file'))

        if file_url == None:
            file_url = ''

        # Atualizar fornecedor
        # TER CERTEZA DE QUE O ID VAI VIR NO PAYLOAD (JSON)
        credentials_id = conn.execute(text("UPDATE Provider SET name = :name, phone = :phone, city = :city, document = :document WHERE id = :id RETURNING credentials"),
            {
                "name": request.form['name'],
                "phone": request.form['phone'],
                "city": request.form['city'],
                "document": file_url,
                "id": request.form['id']
            }
        )
        conn.connection.commit()

        credentials_id = credentials_id.fetchone()[0]

        conn.execute(text("UPDATE Credentials SET email = :email WHERE id = :id"),
            {
                "email": request.form['email'],
                "id": credentials_id
            }
        )
        conn.connection.commit()

        # Inserir orçamentos
        for i in request.json['budget']:
            conn.execute(text("UPDATE Budget_Provider SET state_cost = :state_cost WHERE provider = :provider AND state = :state"),
                {
                    "provider": request.form['id'],
                    "state": i['state'],
                    "state_cost": i['state_cost']
                }
            )

        conn.connection.commit()

        # Retornar fornecedor atualizado
        query = conn.execute(text("""
            SELECT Provider.name, Provider.phone, Provider.city, Credentials.email, Credentials.role, Budget_Provider.state, Budget_Provider.cost
            FROM Provider 
            JOIN Credentials ON Provider.credentials = Credentials.id
            JOIN Budget_Provider ON Provider.id = Budget_Provider.provider
            WHERE Provider.id = :id
        """),
            {'id': request.form['id']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)