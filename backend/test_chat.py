import urllib.request
import json

data = {"pregunta": "cómo crear un taller", "contexto": "general"}
json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8001/api/v1/chat/chat',
    data=json_data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        print(json.dumps(result, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
