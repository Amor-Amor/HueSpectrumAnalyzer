import requests

# Making a PUT request
r = requests.put('http://192.168.0.20/debug/clip.html/api/UWO8pVJA2CFZTSg2eqcpXGFoJ97j5wGvO26kqzgY/lights/1/state / put', data={'on': 'false'})

# check status code for response received
# success code - 200
print(r)

# print content of request
print(r.content)