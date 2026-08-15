import pygame
import sys
import os

try:
    from datos import guardar_partida, obtener_ranking
except ImportError:
    from data.datos import guardar_partida, obtener_ranking

from pantallas.registro import Registro
from logica import seleccionar_escenarios, calcular_puntuacion
from pantallas.juego import Juego

FPS = 60

# Paleta
FONDO_NEGRO = (8, 12, 16)
GRILLA_COLOR = (18, 32, 28)
VERDE_NEON = (0, 255, 102)
VERDE_BRIGHT = (51, 255, 153)
VERDE_OSCURO = (15, 60, 35)
CIAN_NEON = (0, 229, 255)
BLANCO = (230, 245, 235)
ROJO_NEON = (255, 60, 90)
GRIS_TERMINAL = (40, 50, 60)

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Configuración pantalla completa adaptable
pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ANCHO, ALTO = pantalla.get_size()

pygame.display.set_caption("Algoritmo Express")
reloj = pygame.time.Clock()

# Sonidos
posibles_rutas = [
    "",
    "sounds",
    os.path.join(os.path.dirname(__file__), "sounds")
]

# Funciones
def cargar_sonido_multiruta(lista_nombres):
    for ruta_base in posibles_rutas:
        for nombre in lista_nombres:
            ruta = os.path.join(ruta_base, nombre) if ruta_base else nombre
            if os.path.exists(ruta):
                try:
                    return pygame.mixer.Sound(ruta)
                except Exception:
                    pass
    return None


def cargar_musica_multiruta(lista_nombres):
    for ruta_base in posibles_rutas:
        for nombre in lista_nombres:
            ruta = os.path.join(ruta_base, nombre) if ruta_base else nombre
            if os.path.exists(ruta):
                try:
                    pygame.mixer.music.load(ruta)
                    return True
                except Exception:
                    pass
    return False

snd_click = cargar_sonido_multiruta([
    "click.wav",
    "click.mp3",
    "grab.wav",
    "grab.mp3"
])

snd_grab = cargar_sonido_multiruta([
    "click2.wav",
    "click2.mp3",
    "grab.wav",
    "grab.mp3"
])

snd_success = cargar_sonido_multiruta([
    "success.wav",
    "success.mp3",
    "correcto.wav",
    "correcto.mp3"
])

snd_success_final = cargar_sonido_multiruta([
    "success_final.wav",
    "success_final.mp3"
])

snd_error = cargar_sonido_multiruta([
    "error.wav",
    "error.mp3"
])

snd_teclado = cargar_sonido_multiruta([
    "teclado.wav",
    "teclado.mp3"
])


class DummySound:
    def play(self):
        pass

if not snd_click:
    snd_click = DummySound()

if not snd_grab:
    snd_grab = snd_click

if not snd_success:
    snd_success = DummySound()

if not snd_success_final:
    snd_success_final = DummySound()

if not snd_error:
    snd_error = DummySound()

if not snd_teclado:
    snd_teclado = DummySound()

if hasattr(snd_click, "set_volume"):
    snd_click.set_volume(0.5)

if hasattr(snd_grab, "set_volume"):
    snd_grab.set_volume(0.5)

if hasattr(snd_success, "set_volume"):
    snd_success.set_volume(0.7)

if hasattr(snd_success_final, "set_volume"):
    snd_success_final.set_volume(0.7)    

if hasattr(snd_error, "set_volume"):
    snd_error.set_volume(0.6)

if hasattr(snd_teclado, "set_volume"):
    snd_teclado.set_volume(0.5)

# Música
if cargar_musica_multiruta(["bgm.mp3", "bgm.wav"]):
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)


# Fuentes/Tipografías
directorio_base = os.path.dirname(os.path.abspath(__file__))
nombre_archivo_ttf = "PressStart2P-Regular.ttf"
path_fuente_pixel = os.path.join(directorio_base, "fonts", nombre_archivo_ttf)

fuente_titulo = pygame.font.Font(path_fuente_pixel, int(ALTO * 0.032))

fuente_subtitulo = pygame.font.Font(path_fuente_pixel, int(ALTO * 0.020))

fuente_boton = pygame.font.Font(path_fuente_pixel, int(ALTO * 0.018))

fuente_ranking = pygame.font.Font(path_fuente_pixel, int(ALTO * 0.015))

# Botones
ancho_btn_menu = min(420, int(ANCHO * 0.35))
alto_btn_menu = int(ALTO * 0.07)
x_btn_menu = ANCHO // 2 - ancho_btn_menu // 2

boton_jugar = pygame.Rect(x_btn_menu, int(ALTO * 0.72), ancho_btn_menu, alto_btn_menu)

boton_salir = pygame.Rect(x_btn_menu, int(ALTO * 0.82), ancho_btn_menu, alto_btn_menu)

