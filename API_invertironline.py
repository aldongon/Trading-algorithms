import requests
import json
import datetime

def get_token():
    user = ''
    password = ''
    return json.loads(requests.post("https://api.invertironline.com/token", 
                                    data = {"username": user,
                                            "password": password,
                                            "grant_type": "password"}).text)

def refresh_token(refresh):
    return json.loads(requests.post("https://api.invertironline.com/token", 
                      data = {'refresh_token':refresh,
                              'grant_type': 'refresh_token'}).text)

def sell(symbol, price, amount, token, plazo = 't0', valid = None):
    """
    Ejecuta orden de venta.
    plazo:
        't0': contado inmediato
        't1': 24 horas
        't2': 72 horas
    """
    
    # Determinar la fecha de validez para la operacion. Si no se
    # ingresa ningun parametro, utilizar la fecha actual
    if valid == None:
        valid = str(datetime.datetime.today().date())
        
    # Ejecutar la operacion de venta
    r = json.loads(requests.post("https://api.invertironline.com/api/v2/operar/Vender",
                  headers = {"Authorization": "Bearer " + token},
                  data = {"mercado": "bCBA",
                          "simbolo": symbol,
                          "cantidad": amount,
                          "precio": price,
                          "validez": valid,
                          "plazo": plazo}).text)
    return r
    
    
def buy(symbol, price, amount, token, plazo = 't0', valid = None):
    """
    Ejecuta orden de compra.
    plazo:
        't0': contado inmediato
        't1': 24 horas
        't2': 72 horas
    """
    # Determinar la fecha de validez para la operacion. Si no se
    # ingresa ningun parametro, utilizar la fecha actual
    if valid == None:
        valid = str(datetime.datetime.today().date())
        
    # Ejecutar la operacion de compra
    r = json.loads(requests.post("https://api.invertironline.com/api/v2/operar/Comprar",
                  headers = {"Authorization": "Bearer " + token},
                  data = {"mercado": "bCBA",
                          "simbolo": symbol,
                          "cantidad": amount,
                          "precio": price,
                          "validez": valid,
                          "plazo": plazo}).text)
    return r

def get_price(symbol, token):
    return json.loads(requests.get('https://api.invertironline.com/api/v2/bCBA/Titulos/'+ symbol + '/Cotizacion',
                                   headers = {"Authorization":"Bearer "+token}).text)

def get_operation(operation_num, bearer):
    return json.loads(requests.get(url = 'https://api.invertironline.com/api/v2/operaciones/'+operation_num, 
                      headers = {'Authorization': 'Bearer '+bearer}).text)