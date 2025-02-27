import os
import time
from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive 
import tempfile
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///exemplo.db")
db_connect = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Configurar credenciais do Google Drive
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "my_credentials.json")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

class Customers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("""
            SELECT 
                Client.name, Client.phone, Address.cep, Address.state, 
                Address.street, Address.city, Address.number, Credentials.email, Credentials.role
            FROM Client
            JOIN Address ON Customer.address = Address.id
            JOIN Credentials ON Customer.credentials = Credentials.id
        """))
        
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        conn.close()
        return jsonify(result)

    def authenticate_google_drive(self):
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(GOOGLE_CREDENTIALS_PATH)
        
        if gauth.credentials is None:
            # Perform local webserver authentication if no credentials exist
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            try:
                # Attempt to refresh the token
                gauth.Refresh()
            except Exception as e:
                # If refresh fails, re-authenticate
                print("Token refresh failed. Re-authenticating...")
                gauth.LocalWebserverAuth()
        else:
            # Authorize with existing credentials
            gauth.Authorize()
        
        # Save the new credentials
        gauth.SaveCredentialsFile(GOOGLE_CREDENTIALS_PATH)
        return GoogleDrive(gauth)

    def upload_to_google_drive(self, file):
        if not file or file.filename == '':
            return None
        
        file_suffix = file.filename[file.filename.rfind('.'):]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
            temp_path = temp_file.name
            file.save(temp_path)
        
        drive = self.authenticate_google_drive()
        gfile = drive.CreateFile({'parents': [{'id': GDRIVE_FOLDER_ID}]})
        gfile.SetContentFile(temp_path)
        gfile.Upload()
        
        try:
            os.remove(temp_path)
        except:
            print('It was not possible to delete the file')

        return f"https://drive.google.com/file/d/{gfile['id']}/view?usp=sharing"

    def post(self):
        conn = db_connect.connect()
        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        id_credentials = conn.execute(text("""
            INSERT INTO Credentials (email, password, role)
            VALUES (:email, :password, :role) RETURNING id
        """), {
            "email": request.json['email'],
            "password": hashed_password,
            "role": request.json['role'],
        })

        id_credentials = id_credentials.fetchone()[0]

        id_address = conn.execute(text("""
            INSERT INTO Address (cep, state, street, city, number)
            VALUES (:cep, :state, :street, :city, :number) RETURNING id
        """), {
            "cep": request.json['cep'],
            "state": request.json['state'],
            "street": request.json['street'],
            "city": request.json['city'],
            "number": request.json['number']
        })

        id_address = id_address.fetchone()[0]

        conn.execute(text("""
            INSERT INTO Client (name, address, credentials, phone, document, electricity_bill)
            VALUES (:name, :address, :credentials, :phone, :document, :electricity_bill)
        """), {
            "name": request.json['name'],
            "address": id_address,
            "credentials": id_credentials,
            "phone": request.json['phone'],
            "document": '',
            "electricity_bill": ''
        })
        
        conn.commit()
        
        query = conn.execute(text("""
            SELECT 
                Client.name, Client.phone, Client.electricity_bill, Client.document, 
                Credentials.email, Credentials.role, 
                Address.cep, Address.state, Address.street, Address.city, Address.number
            FROM Client 
            JOIN Address ON Client.address = Address.id 
            JOIN Credentials ON Client.credentials = Credentials.id
            WHERE Credentials.email = :email
        """), {"email": request.json['email']})
        
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        conn.close()
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()
        
        document_url = self.upload_to_google_drive(request.files.get('document'))
        electricity_bill_url = self.upload_to_google_drive(request.files.get('electricity_bill'))

        if document_url == None:
            document_url = ''

        if electricity_bill_url == None:
            electricity_bill_url = ''

        # TER CERTEZA DE QUE O ID VAI VIR NO PAYLOAD (JSON)
        update_data = conn.execute(text("""
            UPDATE Client SET name = :name, phone = :phone, document = :document, electricity_bill = :electricity_bill)
            WHERE id = :id RETURNING credentials, address
        """), {
            "name": request.form['name'],
            "phone": request.form['phone'],
            "id": request.form['id'],
            "document": document_url,
            "electricity_bill": electricity_bill_url
        })

        update_data = update_data.fetchone()

        conn.execute(text("""
            UPDATE Credentials SET email = :email
            WHERE id = :id
        """), {
            "email": request.form['email'],
            "id": update_data['credentials']
        })

        conn.execute(text("""
            UPDATE Address SET cep = :cep, state = :state, street = :street,
            city = :city, number = :number WHERE id = :id
        """), {
            "cep": request.form['cep'],
            "state": request.form['state'],
            "street": request.form['street'],
            "city": request.form['city'],
            "number": request.form['number'],
            "id": update_data['address']
        })
        
        conn.commit()
        
        query = conn.execute(text("""
            SELECT 
                Client.name, Client.phone, Client.electricity_bill, Client.document, 
                Credentials.email, Credentials.role, 
                Address.cep, Address.state, Address.street, Address.city, Address.number
            FROM Client 
            JOIN Address ON Client.address = Address.id 
            JOIN Credentials ON Client.credentials = Credentials.id
            WHERE Credentials.email = :email
        """), {"email": request.form['email']})
        
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        conn.close()
        return jsonify(result)