from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt

db_connect = create_engine('sqlite:///exemplo.db?check_same_thread=False')

class Login(Resource):
    def post(self):
        conn = db_connect.connect()

        tables = ['Customer', 'Provider']

        email = request.json.get("Email")
        password = request.json.get("Password")
        print(email, password)

        if not email or not password:
            return {"message": "Email and password are required"}, 400

        for table in tables:
            query = conn.execute(text(f"SELECT cpf, name, email, password FROM {table} WHERE email = :email"), {"email": email})
            user = query.fetchone()

            if user is not None:
                role = table if table != "Customer" else "Client"
                break
        
        if user is None:
            return {"message": "Invalid email"}, 401

        hashed_password = user.password

        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            result = {
                    "id": str(bcrypt.hashpw(str(user.cpf).encode('utf-8'), bcrypt.gensalt())),
                    "email": user.email,
                    "name": user.name,
                    "role": role.lower()
            }

            return jsonify(result)
        else:
            return {"message": "Invalid password"}, 401