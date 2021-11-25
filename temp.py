import json, random 


file = open('Data/shop.json')

data = json.load(file)

count = 0
for d in data:
    data[d]['Discount'] = 1
    

json.dump(data, open('Data/shop.json', 'w'), indent = 4)
