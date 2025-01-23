from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text

db_connect = create_engine('sqlite:///exemplo.db')

class Customers(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.cpf"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        conn.execute(
            text("insert into Customer values(:cpf, :name, :email, :password, :phone, null, null)"), 
            {
                "cpf": request.json['cpf'],
                "name": request.json['name'],
                "email": request.json['email'],
                "password": request.json['password'],
                "phone": request.json['phone']
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

        query = conn.execute(text('SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']})

        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        conn.execute(
            text("update Customer set email = :email, phone = :phone WHERE cpf = :cpf"), 
            {
                "email": request.json['email'],
                "phone": request.json['phone'],
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
            text('SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

class UserById(Resource):
    def delete(self, id):
        conn = db_connect.connect()
        conn.execute(text("delete from user where id = :id"), {"id": int(id)})
        conn.connection.commit()  
        return {"status": "success"}

    def get(self, id):
        conn = db_connect.connect()
        query = conn.execute(text("select * from user where id = :id"), {"id": int(id)})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)