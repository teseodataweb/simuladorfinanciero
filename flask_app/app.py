from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_app.modelo_riesgo_credito import simular_credito

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return render_template("index.html")

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
@app.route('/visor')
def visor():
    return render_template("visor.html")