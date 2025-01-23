from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import create_engine, text

db_connect = create_engine('sqlite:///exemplo.db')

class Services(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute(text("SELECT * FROM Service"))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def post(self):
        conn = db_connect.connect()

        conn.execute(
            text("insert into Service values(null, :cpf_customer, :cpf_provider, :bank_document, :materials_documen, :materials, :stay, :labor)"), 
            {
                "cpf_customer": request.json['cpf_customer'],
                "cpf_provider": request.json['cpf_providerame'],
                "bank_document": request.json['bank_document'],
                "materials_document": request.json['materials_document'],
                "materials": request.json['materials'],
                "stay": request.json['stay'],
                "labor": request.json['labor']
            }
        )

        conn.connection.commit()  

        query = conn.execute(text('SELECT * FROM Service order by id DESC LIMIT 1'))

        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

    def put(self):
        conn = db_connect.connect()

        conn.execute(
            text("update Service set bank_document = :bank_document, materials_document = :materials_document, materials = :materials, stay = :stay, labor = :labor WHERE id = :id"), 
            {
                "cep": request.json['cep'],
                "id": request.json['id'],
                "neighborhood": request.json['neighborhood'],
                "street": request.json['street'],
                "state": request.json['state']
            }
        )

        conn.connection.commit()  

        query = conn.execute(text("select * from Service where id = :id"), {"id": request.json['id']})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)
