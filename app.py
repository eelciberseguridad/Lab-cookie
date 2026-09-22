from flask import Flask, request, make_response, redirect

app = Flask(__name__)

# Laboratorio deliberadamente inseguro.
# Las sesiones se guardan solo en memoria para facilitar la demostración.
SESIONES = {}


@app.route("/")
def inicio():
    return """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>EEL CIBERSEGURIDAD - Laboratorio de sesión</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 720px; margin: 70px auto; padding: 0 20px; }
            .card { border: 1px solid #ccc; border-radius: 12px; padding: 28px; }
            input { padding: 10px; width: 90%; max-width: 360px; }
            button { padding: 10px 18px; cursor: pointer; }
            .note { margin-top: 24px; color: #555; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>EEL CIBERSEGURIDAD</h1>
            <h2>Laboratorio de cookie de sesión</h2>
            <form method="POST" action="/login">
                <p><input name="usuario" placeholder="Usuario" required></p>
                <p><input name="password" type="password" placeholder="Contraseña" required></p>
                <button type="submit">INICIAR SESIÓN</button>
            </form>
            <p class="note">Entorno educativo local. No utilizar contra sistemas o cuentas reales.</p>
        </div>
    </body>
    </html>
    """


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario")
    password = request.form.get("password")

    if usuario == "alumno" and password == "laboratorio123":
        # Token fijo SOLO para que el comportamiento sea fácil de observar.
        # Una aplicación real debe usar identificadores aleatorios e impredecibles.
        token = "SESION-EEL-2026"
        SESIONES[token] = usuario

        respuesta = make_response(redirect("/panel"))
        respuesta.set_cookie("sesion_eel", token)
        return respuesta

    return "USUARIO O CONTRASEÑA INCORRECTOS", 401


@app.route("/panel")
def panel():
    token = request.cookies.get("sesion_eel")

    if token in SESIONES:
        usuario = SESIONES[token]
        return f"""
        <!doctype html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <title>Panel privado</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 720px; margin: 70px auto; padding: 0 20px; }}
                .card {{ border: 1px solid #ccc; border-radius: 12px; padding: 28px; }}
                .saldo {{ font-size: 42px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>EEL CIBERSEGURIDAD</h1>
                <h2>PANEL PRIVADO</h2>
                <h3>Bienvenido {usuario}</h3>
                <p>Sesión autenticada correctamente.</p>
                <hr>
                <h2>SALDO DISPONIBLE</h2>
                <div class="saldo">$500.000</div>
                <p>Información ficticia utilizada únicamente para el laboratorio.</p>
            </div>
        </body>
        </html>
        """

    return """
    <!doctype html>
    <html lang="es">
    <head><meta charset="utf-8"><title>Acceso denegado</title></head>
    <body style="font-family:Arial;margin:70px">
        <h1>ACCESO DENEGADO</h1>
        <p>No existe una sesión autenticada.</p>
    </body>
    </html>
    """, 401


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
