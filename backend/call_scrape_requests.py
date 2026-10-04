import requests
try:
    r = requests.post('http://127.0.0.1:5000/api/scrape', json={'limit':5}, timeout=30)
    print('status', r.status_code)
    try:
        print(r.json())
    except Exception as e:
        print('text', r.text)
except Exception as e:
    print('ERROR', e)
