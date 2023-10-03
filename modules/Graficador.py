import os
import glob
import graphviz as gv


def graficarAutomataFinitoNoDeterminista(afn, numero_transiciones=0):
    # Crear el directorio si no existe
    directorio = "AFN_Imagenes"
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    # Contar cuántos archivos ya existen en el directorio
    archivos_existentes = glob.glob(os.path.join(directorio, "thompson_*.png"))
    siguiente_numero = len(archivos_existentes) + 1
    ruta_salida = os.path.join(directorio, f"thompson_{siguiente_numero}")

    # Creamos el grafo
    grafo = gv.Digraph(format='png', graph_attr={'rankdir': 'LR'})

    # Agregar los estados y transiciones
    total_transiciones = len(afn.transiciones)
    for idx, transicion in enumerate(afn.transiciones):
        estado_orig = str(transicion.origen)
        estado_dest = str(transicion.destino)
        estado_simb = str(transicion.simbolo)
        
        # Si estamos en las últimas dos transiciones, coloreamos de rojo
        if idx >= total_transiciones - numero_transiciones and numero_transiciones != 0:
            grafo.edge(estado_orig, estado_dest, label=estado_simb, color="red", fontcolor="red")
        else:
            grafo.edge(estado_orig, estado_dest, label=estado_simb, color="blue", fontcolor="blue")

    # Agregar el estado inicial
    grafo.node(str(afn.getEstadoInicial()), shape='circle', style='filled', fillcolor="lightyellow", fontcolor="black")

    # Agregar la flecha de inicio
    grafo.node('Inicio', shape='point')
    grafo.edge('Inicio', str(afn.getEstadoInicial()), color="green")

    # Agregar el estado de aceptación
    grafo.node(str(afn.getEstadoFinal()), shape='doublecircle', style='filled', fillcolor="lightgreen", fontcolor="black")

    # Guardar el grafo sin mostrarlo
    grafo.render(ruta_salida, view=False)


def graficarAutomataFinitoDeterminista(afd, titulo):

    # Creamos el grafo
    grafo = gv.Digraph(format='png', graph_attr={'rankdir': 'LR'})

    # print(afd.transiciones)

    # print(afd.estadosAceptacion)

    # print(afd.estadosIniciales)

    # Agregamos los estados
    for transicion in afd.transiciones:

        estado_dest = str(transicion[2])
        estado_simb = str(transicion[1])
        estado_orig = str(transicion[0])

        grafo.edge(estado_orig, estado_dest, label=estado_simb)

    # Agregamos el estado inicial
    grafo.node(str(afd.estadosIniciales[0]), shape='circle', style='bold')

    # Agregamos la flecha de inicio
    grafo.node('Inicio', shape='point')

    # Conectamos el estado inicial con la flecha de inicio
    grafo.edge('Inicio', str(afd.estadosIniciales[0]))

    # Agregamos los estados de aceptacion
    for estado in afd.estadosAceptacion:

        grafo.node(str(estado), shape='doublecircle', style='bold')

    # Guardamos el grafo
    grafo.render(titulo, view=True)
