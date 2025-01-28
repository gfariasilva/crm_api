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

        # Checa se o arquivo veio no put
        if 'file' in request.files and file.filename != '':
            file = request.files['file']

            # Detecta o index do ponto '.' no nome do arquivo e pega daí pra frente, extraindo a extensão do arquivo
            file_suffix = file.filename[file.filename.find('.'):]

            # Salva o arquivo localmente em uma pasta temporária do PC
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_path = temp_file.name
                file.save(temp_path)

        try:
            # Checa se o arquivo veio no put
            if 'file' in request.files and file.filename != '':
                # Faz o upload no Google Drive no id de uma pasta predeterminada
                gfile = drive.CreateFile({'parents': [{'id': '1KQjnQHj4Wmrs4DuAIqdhX-x0_gWEGcF8'}]})
                gfile.SetContentFile(temp_path)
                gfile.Upload()
                # Pega o id do arquivo que foi subido
                file_id = gfile['id']
                # Monta a URL do arquivo já no Drive
                file_url = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'

                print(file_url)

                # Tem certeza que o upload já foi feito antes de excluir o arquivo
                time.sleep(1)

                # Exclui o arquivo da pasta temporária
                os.remove(temp_path)
            else:
                file_url = ''

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
            query = conn.execute(text('SELECT Customer.cpf, Customer.name, Customer.email, Customer.phone,, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf'),
                {'cpf': request.form['cpf']}
            )
            result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
            return jsonify(result)

        except Exception as e:
            # Exclui os arquivos temporários
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': str(e)}), 500