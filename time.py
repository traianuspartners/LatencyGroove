import requests
import time

# URL dell'API per ottenere il server time di Bybit
url = "https://api.bybit.com/v2/public/time"

# Misura l'istante prima della richiesta
start_time = time.time()

# Esegue la richiesta GET all'API
response = requests.get(url)

# Misura l'istante dopo la risposta
end_time = time.time()

# Calcola la RTT latency
rtt_latency = (end_time - start_time) * 1000  # Converti in millisecondi

print(f"RTT Latency: {rtt_latency} ms")

# Assicurati che la risposta sia OK per validare il test
if response.status_code == 200:
    print("Risposta ricevuta correttamente.")
else:
    print("Problema nella richiesta. Status Code:", response.status_code)
