from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt

db_connect = create_engine('sqlite:///exemplo.db?check_same_thread=False')

class Login(Resource):
    def post(self):
        conn = db_connect.connect()

        tables = ['Customer', 'Provider']

        # Get email and password from request
        email = request.json.get("Email")
        password = request.json.get("Password")
        print(email, password)

        if not email or not password:
            return {"message": "Email and password are required"}, 400

        for table in tables:
            # Query to fetch user data based on email
            query = conn.execute(text(f"SELECT cpf, name, email, password FROM {table} WHERE email = :email"), {"email": email})
            # Retrieves a single row from the query. If there's no result, it returns None
            user = query.fetchone()

            if user is not None:
                role = table if table != "Customer" else "Client"
                break
        
        if user is None:
            return {"message": "Invalid email"}, 401

        # Extract hashed password from DB
        hashed_password = user.password

        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return {
                    "id": bcrypt.hashpw(str(user.cpf).encode('utf-8'), bcrypt.gensalt()),
                    "email": user.email,
                    "name": user.name,
                    "role": role
            }, 200
        else:
            return {"message": "Invalid password"}, 401