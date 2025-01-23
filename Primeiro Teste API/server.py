from flask import Flask
from flask_restful import Api
from controllers.customers import Customers, UserById
from controllers.providers import Providers
from controllers.services import Services

app = Flask(__name__)
api = Api(app)

api.add_resource(Customers, '/customers') 
api.add_resource(Providers, '/providers') 
api.add_resource(Services, '/services') 
api.add_resource(UserById, '/users/<id>') 

if __name__ == '__main__':
    app.run()