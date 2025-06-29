import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_app.modelo_riesgo_credito import simular_credito

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "App Flask en Render funcionando ✅"

@app.route('/simular', methods=['POST'])
def simular():
    try:
        datos = request.get_json()
        resultados = simular_credito(datos)
        if 'tabla_amortizacion' in resultados:
            resultados['tabla_amortizacion'] = resultados['tabla_amortizacion'].to_dict(orient='records')
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
