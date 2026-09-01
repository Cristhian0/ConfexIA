import urllib.request
import json

test_cases = [
    {"pregunta": "cómo crear un taller", "contexto": "general"},  # Acción específica
    {"pregunta": "dime como hacer", "contexto": "general"},  # Consulta vaga
]

for i, data in enumerate(test_cases, 1):
    print(f"\n--- Test {i}: {data['pregunta']} ---")
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    req = urllib.request.Request(
        'http://localhost:8001/api/v1/chat/chat',
        data=json_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"Status: ✅ {response.status}")
            print(f"Tipo: {result.get('tipo')}")
            print(f"Respuesta: {result.get('respuesta')[:100]}...")
            if result.get('acciones'):
                print(f"Acciones: {len(result['acciones'])} encontradas")
                for accion in result['acciones']:
                    print(f"  - {accion.get('titulo')}: {accion.get('destino')}")
            else:
                print("Acciones: Ninguna")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}")
        error_msg = e.read().decode('utf-8')
        print(f"Error: {error_msg}")
    except Exception as e:
        print(f"❌ Error: {e}")
