import uvicorn
from asgiref.wsgi import WsgiToAsgi

from flask import Flask, render_template, request, redirect, url_for

from modules.Gif        import crear_gif_thompson
@@ -13,11 +9,10 @@
import shutil

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

@app.route('/')
def hello_world():
    gif_path = "/tmp/RESULTADO.gif"
    gif_exists = os.path.exists(gif_path)
    return render_template('index.html', gif_exists=gif_exists)

@@ -34,7 +29,7 @@ def generate():

        # ELIMINANDO EL DIRECTORIO DE IMAGENES SI EXISTE

        directorio = "/tmp/AFN_Imagenes"
        if os.path.exists(directorio):
            shutil.rmtree(directorio)
            print(f" - Directorio '{directorio}' eliminado con éxito.")
@@ -70,6 +65,3 @@ def generate():
    except Exception as e:
        print(" + Error:", e)
        return render_template('index.html', error=e)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=8181)