boton_volver_menu = pygame.Rect(ANCHO // 2 - 200, int(ALTO * 0.80), 400, alto_btn_menu)

# Estado del juego
registro = Registro(pantalla, ANCHO, ALTO)

pantalla_actual = "menu"
partida = []
nivel_actual = 0
juego = None

tiempo_total = 0
errores_total = 0
puntuacion_final = 0

def dibujar_fondo_retro(superficie):
    superficie.fill(FONDO_NEGRO)

    for x in range(0, ANCHO, 40):
        pygame.draw.line(
            superficie,
            GRILLA_COLOR,
            (x, 0),
            (x, ALTO),
            1
        )

    for y in range(0, ALTO, 40):
        pygame.draw.line(
            superficie,
            GRILLA_COLOR,
            (0, y),
            (ANCHO, y),
            1
        )


# Bucle principal
ejecutando = True

while ejecutando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False
            continue

        # ESC
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False
                continue

        # Menú
        if pantalla_actual == "menu":
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                posicion_mouse = evento.pos

                if boton_jugar.collidepoint(posicion_mouse):
                    snd_click.play()
                    pantalla_actual = "registro"
                    pygame.key.start_text_input()

                elif boton_salir.collidepoint(posicion_mouse):
                    snd_click.play()
                    pygame.time.delay(150)
                    ejecutando = False

        # Registro
        elif pantalla_actual == "registro":

            resultado = registro.manejar_evento(evento)

            if resultado == "volver":
                snd_click.play()
                pantalla_actual = "menu"

            elif resultado:
                snd_click.play()
                partida = seleccionar_escenarios(3)
                nivel_actual = 0
                tiempo_total = 0
                errores_total = 0

                juego = Juego(
                    pantalla,
                    ANCHO,
                    ALTO,
                    partida[nivel_actual],
                    nivel_actual + 1,
                    snd_click=snd_click,
                    snd_grab=snd_grab,
                    snd_success=snd_success,
                    snd_error=snd_error
                )
                pantalla_actual = "juego"

        # Juego
        elif pantalla_actual == "juego":

            resultado = juego.manejar_evento(evento)

            if resultado == "continuar":
                
                # Sonido click
                snd_click.play()

                tiempo_total += juego.obtener_tiempo()
                errores_total += juego.obtener_errores()
                nivel_actual += 1

                if nivel_actual >= len(partida):
                    puntuacion_final = calcular_puntuacion(
                        tiempo_total,
                        errores_total
                    )

                    guardar_partida(
                        nombre=registro.nombre,
                        edad=registro.edad,
                        escenarios=partida,
                        puntuacion=puntuacion_final,
                        tiempo=tiempo_total,
                        errores=errores_total
                    )

                    pygame.mixer.music.stop()
                    snd_success_final.play()
                    
                    pantalla_actual = "fin_juego"
                    juego = None

                else:
                    juego = Juego(
                        pantalla,
                        ANCHO,
                        ALTO,
                        partida[nivel_actual],
                        nivel_actual + 1,
                        snd_click=snd_click,
                        snd_grab=snd_grab,
                        snd_success=snd_success,
                        snd_error=snd_error
                    )

        # Fin de juego
        elif pantalla_actual == "fin_juego":

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                posicion_mouse = evento.pos

                if boton_volver_menu.collidepoint(posicion_mouse):
                    snd_click.play()

                    registro.nombre = ""
                    registro.edad = ""
                    registro.campo_activo = "nombre"

                    if cargar_musica_multiruta(["bgm.mp3", "bgm.wav"]):
                        pygame.mixer.music.set_volume(0.3)
                        pygame.mixer.music.play(-1)

                    pantalla_actual = "menu"

    # Dibujar Pantalla
    if pantalla_actual == "menu":

        dibujar_fondo_retro(pantalla)

        pygame.draw.rect(pantalla, VERDE_NEON, (20, 20, ANCHO - 40, ALTO - 40), 2)

        titulo = fuente_titulo.render(
            "[ ALGORITMO_EXPRESS.EXE ]",
            True,
            VERDE_NEON
        )

        pantalla.blit(
            titulo,
            titulo.get_rect(
                center=(ANCHO // 2, int(ALTO * 0.10))
            )
        )

        subtitulo = fuente_subtitulo.render(
            "TOP 6 MEJORES JUGADORES",
            True,
            CIAN_NEON
        )

        pantalla.blit(
            subtitulo,
            subtitulo.get_rect(
                center=(ANCHO // 2, int(ALTO * 0.18))
            )
        )

        w_panel = min(800, int(ANCHO * 0.65))
        h_panel = int(ALTO * 0.44)

        rect_panel = pygame.Rect(
            ANCHO // 2 - w_panel // 2,
            int(ALTO * 0.23),
            w_panel,
            h_panel
        )

        pygame.draw.rect(
            pantalla,
            (12, 22, 28),
            rect_panel
        )

        pygame.draw.rect(
            pantalla,
            CIAN_NEON,
            rect_panel,
            2
        )

        top_jugadores = obtener_ranking(6)

        pos_y = rect_panel.y + int(h_panel * 0.10)
        line_height = h_panel // 6

        if top_jugadores:

            for i, p in enumerate(top_jugadores, 1):
                nombre_jugador = p['nombre']
                
                # Texto izquierdo (Número y Nombre)
                texto_izq = f"{i:02d}.  {nombre_jugador}"
                surf_izq = fuente_subtitulo.render(texto_izq, True, BLANCO)
                
                # Texto derecho (Puntaje)
                texto_der = f"{p['puntuacion']} PTS"
                surf_der = fuente_subtitulo.render(texto_der, True, BLANCO)

                rect_izq = surf_izq.get_rect(midleft=(rect_panel.x + int(w_panel * 0.08), pos_y))
                
                rect_der = surf_der.get_rect(midright=(rect_panel.right - int(w_panel * 0.08), pos_y))

                # Dibujar rankingk en pantalla
                pantalla.blit(surf_izq, rect_izq)
                pantalla.blit(surf_der, rect_der)

                pos_y += line_height

        else:
            surf_vacio = fuente_subtitulo.render(
                "> NO HAY REGISTROS <",
                True,
                ROJO_NEON
            )

            pantalla.blit(
                surf_vacio,
                surf_vacio.get_rect(
                    center=rect_panel.center
                )
            )

        posicion_mouse = pygame.mouse.get_pos()

        hover_jugar = boton_jugar.collidepoint(posicion_mouse)

        pygame.draw.rect(
            pantalla,
            VERDE_BRIGHT if hover_jugar else VERDE_OSCURO,
            boton_jugar
        )

        pygame.draw.rect(
            pantalla,
            VERDE_NEON,
            boton_jugar,
            3
        )

        txt_jugar = fuente_boton.render(
            "> INICIAR_JUEGO",
            True,
            FONDO_NEGRO if hover_jugar else BLANCO
        )

        pantalla.blit(
            txt_jugar,
            txt_jugar.get_rect(
                center=boton_jugar.center
            )
        )

        hover_salir = boton_salir.collidepoint(posicion_mouse)

        pygame.draw.rect(
            pantalla,
            ROJO_NEON if hover_salir else (60, 20, 30),
            boton_salir
        )

        pygame.draw.rect(
            pantalla,
            ROJO_NEON,
            boton_salir,
            3
        )

        txt_salir = fuente_boton.render(
            "> SALIR",
            True,
            BLANCO
        )

        pantalla.blit(
            txt_salir,
            txt_salir.get_rect(
                center=boton_salir.center
            )
        )

    elif pantalla_actual == "registro":

        registro.dibujar()

    elif pantalla_actual == "juego":

        if juego:
            juego.dibujar()

    # Pantalla Final
    elif pantalla_actual == "fin_juego":

        dibujar_fondo_retro(pantalla)

        pygame.draw.rect(
            pantalla,
            VERDE_NEON,
            (20, 20, ANCHO - 40, ALTO - 40),
            2
        )

        # 1. TÍTULO
        t_fin = fuente_titulo.render(
            "[ SECUENCIA_COMPLETADA ]",
            True,
            VERDE_NEON
        )
        pantalla.blit(
            t_fin,
            t_fin.get_rect(center=(ANCHO // 2, int(ALTO * 0.18)))
        )

        # 2. PUNTUACIÓN FINAL
        t_score = fuente_subtitulo.render(
            f"PUNTUACIÓN_FINAL: {puntuacion_final} PTS",
            True,
            CIAN_NEON
        )
        pantalla.blit(
            t_score,
            t_score.get_rect(center=(ANCHO // 2, int(ALTO * 0.35)))
        )

        # 3. TIEMPO TOTAL
        t_tiempo = fuente_subtitulo.render(
            f"TIEMPO TOTAL: {tiempo_total}s",
            True,
            BLANCO
        )
        pantalla.blit(
            t_tiempo,
            t_tiempo.get_rect(center=(ANCHO // 2, int(ALTO * 0.46)))
        )

        # 4. ERRORES
        t_errores = fuente_subtitulo.render(
            f"ERRORES: {errores_total}",
            True,
            ROJO_NEON if errores_total > 0 else VERDE_BRIGHT
        )
        pantalla.blit(
            t_errores,
            t_errores.get_rect(center=(ANCHO // 2, int(ALTO * 0.57)))
        )

        # 5. BOTÓN DE MENÚ PRINCIPAL
        pos = pygame.mouse.get_pos()
        h_vol = boton_volver_menu.collidepoint(pos)

        pygame.draw.rect(
            pantalla,
            VERDE_BRIGHT if h_vol else VERDE_OSCURO,
            boton_volver_menu
        )

        pygame.draw.rect(
            pantalla,
            VERDE_NEON,
            boton_volver_menu,
            2
        )

        t_btn = fuente_boton.render(
            "> MENU_PRINCIPAL",
            True,
            FONDO_NEGRO if h_vol else BLANCO
        )

        pantalla.blit(
            t_btn,
            t_btn.get_rect(center=boton_volver_menu.center)
        )

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()