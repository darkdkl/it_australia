from flask import Flask
import requests
from flask import render_template
from flask import request
app = Flask(__name__)



def get_kladr_id(city):
    suggestSettlement={
        "id": "JsonRpcClient.js",
        "jsonrpc": "2.0",
        "method": "suggestSettlement",
        "params": {
            "query": city,
            "country_code": "RU"
        }
    }
    response = requests.post('https://api.shiptor.ru/public/v1',json=suggestSettlement)
    return response.json()['result'][0]['kladr_id']


def get_calculate_ship(kladr_id_from,kladr_id_to,from_door=None,to_door=None,courier='dpd'):
    calculateShipping={

    "id": "JsonRpcClient.js",
    "jsonrpc": "2.0",
    "method": "calculateShipping",
    "params": {
        
        "kladr_id_from": kladr_id_from,
        "kladr_id": kladr_id_to,
        "courier":courier,
        "length": 60,
        "width": 40,
        "height": 40,
        "weight": 11,
        "cod": 0,
        "declared_cost": 0
            }
            }
        
    response = requests.post('https://api.shiptor.ru/public/v1',json=calculateShipping)
    calculate=response.json()

    if from_door and to_door:
        
        total=calculate['result']['methods'][3]['cost']['total']
        delivery_cost=int(total['sum']) - int(calculate['result']['methods'][0]['cost']['total']['sum'])
        return total['sum'],total['currency'],delivery_cost

    elif from_door:
        total=calculate['result']['methods'][1]['cost']['total']
        delivery_cost=int(total['sum']) - int(calculate['result']['methods'][0]['cost']['total']['sum'])
        
        return total['sum'],total['currency'],delivery_cost

    elif to_door:
        total=calculate['result']['methods'][2]['cost']['total']
        delivery_cost=int(total['sum']) - int(calculate['result']['methods'][0]['cost']['total']['sum'])
        
        return total['sum'],total['currency'],delivery_cost

    else:
        total=calculate['result']['methods'][0]['cost']['total']
        return total['sum'],total['currency'],0

@app.route("/",methods=['GET', 'POST'])
def index():
    delivery_from=request.args.get('delivery_from')
    delivery_to=request.args.get('delivery_to')
    from_door=request.args.get('from_door')
    to_door=request.args.get('to_door')
    context= None
    if delivery_from and delivery_to:
       total,currency,cost_in_door = get_calculate_ship(get_kladr_id(str(delivery_from) ),get_kladr_id(str(delivery_to)),from_door=from_door,to_door=to_door)
       cost_only_delivery= float(total) - float(cost_in_door)
       context={
                'delivery_to':delivery_to,
                'delivery_from':delivery_from,
                'total':total,
                'currency':currency,
                'cost_in_door':cost_in_door,
                'cost_only_delivery':cost_only_delivery
                }
        

    return render_template('index.html',context=context)


if __name__ == "__main__":
       
    app.run()