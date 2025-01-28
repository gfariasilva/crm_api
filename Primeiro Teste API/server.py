from flask import Flask
from flask_restful import Api
from controllers.customers import Customers
from controllers.providers import Providers
from controllers.services import Services
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(Customers, '/customers') 
api.add_resource(Providers, '/providers') 
api.add_resource(Services, '/services') 

if __name__ == '__main__':
    app.run()