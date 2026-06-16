from flask import Flask, jsonify, request
import requests
import math

app = Flask(__name__)

CEP_LOJA = "30710040"
LAT_LOJA = -19.9191
LON_LOJA = -43.9386

def get_coords(cep):
    cep = cep.replace("-", "").strip()
    try:
        via = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5).json()
        if "erro" in via:
            return None
        cidade = via.get('localidade', '')
        uf = via.get('uf', '')
        logradouro = via.get('logradouro', '')
        bairro = via.get('bairro', '')
        query = f"{logradouro} {bairro} {cidade} {uf} Brasil"
        resp = requests.get(
            "https://geocode.maps.co/search",
            params={"q": query, "api_key": "6849df7d3b537612390809fao4aedb7"},
            timeout=10
        ).json()
        if not resp:
            return None
        return float(resp[0]["lat"]), float(resp[0]["lon"])
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
    cep2 = request.args.get("cep", "")
    if not cep2:
        return jsonify({"distancia_km": "ERRO"})
    c2 = get_coords(cep2)
    if not c2:
        return jsonify({"distancia_km": "ERRO"})
    dist = haversine((LAT_LOJA, LON_LOJA), c2)
    return jsonify({"distancia_km": dist})

if __name__ == "__main__":
    app.run()
