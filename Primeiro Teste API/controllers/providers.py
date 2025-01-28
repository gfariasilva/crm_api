from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive 
import tempfile
import os

db_connect = create_engine('sqlite:///exemplo.db', connect_args={'check_same_thread': False})

class Providers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT Provider.cpf, Provider.name, Provider.email, Provider.phone, Provider.budget, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())

        # Authenticate with Google Drive
        gauth = GoogleAuth()

        # Try to load saved client credentials
        gauth.LoadCredentialsFile("my_credentials.json")

        if gauth.credentials is None:
            # Authenticate if credentials are not available
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh expired credentials
            gauth.Refresh()
        else:
            # Initialize the saved credentials
            gauth.Authorize()

        # Save the credentials for the next run
        gauth.SaveCredentialsFile("my_credentials.json")

        # Initialize Google Drive instance
        drive = GoogleDrive(gauth)

        if 'file' in request.files and file.filename != '':
            file = request.files['file']
            file_suffix = file.filename[file.filename.find('.'):]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_path = temp_file.name
                file.save(temp_path)
            
        if 'file' in request.files and file.filename != '':
            gfile = drive.CreateFile({'parents': [{'id': '1KQjnQHj4Wmrs4DuAIqdhX-x0_gWEGcF8'}]})
            gfile.SetContentFile(temp_path)
            gfile.Upload()
            file_id = gfile['id']
            file_url = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'

            os.remove(temp_path)
        else:
            file_url = ''

        # Inserir fornecedor
        conn.execute(text("INSERT INTO Provider (cpf, name, email, password, phone, document) VALUES (:cpf, :name, :email, :password, :phone, :document)"),
            {
                "cpf": request.json['cpf'],
                "name": request.json['name'],
                "email": request.json['email'],
                "password": hashed_password,
                "phone": request.json['phone'],
                "document": file_url
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

        #Inserir orçamentos
        for i in request.json['budget']:
            conn.execute(text("INSERT INTO Budget (cpf, state, amount) VALUES (:cpf, :state, :amount)"),
                {
                    "cpf": request.json['cpf'],
                    "state": i['state'],
                    "amount": i['amount']
                }
            )

            conn.connection.commit()

        """ 
        {
            "cpf": cpf,
            "budget": {
                "state": state,
                "amount": amount
            }[]
        }
        """

        # Retornar o fornecedor e endereço inseridos
        query = conn.execute(text('SELECT Provider.cpf, Provider.name, Provider.email, Provider.phone, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf WHERE Provider.cpf = :cpf'),
            {'cpf': request.json['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Authenticate with Google Drive
        gauth = GoogleAuth()

        # Try to load saved client credentials
        gauth.LoadCredentialsFile("my_credentials.json")

        if gauth.credentials is None:
            # Authenticate if credentials are not available
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh expired credentials
            gauth.Refresh()
        else:
            # Initialize the saved credentials
            gauth.Authorize()

        # Save the credentials for the next run
        gauth.SaveCredentialsFile("my_credentials.json")

        # Initialize Google Drive instance
        drive = GoogleDrive(gauth)

        if 'file' in request.files and file.filename != '':
            file = request.files['file']
            file_suffix = file.filename[file.filename.find('.'):]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_path = temp_file.name
                file.save(temp_path)
            
        if 'file' in request.files and file.filename != '':
            gfile = drive.CreateFile({'parents': [{'id': '1KQjnQHj4Wmrs4DuAIqdhX-x0_gWEGcF8'}]})
            gfile.SetContentFile(temp_path)
            gfile.Upload()
            file_id = gfile['id']
            file_url = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'

            os.remove(temp_path)
        else:
            file_url = ''

        # Atualizar fornecedor
        conn.execute(text("UPDATE Provider SET email = :email, phone = :phone, document = :document WHERE cpf = :cpf"),
            {
                "cpf": request.json['cpf'],
                "email": request.json['email'],
                "phone": request.json['phone'],
                "budget": request.json['budget'],
                "document": request.json['document']
            }
        )

        conn.connection.commit()

        # Atualizar endereço
        conn.execute(text("UPDATE Address SET cep = :cep, neighborhood = :neighborhood, street = :street, city = :city, state = :state, number = :number WHERE provider_cpf = :cpf"),
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

        # Retornar o fornecedor e endereço atualizados
        query = conn.execute(text('SELECT Provider.cpf, Provider.name, Provider.email, Provider.phone, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf WHERE Provider.cpf = :cpf'),
            {'cpf': request.json['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)