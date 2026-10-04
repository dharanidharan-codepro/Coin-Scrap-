import urllib.request
resp = urllib.request.urlopen('http://127.0.0.1:5000/api/health')
print(resp.read().decode())
