from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text
import bcrypt

db_connect = create_engine('sqlite:///exemplo.db?check_same_thread=False')

class Login(Resource):
    def login(self):
        conn = db_connect.connect()

        tables = ['Customer', 'Provider']

        # Get email and password from request
        email = request.json.get("Email")
        password = request.json.get("Password")

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        for table in tables:
            # Query to fetch user data based on email
            query = conn.execute(text(f"SELECT name, email, password FROM {table} WHERE email = :email"), {"email": email})
            # Retrieves a single row from the query. If there's no result, it returns None
            user = query.fetchone()

            if user is not None:
                role = table
                break
        
        if user is None:
            return jsonify({"message": "Invalid email"}), 401

        # Extract hashed password from DB
        hashed_password = user.password

        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return jsonify({
                "user": {
                    "Email": user.email,
                    "Name": user.name,
                    "Role": role
                }
            })
        else:
            return jsonify({"message": "Invalid password"}), 401