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
            SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone, Address.*
            FROM Customer
            JOIN Address ON Customer.cpf = Address.customer_cpf
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
        
        conn.execute(text("""
            INSERT INTO Customer (cpf, name, email, password, phone, document, electricity_bill)
            VALUES (:cpf, :name, :email, :password, :phone, :document, :electricity_bill)
        """), {
            "cpf": request.json['cpf'],
            "name": request.json['name'],
            "email": request.json['email'],
            "password": hashed_password,
            "phone": request.json['phone'],
            "document": '',
            "electricity_bill": ''
        })
        
        conn.execute(text("""
            INSERT INTO Address (cep, customer_cpf, neighborhood, street, city, state, number)
            VALUES (:cep, :customer_cpf, :neighborhood, :street, :city, :state, :number)
        """), {
            "cep": request.json['cep'],
            "customer_cpf": request.json['cpf'],
            "neighborhood": request.json['neighborhood'],
            "street": request.json['street'],
            "city": request.json['city'],
            "state": request.json['state'],
            "number": request.json['number']
        })
        
        conn.commit()
        
        query = conn.execute(text("""
            SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone, Address.*
            FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf
        """), {"cpf": request.json['cpf']})
        
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        conn.close()
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()
        
        document_url = self.upload_to_google_drive(request.files.get('document'))
        electricity_bill_url = self.upload_to_google_drive(request.files.get('electricity_bill'))
        
        conn.execute(text("""
            UPDATE Customer SET email = :email, phone = :phone,
            document = COALESCE(:document, document),
            electricity_bill = COALESCE(:electricity_bill, electricity_bill)
            WHERE cpf = :cpf
        """), {
            "cpf": request.form['cpf'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "document": document_url,
            "electricity_bill": electricity_bill_url
        })
        
        conn.execute(text("""
            UPDATE Address SET cep = :cep, neighborhood = :neighborhood, street = :street,
            city = :city, state = :state, number = :number WHERE customer_cpf = :cpf
        """), {
            "cep": request.form['cep'],
            "neighborhood": request.form['neighborhood'],
            "street": request.form['street'],
            "city": request.form['city'],
            "state": request.form['state'],
            "number": request.form['number'],
            "cpf": request.form['cpf']
        })
        
        conn.commit()
        
        query = conn.execute(text("""
            SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone, Customer.document, Customer.electricity_bill, Address.*
            FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf
        """), {"cpf": request.form['cpf']})
        
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        conn.close()
        return jsonify(result)