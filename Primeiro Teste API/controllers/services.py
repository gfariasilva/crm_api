from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text

# Conexão com o banco de dados SQLite
db_connect = create_engine('sqlite:///exemplo.db')

class Services(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT * FROM Service"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.fetchall()]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()
        
        # Inserindo um novo serviço        
        id = conn.execute(text("INSERT INTO Service (client_id, provider_id, initial_date, end_date, provider_cost, total_cost, working_days, status) VALUES (:client_id, :provider_id, :initial_date, :end_date, :provider_cost, :total_cost, :working_days, :status) RETURNING ID"), 
            {
                "client_id": request.json['client_id'],
                "provider_id": request.json['provider_id'],
                "initial_date": request.json['initial_date'],
                "end_date": request.json['end_date'],
                "provider_cost": request.json['provider_cost'],
                "total_cost": request.json['total_cost'],
                "working_days": request.json['working_days'],
                "status": request.json['status']
            }
        )

        id = id.fetchone()[0]

        # Recuperando o último registro inserido
        result_query = conn.execute(text("SELECT * FROM Service WHERE id = :id"), {"id": id})
        result = [dict(zip(tuple(result_query.keys()), i)) for i in result_query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Atualizando um serviço existente        
        conn.execute(text("UPDATE Service SET initial_date = :initial_date, end_date = :end_date, provider_cost = :provider_cost, total_cost = :total_cost, working_days = :working_days, status = :status WHERE id = :id"), 
            {
                "id": request.json['id'],
                "initial_date": request.json['initial_date'],
                "end_date": request.json['end_date'],
                "provider_cost": request.json['provider_cost'],
                "total_cost": request.json['total_cost'],
                "working_days": request.json['working_days'],
                "status": request.json['status']
            }
        )

        # Recuperando o registro atualizado
        result_query = conn.execute(text("SELECT * FROM Service WHERE id = :id"), {"id": request.json['id']})
        result = [dict(zip(tuple(result_query.keys()), i)) for i in result_query.fetchall()]
        return jsonify(result)
