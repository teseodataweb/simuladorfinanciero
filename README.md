# 🏡 Simulador Financiero para Compra de Terrenos

Este proyecto implementa un **simulador de riesgo crediticio y retorno de inversión (ROI)** para terrenos habitacionales, basado en factores como edad, ingresos, enganche, tipo de crédito, zona del lote, etc. Desarrollado con **Flask** y visualización en HTML/JavaScript, incluye soporte para simulaciones gráficas y modelos 3D.

---

## 🚀 Despliegue en Render

Este repositorio está preparado para ser desplegado automáticamente en [Render.com](https://render.com).

### ✅ Instrucciones para el despliegue:
1. Conecta tu repositorio a Render.
2. Selecciona el tipo de servicio: **Web Service**.
3. En la sección de "Start Command", ingresa:

   ```
   gunicorn flask_app.app:app
   ```

4. Asegúrate que en `flask_app/app.py` tengas:

   ```python
   app = Flask(__name__, static_folder='../static', template_folder='../templates')
   ```

5. Render instalará las dependencias desde `requirements.txt`.

---

## 📁 Estructura del Proyecto

```
simulador-financiero/
│
├── flask_app/
│   ├── app.py                    # Lógica principal de la app Flask
│   ├── modelo_riesgo_credito.py  # Modelo de riesgo y simulaciones financieras
│
├── static/                       # Archivos públicos: JS, GLB, imágenes, JSON
│   ├── plano-app.js
│   ├── background.png
│   ├── valdepenas.glb
│   ├── Swanky Kup-Esboo.glb
│   ├── tinker.obj
│   ├── obj.mtl
│   ├── lotes.json
│
├── templates/                    # Plantillas HTML servidas por Flask
│   ├── index.html                # Interfaz del simulador
│   ├── visor.html                # Visualizador de modelos 3D (Three.js)
│
├── planos/                       # Auxiliares que no se están usando actualmente
│   ├── planos.html
│   ├── plano_lotes_disponibilidad.svg
│
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Este documento
```

---

## ⚙️ Instalación local

Si quieres correrlo localmente:

```bash
git clone https://github.com/teseodataweb/simuladorfinanciero.git
cd simulador-financiero
python -m venv venv
source venv/bin/activate     # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cd flask_app
python app.py                # o usa flask run
```

---

## 🧠 ¿Qué hace este simulador?

- Calcula el **puntaje de riesgo** basado en edad, ingresos, enganche, zona y tipo de crédito.
- Determina la **tasa de interés**, enganche mínimo y préstamo máximo según el riesgo.
- Calcula la **mensualidad**, **tabla de amortización**, **valor futuro del terreno** y **ROI**.
- Genera gráficos interactivos (matplotlib + seaborn).
- Visualiza modelos en 3D desde el navegador.

---

## 📦 Dependencias principales

- `Flask`
- `gunicorn` (para producción)
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`

---

## 🖼 Ejemplo de uso

Puedes probar en producción vía Render:

**🔗 https://simuladorfinanciero.onrender.com**

- Página principal: `/`
- Endpoint de simulación (POST JSON): `/simular`
- Visor 3D: `/visor`

---

## 🧑‍💻 Autoría

Desarrollado por Manus & Lizbeth – 2025.

---

---

## 🧩 Estructura visual del proyecto y flujo de rutas

### 📂 Estructura general

```
simuladorfinanciero/
│
├── flask_app/
│   └── modelo_riesgo_credito.py      ← Lógica principal del modelo de simulación
│
├── static/                           ← Archivos estáticos para frontend
│   ├── backherosection.jpg           ← Imagen de fondo
│   ├── valdepenas.glb                ← Plano exportado de tinkecard
│   └── ...                           ← Otros recursos como .obj, etc.
│
├── templates/
│   ├── index.html                    ← Página principal con formulario de simulación
│   └── visor.html                    ← Visor 3D de lotes que llama al .glb
│
├── app.py                            ← Servidor Flask que orquesta rutas y respuestas
├── requirements.txt                  ← Dependencias del proyecto
└── ...
```

### ⚙️ Archivos clave de funcionalidad (Back-end)

| Archivo | Descripción |
|--------|-------------|
| `app.py` | Punto de entrada Flask. Define rutas `/`, `/simular`, `/visor`, recibe datos vía POST y retorna resultados JSON. |
| `flask_app/modelo_riesgo_credito.py` | Implementa el modelo de riesgo y funciones para calcular mensualidad, ROI, amortización, plusvalía y validaciones. |

### 🎨 Archivos clave de diseño (Front-end)

| Archivo | Descripción |
|---------|-------------|
| `templates/index.html` | Página HTML que carga el formulario y se conecta vía JS con `/simular`. Usa Jinja2 para incluir rutas estáticas. |
| `templates/visor.html` | Página para desplegar el visor 3D interactivo usando JavaScript y Three.js. |
| `static/background.png` y otros | Recursos visuales como imágenes o modelos 3D. |

---

### 🌐 Cómo se mandan a llamar las rutas (con `url_for` y `fetch`)

Flask usa **Jinja2** para generar rutas dinámicas dentro de las plantillas HTML. Ejemplo:

```html
<link rel="icon" href="{{ url_for('static', filename='favicon_nuevo.ico') }}" type="image/x-icon" />
```

Esto indica que el navegador debe cargar el favicon desde `/static/favicon_nuevo.ico`.

También se usa `fetch` en el frontend para invocar el endpoint `/simular`:

```javascript
fetch('/simular', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(datos)
})
.then(response => response.json())
.then(data => {
  // Renderizar resultados en el HTML
});
```

Las rutas configuradas en `app.py` son:

```python
@app.route('/')              # Carga index.html
@app.route('/simular')       # Procesa los datos POST para simulación
@app.route('/visor')         # Carga visor.html
```

Estas permiten un flujo completo desde la entrada del usuario hasta la visualización de resultados o modelos 3D.