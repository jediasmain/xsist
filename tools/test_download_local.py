import requests

payload = {"tipo": "NFE", "chave": "35111111111111111111111111111111111111111111"}

r = requests.post("http://127.0.0.1:8765/download", json=payload, timeout=30)
print("HTTP:", r.status_code)
print(r.text)