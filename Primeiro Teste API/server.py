from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine, text
from json import dumps

db_connect = create_engine('sqlite:///exemplo.db')
app = Flask(__name__)
api = Api(app)


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

        query = conn.execute(
            text('SELECT Customer.*, Address.* FROM Customer JOIN Address ON Customer.cpf = Address.cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

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

        query = conn.execute(
            text('SELECT Provider.*, Address.* FROM Provider JOIN Address ON Customer.cpf = Address.cpf WHERE Customer.cpf = :cpf'),
            {'cpf': request.json['cpf']})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

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

        query = conn.execute(text("select * from Service where id = :id"), {"id": request.json['id']})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

class UserById(Resource):
    def delete(self, id):
        conn = db_connect.connect()
        conn.execute(text("delete from user where id = :id"), {"id": int(id)})
        return {"status": "success"}

    def get(self, id):
        conn = db_connect.connect()
        query = conn.execute(text("select * from user where id = :id"), {"id": int(id)})
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return jsonify(result)

api.add_resource(Customers, '/customers') 
api.add_resource(Providers, '/providers') 
api.add_resource(Services, '/services') 
api.add_resource(UserById, '/users/<id>') 

if __name__ == '__main__':
    app.run()
