from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text

db_connect = create_engine('sqlite:///exemplo.db')

class Providers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT Provider.*, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.cpf"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        conn.execute(
            text("insert into Provider values(:cpf, :name, :email, :password, :phone, :budget, null)"), 
            {
                "cpf": request.json['cpf'],
                "name": request.json['name'],
                "email": request.json['email'],
                "password": request.json['password'],
                "phone": request.json['phone'],
                "budget": request.json['budget']
            }
        )

        conn.execute(
            text("insert into Address values(:cep, :cpf, :neighborhood, :street, :city, :state, null)"), 
            {
                "cep": request.json['cep'],
                "cpf": request.json['cpf'],
                "neighborhood": request.json['neighborhood'],
                "street": request.json['street'],
                "state": request.json['state']
            }
        )

        conn.connection.commit()  

        query = conn.execute(
            text('SELECT Provider.*, Address.* FROM Provider JOIN Address ON Provider.cpf = Address.cpf WHERE Provider.cpf = :cpf'),
            {'cpf': request.json['cpf']})

        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        conn.execute(
            text("update Provider set email = :email, phone = :phone, budget = :budget WHERE cpf = :cpf"), 
            {
                "email": request.json['email'],
                "phone": request.json['phone'],
                "budget": request.json['budget']
            }
        )

        conn.execute(
            text("update Adress set cep = :cep, neighborhood = :neighborhood, street = :street, state = :state WHERE cpf = :cpf"), 
            {
                "cep": request.json['cep'],
                "cpf": request.json['cpf'],
                "neighborhood": request.json['neighborhood'],
                "street": request.json['street'],
                "state": request.json['state']
            }
        )

        conn.connection.commit()  

        query = conn.execute(
            text('SELECT Provider.*, Address.* FROM Provider JOIN Address ON Customer.cpf = Address.cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)