# EEL CIBERSEGURIDAD - Laboratorio de reutilización de una cookie de sesión

Laboratorio educativo y deliberadamente vulnerable para observar, de
forma local y controlada, cómo una aplicación web mantiene una sesión
autenticada mediante una cookie y qué ocurre cuando esa misma cookie se
reutiliza desde un segundo navegador.

> **Advertencia:** utilizar exclusivamente en este laboratorio, sistemas
> propios o entornos expresamente autorizados. No reutilices cookies
> obtenidas de cuentas, servicios o sistemas reales.

## ¿Qué vamos a demostrar?

Usaremos dos navegadores. El **Navegador A** iniciará sesión normalmente
con usuario y contraseña. La aplicación le entregará una cookie llamada
`sesion_eel`. Observaremos esa petición con Burp Suite. Después
abriremos un **Navegador B** que nunca realizó el login, agregaremos
manualmente la cookie ficticia del laboratorio y comprobaremos que el
servidor reconoce la sesión.

La contraseña se utiliza para la autenticación inicial. Después, muchas
aplicaciones identifican las solicitudes posteriores mediante un token
de sesión. Por eso un token de sesión debe protegerse como una
credencial temporal.

## Requisitos

-   Kali Linux (recomendado para seguir exactamente el tutorial).
-   Python 3.
-   `python3-venv`.
-   Burp Suite Community o Professional.
-   Firefox.

Todo el laboratorio funciona únicamente en `127.0.0.1:5000`.

## Archivos

``` text
Lab-cookie/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## PARTE 1 --- Descargar el laboratorio

Clonasción con Git:

``` bash
git clone https://github.com/eelciberseguridad/Lab-cookie.git
cd Lab-cookie
```

## PARTE 2 --- Preparar Python

Desde la carpeta del proyecto:

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Cuando el entorno esté activo normalmente aparecerá `(venv)` al comienzo
de la terminal.

## PARTE 3 --- Ejecutar la aplicación

``` bash
python3 app.py
```

Flask debería indicar:

``` text
Running on http://127.0.0.1:5000
```

Dejá esa terminal abierta. **No reinicies Flask durante la
demostración:** las sesiones de este laboratorio se guardan únicamente
en memoria y se pierden al reiniciar el proceso.

## PARTE 4 --- Navegador A: iniciar una sesión legítima

Abrí Burp Suite y dirigite a:

``` text
Proxy → Intercept
```

Para que la navegación sea más sencilla, dejá inicialmente:

``` text
Intercept is OFF
```

Presioná **Open Browser**. Ese navegador será el **Navegador A**.

Entrá en:

``` text
http://127.0.0.1:5000
```

Usá las credenciales ficticias:

``` text
Usuario: alumno
Contraseña: laboratorio123
```

Presioná **INICIAR SESIÓN**. La aplicación redirigirá a:

``` text
http://127.0.0.1:5000/panel
```

Deberías ver el panel privado, el usuario `alumno` y un saldo ficticio
de `$500.000`.

### ¿Qué ocurrió?

Al validar las credenciales, el servidor ejecuta conceptualmente estas
dos operaciones:

``` python
token = "SESION-EEL-2026"
SESIONES[token] = usuario
```

Luego entrega al navegador una cookie:

``` python
respuesta.set_cookie("sesion_eel", token)
```

El token fijo es intencionalmente inseguro y existe únicamente para que
el laboratorio resulte fácil de seguir.

## PARTE 5 --- Observar la cookie con Burp Suite

Volvé a Burp Suite y abrí:

``` text
Proxy → HTTP history
```

Buscá la petición:

``` text
GET /panel
```

Seleccionála y observá **Request**. Entre las cabeceras debería
aparecer:

``` http
Cookie: sesion_eel=SESION-EEL-2026
```

Tenemos dos datos importantes:

``` text
Nombre: sesion_eel
Valor:  SESION-EEL-2026
```

**Atención:** `sesion_eel` contiene un guion bajo `_`. El nombre debe
coincidir exactamente con el que espera `app.py`.

También podés buscar la respuesta a `POST /login`. Allí debería
observarse una cabecera `Set-Cookie`, que es la forma en que el servidor
le indica al navegador que almacene la cookie.

## PARTE 6 --- Navegador B: comprobar que inicialmente no tiene acceso

Sin cerrar Flask ni reiniciarlo, abrí **Firefox normal**. Este será el
**Navegador B**.

No introduzcas usuario ni contraseña. Entrá directamente en:

``` text
http://127.0.0.1:5000/panel
```

El resultado esperado es:

``` text
ACCESO DENEGADO
No existe una sesión autenticada.
```

Esto confirma que el segundo navegador todavía no posee la cookie de la
sesión creada por el Navegador A.

## PARTE 7 --- Agregar la cookie ficticia al Navegador B

En Firefox presioná `F12` y abrí:

``` text
Storage / Almacenamiento → Cookies → http://127.0.0.1:5000
```

Agregá una cookie con estos valores:

``` text
Name:   sesion_eel
Value:  SESION-EEL-2026
Domain: 127.0.0.1
Path:   /
```

## PARTE 8 --- Comprobar que Firefox realmente envía la cookie

En Firefox abrí:

``` text
F12 → Network / Red
```

Actualizá `/panel`, seleccioná la petición `GET /panel` y revisá
**Request Headers**.

Debería aparecer:

``` http
Cookie: sesion_eel=SESION-EEL-2026
```

Esto permite distinguir entre una cookie simplemente visible en Storage
y una cookie que efectivamente está siendo enviada al servidor.

## PARTE 9 --- Cambiar el token y observar el resultado

Volvé a:

``` text
F12 → Storage → Cookies
```

Cambiá temporalmente el valor:

``` text
SESION-EEL-2026
```

por:

``` text
COOKIE-FALSA
```

Actualizá `/panel`. El servidor debería responder **ACCESO DENEGADO**
porque `COOKIE-FALSA` no existe dentro de `SESIONES`.

Restaurá:

``` text
SESION-EEL-2026
```

Actualizá nuevamente. El panel privado debería volver a mostrarse.

## ¿Por qué este código es deliberadamente inseguro?

No representa cómo debería desarrollarse un sistema real. Entre otras
simplificaciones, utiliza un token fijo y predecible, guarda las
sesiones en memoria y no configura explícitamente atributos defensivos
de la cookie. Esto permite observar el concepto sin ocultarlo detrás de
un framework de autenticación más complejo.

En producción deben considerarse, entre otras medidas, identificadores
de sesión criptográficamente aleatorios, HTTPS, cookies `Secure`,
`HttpOnly` y una política `SameSite` adecuada, expiración, rotación del
identificador tras autenticarse, invalidación de sesiones en el servidor
y protección frente a vulnerabilidades que puedan exponer tokens.

`HttpOnly`, por ejemplo, dificulta que JavaScript del lado cliente lea
una cookie, pero **no convierte por sí solo una cookie robada en
inutilizable**. La seguridad de sesión requiere varias capas.

## Reflexión final

Este laboratorio muestra una distinción fundamental: **autenticarse y
mantener una sesión no son exactamente lo mismo**. La contraseña puede
intervenir al comienzo, pero después el servidor necesita reconocer las
solicitudes posteriores y suele hacerlo mediante un token de sesión. Si
ese token queda expuesto y continúa siendo válido, puede convertirse
temporalmente en una credencial tan sensible como la propia contraseña.

El objetivo de estudiar el problema no es aprender a tomar sesiones
ajenas, sino entender por qué las aplicaciones deben proteger, renovar e
invalidar correctamente sus tokens de sesión.
