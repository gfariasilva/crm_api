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
        conn.execute(text("INSERT INTO Service (cpf_customer, cpf_provider, bank_document, materials_document, materials_cost, stay_cost, labor_cost) VALUES (:cpf_customer, :cpf_provider, :bank_document, :materials_document, :materials_cost, :stay_cost, :labor_cost)"), 
            {
                "cpf_customer": request.json['cpf_customer'],
                "cpf_provider": request.json['cpf_provider'],
                "bank_document": request.json.get('bank_document', None),
                "materials_document": request.json.get('materials_document', None),
                "materials_cost": request.json.get('materials_cost', 0),
                "stay_cost": request.json.get('stay_cost', 0),
                "labor_cost": request.json.get('labor_cost', 0)
            }
        )

        # Recuperando o último registro inserido
        result_query = conn.execute(text("SELECT * FROM Service ORDER BY id DESC LIMIT 1"))
        result = [dict(zip(tuple(result_query.keys()), i)) for i in result_query.fetchall()]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        # Atualizando um serviço existente        
        conn.execute(text("UPDATE Service SET bank_document = :bank_document, materials_document = :materials_document, materials_cost = :materials_cost, stay_cost = :stay_cost, labor_cost = :labor_cost WHERE id = :id"), 
            {
                "id": request.json['id'],
                "bank_document": request.json.get('bank_document', None),
                "materials_document": request.json.get('materials_document', None),
                "materials_cost": request.json.get('materials_cost', 0),
                "stay_cost": request.json.get('stay_cost', 0),
                "labor_cost": request.json.get('labor_cost', 0)
            }
        )

        # Recuperando o registro atualizado
        result_query = conn.execute(text("SELECT * FROM Service WHERE id = :id"), {"id": request.json['id']})
        result = [dict(zip(tuple(result_query.keys()), i)) for i in result_query.fetchall()]
        return jsonify(result)
