import json
with open('wordlist.txt', 'r') as f:
    words = f.read().splitlines()

words = [x.strip() for x in words]

words = [x for x in words if ((len(x) > 2) and len(x) < 6)]

with open('data.json', 'w') as f:
    f.write(json.dumps(words))

print('created a wordlist with ' + str(len(words)) + ' words')
