import urllib.request, json

url = 'http://127.0.0.1:5000/api/scrape'
data = json.dumps({'limit': 5}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    print('TEST: sending request')
    resp = urllib.request.urlopen(req, timeout=60)
    print('TEST: got response')
    body = resp.read().decode('utf-8')
    print('RESPONSE', body)
except Exception as e:
    print('ERROR', repr(e))
    import traceback
    traceback.print_exc()
