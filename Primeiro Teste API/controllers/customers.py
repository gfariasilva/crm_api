import os
import time
from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive 
import tempfile

db_connect = create_engine('sqlite:///exemplo.db?check_same_thread=False')

class Customers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf"))

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())

        # Inserir cliente
        conn.execute(text("INSERT INTO Customer (cpf, name, email, password, phone, document) VALUES (:cpf, :name, :email, :password, :phone)"),
            {
                "cpf": request.json['cpf'],
                "name": request.json['name'],
                "email": request.json['email'],
                "password": hashed_password,
                "phone": request.json['phone']
            }
        )

        conn.connection.commit()

        # Inserir endereço
        conn.execute(text("INSERT INTO Address (cep, customer_cpf, neighborhood, street, city, state, number) VALUES (:cep, :customer_cpf, :neighborhood, :street, :city, :state, :number)"),
            {
                "cep": request.json['cep'],
                "customer_cpf": request.json['cpf'],
                "neighborhood": request.json['neighborhood'],
                "street": request.json['street'],
                "city": request.json['city'],
                "state": request.json['state'],
                "number": request.json['number']
            }
        )

        conn.connection.commit()

        # Retornar o cliente e endereço inseridos
        query = conn.execute(text('SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Autentica com o Google Drive
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Authenticate via local webserver
        drive = GoogleDrive(gauth)

        # Dict que guarda os arquivos advindos do put
        files = {
            'file1': '', 
            'file2': ''
        }

        if len(request.files):
            for i, file in enumerate(request.files.keys()):
                if request.files[file].filename != '':
                    # Detecta o index do ponto '.' no nome do arquivo e pega daí pra frente, extraindo a extensão do arquivo
                    file_suffix = file[request.files[file].filename.find('.'):]

                    # Salva o arquivo localmente em uma pasta temporária do PC
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                        temp_path = temp_file.name
                        request.files[file].save(temp_path)
                        # Salva o caminho do arquivo temporário no dicionário
                        files[f'file{i+1}'] = temp_path

        try:
            # Realiza o upload para o Google Drive
            for key, temp_path in files.items():
                gfile = drive.CreateFile({'parents': [{'id': '1KQjnQHj4Wmrs4DuAIqdhX-x0_gWEGcF8'}]})
                gfile.SetContentFile(temp_path)
                gfile.Upload()

                # Substitui o caminho pelo link do Drive
                file_url = f"https://drive.google.com/file/d/{gfile['id']}/view?usp=sharing"
                files[key] = file_url
                # Remove o arquivo temporário
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except PermissionError as e:
                    print('O arquivo não pôde ser excluído.')

            # Atualizar cliente
            conn.execute(text("UPDATE Customer SET email = :email, phone = :phone WHERE cpf = :cpf"),
                {
                    "cpf": request.form['cpf'],
                    "email": request.form['email'],
                    "phone": request.form['phone']
                }
            )
            conn.connection.commit()

            # Atualizar endereço
            conn.execute(text("UPDATE Address SET cep = :cep, neighborhood = :neighborhood, street = :street, city = :city, state = :state, number = :number WHERE customer_cpf = :cpf"),
                {
                    "cep": request.form['cep'],
                    "neighborhood": request.form['neighborhood'],
                    "street": request.form['street'],
                    "city": request.form['city'],
                    "state": request.form['state'],
                    "number": request.form['number'],
                    "cpf": request.form['cpf']
                }
            )
            conn.connection.commit()

            # Fetch the updated customer details
            query = conn.execute(text('SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf'),
                {'cpf': request.form['cpf']}
            )
            result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
            return jsonify(result)

        except Exception as e:
            # Exclui os arquivos temporários
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': str(e)}), 500