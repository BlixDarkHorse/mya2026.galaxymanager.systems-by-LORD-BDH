from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def cargar_invitados():

    with open(
        "invitados.json",
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)


@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )


@app.route("/buscar")
def buscar():

    texto = request.args.get(
        "q",
        ""
    ).lower()

    invitados = cargar_invitados()

    resultado = next(

        (
            i for i in invitados

            if texto in
            i["nombre"].lower()

            or

            texto ==
            i["codigo"].lower()

        ),

        None

    )

    if resultado:

        return jsonify(resultado)

    return jsonify({
        "error":
        "Invitación no encontrada"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )