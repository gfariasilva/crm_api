from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text

db_connect = create_engine('sqlite:///exemplo.db')

class Providers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(
            text("SELECT Provider.*, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf")
        )
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()
        data = request.json

        # Validação básica para garantir que os dados obrigatórios existam
        required_fields = ["cpf", "name", "email", "password", "phone", "budget", "cep", "neighborhood", "street", "city", "state", "number"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Inserir fornecedor
        conn.execute(
            text("INSERT INTO Provider (cpf, name, email, password, phone, budget) VALUES (:cpf, :name, :email, :password, :phone, :budget)"),
            {
                "cpf": data['cpf'],
                "name": data['name'],
                "email": data['email'],
                "password": data['password'],
                "phone": data['phone'],
                "budget": data['budget']
            }
        )

        # Inserir endereço
        conn.execute(
            text("INSERT INTO Address (cep, provider_cpf, neighborhood, street, city, state, number) VALUES (:cep, :provider_cpf, :neighborhood, :street, :city, :state, :number)"),
            {
                "cep": data['cep'],
                "provider_cpf": data['cpf'],
                "neighborhood": data['neighborhood'],
                "street": data['street'],
                "city": data['city'],
                "state": data['state'],
                "number": data['number']
            }
        )

        # Retornar o fornecedor e endereço inseridos
        query = conn.execute(
            text('SELECT Provider.*, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf WHERE Provider.cpf = :cpf'),
            {'cpf': data['cpf']}
        )
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()
        data = request.json

        # Validação básica
        required_fields = ["cpf", "email", "phone", "budget", "cep", "neighborhood", "street", "city", "state", "number"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Atualizar fornecedor
        conn.execute(
            text("UPDATE Provider SET email = :email, phone = :phone, budget = :budget WHERE cpf = :cpf"),
            {
                "cpf": data['cpf'],
                "email": data['email'],
                "phone": data['phone'],
                "budget": data['budget']
            }
        )

        # Atualizar endereço
        conn.execute(
            text("UPDATE Address SET cep = :cep, neighborhood = :neighborhood, street = :street, city = :city, state = :state, number = :number WHERE provider_cpf = :cpf"),
            {
                "cep": data['cep'],
                "provider_cpf": data['cpf'],
                "neighborhood": data['neighborhood'],
                "street": data['street'],
                "city": data['city'],
                "state": data['state'],
                "number": data['number']
            }
        )

        # Retornar o fornecedor e endereço atualizados
        query = conn.execute(
            text('SELECT Provider.*, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.provider_cpf WHERE Provider.cpf = :cpf'),
            {'cpf': data['cpf']}
        )
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)
