from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text

db_connect = create_engine('sqlite:///exemplo.db?check_same_thread=False')

class Customers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf"))

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        # Inserir cliente
        conn.execute(text("INSERT INTO Customer (cpf, name, email, password, phone) VALUES (:cpf, :name, :email, :password, :phone)"),
            {
                "cpf": request.json['cpf'],
                "name": request.json['name'],
                "email": request.json['email'],
                "password": request.json['password'],
                "phone": request.json['phone']
            }
        )

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

        # Retornar o cliente e endereço inseridos
        query = conn.execute(text('SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Atualizar cliente
        conn.execute(text("UPDATE Customer SET email = :email, phone = :phone WHERE cpf = :cpf"),
            {
                "cpf": request.json['cpf'],
                "email": request.json['email'],
                "phone": request.json['phone']
            }
        )

        # Atualizar endereço
        conn.execute(text("UPDATE Address SET cep = :cep, neighborhood = :neighborhood, street = :street, city = :city, state = :state, number = :number WHERE customer_cpf = :cpf"),
            {
                "cep": request.json['cep'],
                "neighborhood": request.json['neighborhood'],
                "street": request.json['street'],
                "city": request.json['city'],
                "state": request.json['state'],
                "number": request.json['number'],
                "cpf": request.json['cpf']
            }
        )

        query = conn.execute(text('SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.customer_cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']}
        )

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)
