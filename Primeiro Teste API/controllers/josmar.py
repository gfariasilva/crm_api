from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt

db_connect = create_engine('sqlite:///exemplo.db', connect_args={'check_same_thread': False})

class Josmar(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT * FROM Josmar"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())

        # Inserir fornecedor
        conn.execute(text("INSERT INTO Josmar (email, password, budget) VALUES (:email, :password, :budget)"),
            {
                "email": request.json['email'],
                "password": hashed_password,
                "budget": request.json['budget']
            }
        )

        conn.connection.commit()

        # Retornar o fornecedor e endereço inseridos
        query = conn.execute(text('SELECT email, budget FROM Josmar'))

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]

        return jsonify(result)