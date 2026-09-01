import httpx

# Send file to import endpoint
url = 'http://localhost:8001/api/v1/importacion/excel/lotes'
with open('ejemplo_importacion_lotes.xlsx','rb') as f:
    files = {'file': ('ejemplo_importacion_lotes.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    resp = httpx.post(url, files=files, timeout=60.0)
    print('STATUS', resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
