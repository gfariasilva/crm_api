import requests

url = "http://127.0.0.1:5000/providers"
data = {
    "cpf": 12345678901,
    "name": "João Silva",
    "email": "joao.silva@example.com",
    "password": "senha123",
    "phone": 11999999999,
    "budget": [
        {
            "state": "SP",
            "amount": 5000.00
        },
        {
            "state": "RJ",
            "amount": 3000.00
        }
    ],
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