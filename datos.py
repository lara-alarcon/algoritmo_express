import csv
import os
from datetime import datetime

ARCHIVO_CSV = os.path.join("data", "jugadores.csv")

#Crea la carpeta data y el archivo CSV si no existen.
#Si el archivo existe pero no tiene encabezados correctos, asegura la estructura.
def crear_csv():
    if not os.path.exists("data"):
        os.makedirs("data")

    encabezados = [
        "nombre",
        "edad",
        "fecha",
        "hora",
        "escenarios",
        "puntuacion",
        "tiempo",
        "errores"
    ]

    if not os.path.exists(ARCHIVO_CSV):
        with open(
            ARCHIVO_CSV,
            "w",
            newline="",
            encoding="utf-8"
        ) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(encabezados)

def guardar_partida(
    nombre,
    edad,
    escenarios,
    puntuacion,
    tiempo,
    errores
):
    #Guarda los resultados de una partida en el CSV.
    crear_csv()

    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M")

    # Formatear nombres de escenarios
    nombres_escenarios = []
    for esc in escenarios:
        if isinstance(esc, dict) and "titulo" in esc:
            nombres_escenarios.append(esc["titulo"])
        else:
            nombres_escenarios.append(str(esc))
    
    cadena_escenarios = "-".join(nombres_escenarios)

    # Convertir valores numéricos a string/int
    try:
        puntuacion_val = int(puntuacion)
    except (ValueError, TypeError):
        puntuacion_val = 0

    try:
        tiempo_val = int(tiempo)
    except (ValueError, TypeError):
        tiempo_val = 0

    try:
        errores_val = int(errores)
    except (ValueError, TypeError):
        errores_val = 0

    with open(
        ARCHIVO_CSV,
        "a",
        newline="",
        encoding="utf-8"
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            str(nombre).strip(),
            str(edad).strip(),
            fecha,
            hora,
            cadena_escenarios,
            puntuacion_val,
            tiempo_val,
            errores_val
        ])

#Obtiene las mejores partidas ordenadas por puntuación.
def obtener_ranking(cantidad=6):
    crear_csv()

    partidas = []

    with open(
        ARCHIVO_CSV,
        "r",
        newline="",
        encoding="utf-8"
    ) as archivo:
        # Reader para leer líneas directamente
        lector = csv.reader(archivo)
        lineas = list(lector)

        if not lineas or len(lineas) <= 1:
            return []

        # Primera fila = encabezados
        encabezados = [c.strip().lower().replace("ó", "o") for c in lineas[0]]

        # Busca en qué columna está "nombre" y "puntuacion"
        idx_nombre = 0
        idx_puntuacion = 5

        for i, h in enumerate(encabezados):
            if "nombre" in h:
                idx_nombre = i
            elif "puntuacion" in h or "puntos" in h:
                idx_puntuacion = i

        # Procesar las filas de datos
        for fila in lineas[1:]:
            if not fila or len(fila) <= max(idx_nombre, idx_puntuacion):
                continue

            nombre_jugador = fila[idx_nombre].strip()
            if not nombre_jugador:
                nombre_jugador = "Anónimo"

            try:
                puntuacion_num = int(float(fila[idx_puntuacion].strip()))
            except (ValueError, TypeError):
                continue

            partidas.append({
                "nombre": nombre_jugador,
                "puntuacion": puntuacion_num
            })

    # Ordenar puntuación de mayor a menor
    partidas.sort(
        key=lambda partida: partida["puntuacion"],
        reverse=True
    )
    return partidas[:cantidad]