from flask import Flask, jsonify, request
import requests
import math
import time

app = Flask(__name__)

CEP_LOJA = "30710040"
PRECO_PRODUTO = 199.90

FAIXAS = [
    (7, 25.00),
    (12, 35.00),
    (20, 45.00),
]

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
        query = f"{logradouro}, {bairro}, {cidade}, {uf}, Brasil"
        time.sleep(0.5)
        resp = requests.get(
            "https://photon.komoot.io/api/",
            params={"q": query, "limit": 1, "lang": "pt"},
            timeout=10
        ).json()
        features = resp.get("features", [])
        if not features:
            resp2 = requests.get(
                "https://photon.komoot.io/api/",
                params={"q": f"{cidade}, {uf}, Brasil", "limit": 1, "lang": "pt"},
                timeout=10
            ).json()
            features = resp2.get("features", [])
        if not features:
            return None
        coords = features[0]["geometry"]["coordinates"]
        return float(coords[1]), float(coords[0])
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

@app.route("/frete")
def frete():
    cep2 = request.args.get("cep", "")
    if not cep2:
        return jsonify({"resultado": "CEP inválido. Verifique e tente novamente."})
    c1 = get_coords(CEP_LOJA)
    c2 = get_coords(cep2)
    if not c1 or not c2:
        return jsonify({"resultado": "CEP inválido. Verifique e tente novamente."})
    distancia = haversine(c1, c2)
    for limite, valor_frete in FAIXAS:
        if distancia <= limite:
            total = PRECO_PRODUTO + valor_frete
            return jsonify({"resultado": f"{total:.2f}"})
    return jsonify({"resultado": "Entrega indisponível para essa região."})

if __name__ == "__main__":
    app.run()
