import requests

url = "http://127.0.0.1:5000/users"
data = {
    "name": "John Doe",
    "email": "johndoe@example.com"
}

response = requests.post(url, json=data)

print(response.status_code)  # Should return 200 if successful
print(response.json())       # Should return the created user record
