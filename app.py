from flask import Flask, render_template, request, redirect, url_for

from modules.Gif        import crear_gif_thompson
from modules.Thompson   import Thompson
from modules.Graficador import graficarAutomataFinitoNoDeterminista
from modules.Postfix    import convertirAPostfix, formatearExpresionRegular

import os
import shutil

app = Flask(__name__)

@app.route('/')
def hello_world():
    gif_path = "static/RESULTADO.gif"
    gif_exists = os.path.exists(gif_path)
    return render_template('index.html', gif_exists=gif_exists)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        user_input = request.form['user_input']
        
        print()

        print(" + La expresion regular es:", user_input)

        print(" + Generando el AFN...")

        # ELIMINANDO EL DIRECTORIO DE IMAGENES SI EXISTE

        directorio = "AFN_Imagenes"
        if os.path.exists(directorio):
            shutil.rmtree(directorio)
            print(f" - Directorio '{directorio}' eliminado con éxito.")
        else:
            print(f" - El directorio '{directorio}' no existe.")

        # CREAMOS EL AUTOMATA FINITO NO DETERMINISTA

        regex = user_input

        # Formateamos la expresion regular para que sea valida

        regex = formatearExpresionRegular(regex)

        # Convertimos la expresion regular de infix a postfix

        regex = convertirAPostfix(regex)

        AFN_Thompson = Thompson(regex).afn

        # Graficamos el automata finito no determinista

        graficarAutomataFinitoNoDeterminista(AFN_Thompson)

        print(" + Generando el GIF...")

        # CREAMOS EL GIF

        crear_gif_thompson()
        
        return redirect(url_for('hello_world'))
    
    except Exception as e:
        print(" + Error:", e)
        return render_template('index.html', error=e)
