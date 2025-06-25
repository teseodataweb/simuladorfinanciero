from flask import Flask, request, jsonify
from flask_cors import CORS
from modelo_riesgo_credito import simular_credito

app = Flask(__name__)
CORS(app)

@app.route('/simular', methods=['POST'])
def simular():
    try:
        datos = request.get_json()
        print("Datos recibidos:", datos)
        resultados = simular_credito(datos)

        # 🔧 Convertimos el DataFrame a JSON serializable
        if 'tabla_amortizacion' in resultados:
            resultados['tabla_amortizacion'] = resultados['tabla_amortizacion'].to_dict(orient='records')

        return jsonify(resultados)
    except Exception as e:
        print("Error en la simulación:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
