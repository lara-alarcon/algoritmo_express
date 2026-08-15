import random
from data.escenarios import ESCENARIOS

def seleccionar_escenarios(cantidad=3):

    # Separar escenariios por dificualtad

    faciles = [
        escenario
        for escenario in ESCENARIOS
        if escenario["dificultad"] == "facil"
    ]

    medios = [
        escenario
        for escenario in ESCENARIOS
        if escenario["dificultad"] == "medio"
    ]

    dificiles = [
        escenario
        for escenario in ESCENARIOS
        if escenario["dificultad"] == "dificil"
    ]

    # Elegir 1 de cada dificultad, evitando repetir conceptos

    escenarios_elegidos = []

    # Fácil
    facil = random.choice(faciles)
    escenarios_elegidos.append(facil)

    # Medio
    medios_disponibles = [
        escenario
        for escenario in medios
        if escenario["concepto"] != facil["concepto"]
    ]
    if not medios_disponibles:
        medios_disponibles = medios

    medio = random.choice(medios_disponibles)
    escenarios_elegidos.append(medio)

    # Dificil
    conceptos_usados = [
        escenario["concepto"]
        for escenario in escenarios_elegidos
    ]

    dificiles_disponibles = [
        escenario
        for escenario in dificiles
        if escenario["concepto"] not in conceptos_usados
    ]

    if not dificiles_disponibles:
        dificiles_disponibles = dificiles

    dificil = random.choice(dificiles_disponibles)
    escenarios_elegidos.append(dificil)

    return escenarios_elegidos

#Devuelve los pasos del escenario en un orden aleatorio
def mezclar_pasos(escenario):
    pasos_mezclados = escenario["pasos"].copy()
    random.shuffle(pasos_mezclados)
    return pasos_mezclados

#Comprueba si el orden elegido por el jugador coincide con el orden correcto
def comprobar_respuesta(escenario, respuesta):
    return respuesta == escenario["pasos"]


#Calcula la puntuación final de una partida.Se premia resolver la partida rápidamente y se penalizan los errores
def calcular_puntuacion(tiempo, errores):

    # Puntos base por completar los 3 niveles
    puntos_base = 1000

    # Bonificación por tiempo
    bonificacion_tiempo = max(
        0,
        600 - tiempo
    )

    # Penalización por errores
    penalizacion_errores = errores * 100

    puntuacion = (
        puntos_base
        + bonificacion_tiempo
        - penalizacion_errores
    )

    # La puntuación nunca puede ser negativa
    return max(0, puntuacion)