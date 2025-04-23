from flask import Flask, render_template, request, redirect, url_for, session
import json, random, os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'payi')

PREGUNTAS_FILE = 'preguntas.json'

# Cargar preguntas y descripciones desde el JSON
def cargar_datos():
    with open(PREGUNTAS_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
    preguntas = data['preguntas']
    descripciones = data['descripciones']
    random.shuffle(preguntas)
    return preguntas, descripciones

@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        # Capturar el nombre del formulario y guardarlo en sesión
        nombre = request.form.get('nombre')
        session.clear()
        session['nombre'] = nombre

        # Cargar preguntas y descripciones
        preguntas, descripciones = cargar_datos()
        session['preguntas'] = preguntas
        session['descripciones'] = descripciones
        session['respuestas'] = []
        session['index'] = 0
        return redirect(url_for('test'))
    return render_template('inicio.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    index = session.get('index', 0)
    preguntas = session.get('preguntas', [])
    respuestas = session.get('respuestas', [])

    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        if respuesta:
            respuestas.append(respuesta)
            session['respuestas'] = respuestas
            session['index'] = index + 1
            index += 1

    if index >= len(preguntas):
        return redirect(url_for('resultado'))

    pregunta_actual = preguntas[index]
    return render_template('test.html', pregunta=pregunta_actual, index=index + 1, total=len(preguntas))

@app.route("/resultado")
def resultado():
    respuestas = session.get("respuestas", [])
    descripciones = session.get("descripciones", {})
    nombre = session.get("nombre", "Usuario")

    # Contar cuál animal fue seleccionado más veces
    conteo = {}
    for animal in respuestas:
        conteo[animal] = conteo.get(animal, 0) + 1

    resultado = max(conteo, key=conteo.get)
    datos = descripciones.get(resultado, {"emoji": "❓", "descripcion": "Sin descripción disponible."})

    return render_template("resultado.html", resultado=resultado.capitalize(), descripcion=datos["descripcion"], emoji=datos["emoji"], nombre=nombre)

if __name__ == '__main__':
    app.run(debug=True)