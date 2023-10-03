import string
import os
import json
from modules.Graficador import graficarAutomataFinitoNoDeterminista


class AFN:

    # Metodo constructor de la clase AFN, inicializa la lista de transiciones vacia
    def __init__(self):

        self.transiciones = []

    # Metodo encargado de agregar una transicion al AFN
    def agregarTransicion(self, transicion):

        self.transiciones.append(transicion)

    # Metodo encargado de obtener los caracteres/valores de transicion del AFN
    def obtenerCaracteres(self):

        listaCaracteres = []

        for transicion in self.transiciones:

            if transicion.simbolo not in listaCaracteres and transicion.simbolo != "ε":

                listaCaracteres.append(transicion.simbolo)

        return listaCaracteres

    def getEstadoInicial(self):

        # El estado inicial de N es el primer estado de la lista de transiciones

        return self.transiciones[0].origen

    def getEstadoFinal(self):

        # El estado final de N es el ultimo estado de la lista de transiciones

        return self.transiciones[-1].destino

    # Metodo encargado de transformar el AFN a un string
    def __str__(self):

        resultado = "\nAFN: \n"

        for transicion in self.transiciones:

            resultado += str(transicion) + "\n"

        return resultado


class Transicion:

    # Metodo constructor de la clase Transicion, recibe como parametros el estado de origen, el estado de destino y el simbolo/transicion
    def __init__(self, origen, destino, simbolo):
        self.origen = origen
        self.destino = destino
        self.simbolo = simbolo

    # Metodo encargado de transformar la transicion a un string
    def __str__(self):
        return f"[Transicion ({self.origen}, {self.simbolo}, {self.destino})]"


