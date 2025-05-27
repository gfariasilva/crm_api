from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt

db_connect = create_engine('sqlite:///exemplo.db', connect_args={'check_same_thread': False})

class Admin(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("""
            SELECT Admin.tax, Credentials.email, Credentials.role
            FROM Admin 
            JOIN Credentials ON Admin.credentials = Credentials.id
        """))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())

        # Inserir credenciais
        id = conn.execute(text("INSERT INTO Credentials (email, password, role) VALUES (:email, :password, :role) RETURNING id"),
            {
                "email": request.json['email'],
                "password": hashed_password,
                "role": request.json['role']
            }
        )

        id = id.fetchone()[0]

        # Inserir budget no Admin
        conn.execute(text("INSERT INTO Admin (credentials, tax) VALUES (:credentials, :tax)"),
            {
                "credentials": id,
                "tax": request.json['tax']
            }
        )

        conn.connection.commit()

        # Retornar o admin inserido
        query = conn.execute(text("""
            SELECT Admin.tax, Credentials.emal, Credentials.role
            FROM Admin 
            JOIN Credentials ON Admin.credentials = Credentials.id
        """))

        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]

        return jsonify(result)