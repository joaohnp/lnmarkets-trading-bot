# main.py
import time
from sys import exit  # Para sair do script de forma limpa

from utils import get_trades, initialize_price

# Inicializa o preço de referência chamando a nova função
highest_price_reference = initialize_price()

# Se a inicialização falhar, o script termina.
if highest_price_reference is None:
    exit()

# O loop que você gosta, agora sem a lógica de setup.
while True:
    try:
        highest_price_reference = get_trades(highest_price_reference)
        time.sleep(10)
    except Exception as e:
        print(e)
        exit()