class Thompson:

    # Constructor de la clase Thompson
    # Recibe como parametro una expresion regular en notacion posfija
    # Inicializa la cantidad de estados generados en 0

    def __init__(self, expresion):

        self.expresion = expresion

        self.cantidadEstadosGenerados = 0

        self.generarAutomataFinitoNoDeterminista()

    # Metodo encargado de renombrar los estados del AFN para un mejor manejo
    @staticmethod
    def generar_siguiente_nombre(ultimo_nombre):
        listaLetras = list(string.ascii_uppercase)

        if not ultimo_nombre:
            return listaLetras[0]

        if ultimo_nombre[-1] != listaLetras[-1]:  # Si no es 'Z'
            # Cambia la última letra al siguiente en la lista
            return ultimo_nombre[:-1] + listaLetras[listaLetras.index(ultimo_nombre[-1]) + 1]
        
        # Si es 'Z', aumenta al principio
        return Thompson.generar_siguiente_nombre(ultimo_nombre[:-1]) + listaLetras[0]


    def renombrarEstados(self):
        diccionarioEstados = {}
        ultimo_nombre = ''

        for transicion in self.afn.transiciones:
            if transicion.origen not in diccionarioEstados:
                ultimo_nombre = Thompson.generar_siguiente_nombre(ultimo_nombre)
                diccionarioEstados[transicion.origen] = ultimo_nombre
                
            if transicion.destino not in diccionarioEstados:
                ultimo_nombre = Thompson.generar_siguiente_nombre(ultimo_nombre)
                diccionarioEstados[transicion.destino] = ultimo_nombre

        for transicion in self.afn.transiciones:
            transicion.origen = diccionarioEstados[transicion.origen]
            transicion.destino = diccionarioEstados[transicion.destino]

    # Metodo encargado de obtener todos los estados que tiene el AFN

    def obtenerEstados(self):

        estados = []

        for transicion in self.afn.transiciones:

            if transicion.origen not in estados:

                estados.append(transicion.origen)

            if transicion.destino not in estados:

                estados.append(transicion.destino)

        self.estadoAceptacion = self.afn.transiciones[-1].destino
        self.estadoInicial = self.afn.transiciones[0].origen

        return estados

    # Metodo utilizado para ilustrar el AFN generado por el algoritmo de Thompson



    # Metodo que se encarga de verificar si un caracter es un operador

    def esOperador(self, caracter):

        return caracter == '*' or caracter == '.' or caracter == '|' or caracter == '+' or caracter == '?'

    # Metodo que se encarga de verificar si un operador es binario o unario

    def esBinario(self, caracter):

        return caracter == '.' or caracter == '|'

    # Regla 1: Simbolo, esta regla se encarga de generar un AFN que solo acepta un simbolo
    # Ejemplo: a
    # AFN: estado 0 -> a -> estado 1
    # Ejemplo concreto:  a = [0a1]

    def reglaSimbolo(self, simbolo):

        afnTemporal = AFN()

        estadoActual = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        estadoSiguiente = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        transicionTemporal = Transicion(estadoActual, estadoSiguiente, simbolo)

        afnTemporal.agregarTransicion(transicionTemporal)

        return afnTemporal

    # Regla 2: Concatenacion, esta regla se encarga de generar un AFN que acepta la concatenacion de dos AFN
    # Ejemplo: ab.
    # AFN: estado 0 -> a -> estado 1 -> b -> estado 2
    # Ejemplo concreto:  [0a1][2b3] = [0a1][1b3]

    def reglaConcatenacion(self, afn1, afn2):

        afnFinal = AFN()

        # Agregamos las transiciones del primer AFN

        for transicion in afn1.transiciones:

            afnFinal.agregarTransicion(transicion)

        # Organizamos los estados del segundo AFN de tal manera que el ultimo estado del primer AFN sea el estado inicial del segundo AFN

        estadoFAFN1 = afn1.transiciones[-1].destino
        estadoIAFN2 = afn2.transiciones[0].origen

        for transicion in afn2.transiciones:

            if transicion.origen == estadoIAFN2:

                transicion.origen = estadoFAFN1

        # Agregamos las transiciones del segundo AFN

        for transicion in afn2.transiciones:

            afnFinal.agregarTransicion(transicion)

        return afnFinal

    # Regla 3: OR, esta regla se encarga de generar un AFN que acepta la union de dos AFN
    # Ejemplo: b|c
    # AFN:          estado 1 -> b -> estado 2
    #           / e                             \ e
    # estado 0                                      estado 5
    #           \ e                             / e
    #               estado 3 -> c -> estado 4
    #
    # Ejemplo concreto:  [2b3][4c5] =
    #      [2b3]
    # [1e2]     [3e6]
    # [1e4]     [5e6]
    #      [4c5]

    def reglaOR(self, afn1, afn2):

        afnFinal = AFN()

        # Creamos el estado inicial

        estadoInicial = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        # Creamos el estado final

        estadoFinal = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        # Creamos la transicion vacia del estado inicial al primer AFN

        transicionTemporal1 = Transicion(
            estadoInicial, afn1.transiciones[0].origen, 'ε')

        # Creamos la transicion vacia del estado inicial al segundo AFN

        transicionTemporal2 = Transicion(
            estadoInicial, afn2.transiciones[0].origen, 'ε')

        # Agregamos las transiciones al AFN final

        afnFinal.agregarTransicion(transicionTemporal1)
        afnFinal.agregarTransicion(transicionTemporal2)

        # Para este paso ya tenemos:
        #
        # [1e2]
        # [1e4]
        #

        # Agregamos las transiciones del primer AFN

        for transicion in afn1.transiciones:

            afnFinal.agregarTransicion(transicion)

        # Agregamos las transiciones del segundo AFN

        for transicion in afn2.transiciones:

            afnFinal.agregarTransicion(transicion)

        # Para este paso ya tenemos:

        #      [2b3]
        # [1e2]
        # [1e4]
        #      [4c5]

        # Obtenemos el ultimo estado del primer AFN

        ultimoEstadoAFN1 = afn1.transiciones[-1].destino

        # Obtener el ultimo estado del segundo AFN

        ultimoEstadoAFN2 = afn2.transiciones[-1].destino

        # Creamos la transicion vacia del ultimo estado del primer AFN al estado final

        transicionTemporal1 = Transicion(ultimoEstadoAFN1, estadoFinal, 'ε')

        # Creamos la transicion vacia del ultimo estado del segundo AFN al estado final

        transicionTemporal2 = Transicion(ultimoEstadoAFN2, estadoFinal, 'ε')

        # Agregamos las transiciones al AFN final

        afnFinal.agregarTransicion(transicionTemporal1)
        afnFinal.agregarTransicion(transicionTemporal2)

        # Para este paso ya tenemos:

        #      [2b3]
        # [1e2]     [3e6]
        # [1e4]     [5e6]
        #      [4c5]

        return afnFinal

    # Regla 4: Cerradura de Kleene, esta regla se encarga de generar un AFN que acepta la cerradura de Kleene de un AFN
    # Ejemplo: a*
    # AFN:
    #                  ____________________>_____________________
    #                 / e                                        \ e
    #          estado 0 -> e -> estado 1 -> a -> estado 2 -> e -> estado 3
    #                               e\             / e
    #                                 \___________/

    def reglaKleene(self, afn):

        afnFinal = AFN()

        # Creamos el estado inicial

        estadoInicial = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        # Creamos el estado final

        estadoFinal = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        # Creamos la transicion vacia del estado inicial al estado final

        transicionEstadoInicialAFinal = Transicion(
            estadoInicial, estadoFinal, 'ε')

        # Creamos la transicion vacia desde el estado inicial al primer del AFN

        transicionEstadoInicialAIncialAFN = Transicion(
            estadoInicial, afn.transiciones[0].origen, 'ε')

        # Agregamos las transiciones al AFN final

        afnFinal.agregarTransicion(transicionEstadoInicialAIncialAFN)

        # Agregamos las transiciones del AFN

        for transicion in afn.transiciones:

            afnFinal.agregarTransicion(transicion)

        # Creamos la transicion vacia desde el ultimo estado del AFN al estado final

        transicionEstadoUltimoAFNAFinal = Transicion(
            afn.transiciones[-1].destino, estadoFinal, 'ε')

        # Agregamos la transicion al AFN final

        afnFinal.agregarTransicion(transicionEstadoUltimoAFNAFinal)

        # Creamos la transicion vacia desde el ultimo estado del AFN al primer estado del AFN

        transicionEstadoUltimoAPrimero = Transicion(
            afn.transiciones[-1].destino, afn.transiciones[0].origen, 'ε')

        # Agregamos la transicion al AFN final

        afnFinal.agregarTransicion(transicionEstadoUltimoAPrimero)

        # Agregamos la transicion vacia del estado inicial al estado final

        afnFinal.agregarTransicion(transicionEstadoInicialAFinal)

        return afnFinal

    # Regla 5: Cerradura Positiva, esta regla se encarga de generar un AFN que acepta la cerradura positiva de un AFN
    def reglaPositiva(self, afn):

        afnTemporal = AFN()

        # Para implementar la cerradura positiva en el algoritmo de Thompson, se puede seguir los siguientes pasos:

        # 1 Crear dos nodos nuevos, start y end, que representan el inicio y el fin del autómata.

        # Creamos el estado inicial

        estadoInicial = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        # Creamos el estado final

        estadoFinal = self.cantidadEstadosGenerados

        self.cantidadEstadosGenerados += 1

        # 2 Crear un nuevo nodo n1 y conectarlo con una transición epsilon (ε) al nodo start.

        transicion1 = Transicion(
            estadoInicial, afn.transiciones[0].origen, 'ε')
        afnTemporal.agregarTransicion(transicion1)

        # 3 Crear otro nuevo nodo n2 y conectarlo con una transición epsilon (ε) al nodo n1.

        transicion2 = Transicion(
            afn.transiciones[-1].destino, afn.transiciones[0].origen, 'ε')
        afnTemporal.agregarTransicion(transicion2)

        # 4 Agregar una transición con el símbolo deseado (por ejemplo, a) desde el nodo n1 al nodo n2.

        for transicion in afn.transiciones:

            afnTemporal.agregarTransicion(transicion)

        # 5 Conectar el nodo n2 con una transición epsilon (ε) al nodo end.

        transicion3 = Transicion(
            afn.transiciones[-1].destino, estadoFinal, 'ε')
        afnTemporal.agregarTransicion(transicion3)

        return afnTemporal

    # Regla 6: Opcional(?), esta regla se encarga de generar un AFN que acepta la opcion de un AFN

    def reglaOpcional(self, afn):

        afnFinal = AFN()

        # Creamos 4 nuevos estados

        estado1 = self.cantidadEstadosGenerados
        self.cantidadEstadosGenerados += 1

        estado2 = self.cantidadEstadosGenerados
        self.cantidadEstadosGenerados += 1

        estado3 = self.cantidadEstadosGenerados
        self.cantidadEstadosGenerados += 1

        estado4 = self.cantidadEstadosGenerados
        self.cantidadEstadosGenerados += 1

        # Creamos una transicion vacia desde el estado 2 al estado 3

        transicionConEpsilum2A3 = Transicion(estado2, estado3, 'ε')

        # Creamos una transicion vacia desde el estado 1 al estado 2

        transicionConEpsilum1A2 = Transicion(estado1, estado2, 'ε')

        # Creamos una transicion vacia desde el estado 3 al estado 4

        transicionConEpsilum3A4 = Transicion(estado3, estado4, 'ε')

        # Creamos una trasicion vacia desde el estado 1 al primer estado del AFN

        transicionConEpsilum1APrimeroAFN = Transicion(
            estado1, afn.transiciones[0].origen, 'ε')

        # Creamos una transicion vacia desde el ultimo estado del AFN al estado 4

        transicionConEpsilumUltimoAFNA4 = Transicion(
            afn.transiciones[-1].destino, estado4, 'ε')

        # Empezamos a agregar todas las transiciones al AFN final

        afnFinal.agregarTransicion(transicionConEpsilum1A2)
        afnFinal.agregarTransicion(transicionConEpsilum2A3)
        afnFinal.agregarTransicion(transicionConEpsilum3A4)
        afnFinal.agregarTransicion(transicionConEpsilum1APrimeroAFN)
        for transicion in afn.transiciones:
            afnFinal.agregarTransicion(transicion)
        afnFinal.agregarTransicion(transicionConEpsilumUltimoAFNA4)

        # Regresamos el AFN final
        return afnFinal

    # Generacion de AFN: Se encarga de generar un AFN a partir de una expresion regular en notacion posfija
    # Ejemplo: ab.
    # AFN: estado 0 -> a -> estado 1 -> b -> estado 2

    def generarAutomataFinitoNoDeterminista(self):

        # Borramos el archivo "orden.json" si existe
        if os.path.exists("orden.json"):
            os.remove("orden.json")

        # Inicializamos una lista para guardar el orden de las operaciones
        orden_operaciones = []

        stack = []

        cantidad_pasos = 0

        for caracter in self.expresion:

            numero_transiciones_usadas = 0

            # Si el caracter no es un operador, entonces es un simbolo
            if not self.esOperador(caracter):

                # Regla 1: Simbolo
                afnTemporal = self.reglaSimbolo(caracter)
                orden_operaciones.append("[ Paso " + str(cantidad_pasos) + " ] "+ "Se uso regla simbolo")
                cantidad_pasos += 1
                numero_transiciones_usadas = 1
                stack.append(afnTemporal)

            # Si el caracter es un operador, entonces
            else:

                # Si el caracter es un operador binario
                if self.esBinario(caracter):

                    # Extraemos los dos ultimos AFN del stack
                    afnTemporal2 = stack.pop()
                    afnTemporal1 = stack.pop()

                    # Revisamos que operando es, para aplicar la regla correspondiente
                    if caracter == '.':

                        # Regla 2: Concatenacion
                        afnTemporal = self.reglaConcatenacion(afnTemporal1, afnTemporal2)
                        orden_operaciones.append("[ Paso " + str(cantidad_pasos) + " ] "+ "Se uso regla CONCATENACION")
                        cantidad_pasos += 1
                        numero_transiciones_usadas = 1
                        stack.append(afnTemporal)

                    elif caracter == '|' or caracter == '+':

                        # Regla 3: OR
                        afnTemporal = self.reglaOR(afnTemporal1, afnTemporal2)
                        orden_operaciones.append("[ Paso " + str(cantidad_pasos) + " ] "+ "Se uso regla OR")
                        cantidad_pasos += 1
                        numero_transiciones_usadas = 2
                        stack.append(afnTemporal)

                # Si el caracter es un operador unario "Kleen"
                else:

                    if caracter == "*":
                        # Extraemos el ultimo AFN del stack
                        afnTemporal = stack.pop()

                        # Regla 4: Kleen
                        afnTemporal = self.reglaKleene(afnTemporal)
                        orden_operaciones.append("[ Paso " + str(cantidad_pasos) + " ] "+ "Se uso regla KLEEN")
                        cantidad_pasos += 1
                        numero_transiciones_usadas = 2
                        stack.append(afnTemporal)

                    elif caracter == "+":
                        afnTemporal = stack.pop()

                        # Regla 5: Cerradura Positiva
                        afnTemporal = self.reglaPositiva(afnTemporal)
                        orden_operaciones.append("[ Paso " + str(cantidad_pasos) + " ] "+ "Se uso regla Cerradura Positiva")
                        cantidad_pasos += 1
                        numero_transiciones_usadas = 2
                        stack.append(afnTemporal)

                    elif caracter == "?":
                        afnTemporal = stack.pop()

                        # Regla 6: Opcional
                        afnTemporal = self.reglaOpcional(afnTemporal)
                        orden_operaciones.append("[ Paso " + str(cantidad_pasos) + " ] "+ "Se uso regla Opcional")
                        cantidad_pasos += 1
                        numero_transiciones_usadas = 4
                        stack.append(afnTemporal)

            graficarAutomataFinitoNoDeterminista(stack[-1], numero_transiciones_usadas)

        # Al finalizar el bucle, guardamos el orden de las operaciones en "orden.json"
        with open("orden.json", "w") as file:
            json.dump({"Orden": orden_operaciones}, file)
        # Retornamos el AFN final

        self.afn = stack.pop()

        # Reorganizamos los estados del AFN

        self.renombrarEstados()

        # Obtenemos los estados del AFN

        self.obtenerEstados()
