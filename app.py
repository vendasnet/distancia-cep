from flask import Flask, jsonify, request
import requests
import math
import time

app = Flask(__name__)

def get_coords(cep):
    cep = cep.replace("-", "").strip()
    try:
        via = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5).json()
        if "erro" in via:
            return None
        endereco = f"{via.get('logradouro', '')}, {via['localidade']}, {via['uf']}, Brasil"
        time.sleep(1)
        nom = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": endereco, "format": "json", "limit": 1},
            headers={"User-Agent": "distancia-cep-app/1.0 (contato@email.com)"},
            timeout=10
        ).json()
        if not nom:
            return None
        return float(nom[0]["lat"]), float(nom[0]["lon"])
    except Exception:
        return None

def haversine(c1, c2):
    R = 6371
    lat1, lon1 = math.radians(c1[0]), math.radians(c1[1])
    lat2, lon2 = math.radians(c2[0]), math.radians(c2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return round(R * 2 * math.asin(math.sqrt(a)), 1)

@app.route("/distancia")
def distancia():
    cep1 = request.args.get("cep1", "30710040")
    cep2 = request.args.get("cep2", "")
    if not cep2:
        return jsonify({"erro": "CEP do cliente não informado"}), 400
    c1 = get_coords(cep1)
    c2 = get_coords(cep2)
    if not c1 or not c2:
        return jsonify({"distancia_km": "ERRO"})
    return jsonify({"distancia_km": haversine(c1, c2)})

if __name__ == "__main__":
    app.run()
