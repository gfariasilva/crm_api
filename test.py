import requests

url = "http://127.0.0.1:5555/users"

data = {
    "nome": "João Silva",
    "email": "joao.silva@example.com",
    "senha": "senha123",
    "telefone": "11999999999",
    "tipo": "prestador",
    "estado": "SP",
    "valor_estado": 1200.50,
    "tipo_de_cobranca": "material",
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
try:
    print("JSON Response:", response.json())
except Exception:
    print("Resposta não é JSON:", response.text)
