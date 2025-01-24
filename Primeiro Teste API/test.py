import requests

url = "http://127.0.0.1:5000/customers"
data = {
    "cpf": 12345678900,  
    "name": "João Silva",
    "email": "joao.silva@example.com",
    "password": "senha123",
    "phone": 11987654321,  
    "cep": 12345000,  
    "neighborhood": "Centro",
    "street": "Rua das Flores",
    "city": "São Paulo",  
    "state": "SP",
    "number": 123  
}


response = requests.post(url, json=data)

print(response.status_code)  
print(response.json())       
