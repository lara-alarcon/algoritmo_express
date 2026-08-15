import pygame
import os

class Registro:

    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto

        pygame.mixer.init()
        self.cargar_sonidos()

        # Cargar tipografía
        directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nombre_archivo_ttf = "PressStart2P-Regular.ttf" 
        path_fuente_pixel = os.path.join(directorio_base, "fonts", nombre_archivo_ttf)

        # Tamaño de tipografía
        self.fuente_titulo = pygame.font.Font(path_fuente_pixel, int(self.alto * 0.026))
        self.fuente_texto = pygame.font.SysFont("consolas", int(self.alto * 0.030), bold=True)
        self.fuente_boton = pygame.font.Font(path_fuente_pixel, int(self.alto * 0.018))

        self.nombre = ""
        self.edad = ""
        self.campo_activo = "nombre"

        pygame.key.start_text_input()
        pygame.key.set_text_input_rect(
            pygame.Rect(
                self.ancho // 2 - 300,
                int(self.alto * 0.28),
                600,
                int(self.alto * 0.07)
            )
        )

        w_btn = min(420, int(self.ancho * 0.35))
        h_btn = int(self.alto * 0.07)
        x_btn = self.ancho // 2 - w_btn // 2

        self.boton_comenzar = pygame.Rect(
            x_btn,
            int(self.alto * 0.70),
            w_btn,
            h_btn
        )
        self.boton_volver = pygame.Rect(
            x_btn,
            int(self.alto * 0.81),
            w_btn,
            h_btn
        )

    def cargar_sonidos(self):
        self.snd_grab = None
        self.snd_drop = None
        self.snd_correcto = None
        self.snd_error = None
        self.snd_teclado = None 

        ruta_base = "sounds"

        archivos = {
            "grab": [
                "grab.wav",
                "grab.mp3",
                "click.wav",
                "click.mp3"
            ],
            "drop": [
                "drop.wav",
                "drop.mp3"
            ],
            "correcto": [
                "correcto.wav",
                "correcto.mp3"
            ],
            "error": [
                "error.wav",
                "error.mp3"
            ],
            "teclado": [ 
                "teclado.wav",
                "teclado.mp3"
            ]
        }

        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass

        def buscar_y_cargar(lista_nombres):
            for nombre in lista_nombres:
                ruta = os.path.join(ruta_base, nombre)
                if os.path.exists(ruta):
                    return pygame.mixer.Sound(ruta)
            return DummySound() 

        self.snd_grab = buscar_y_cargar(archivos["grab"])
        self.snd_drop = buscar_y_cargar(archivos["drop"])
        self.snd_correcto = buscar_y_cargar(archivos["correcto"])
        self.snd_error = buscar_y_cargar(archivos["error"])
        self.snd_teclado = buscar_y_cargar(archivos["teclado"])

    def reproducir_sonido(self, sonido):
        if sonido is not None:
            sonido.play()

    def manejar_evento(self, evento):

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_BACKSPACE:

                if self.campo_activo == "nombre" and self.nombre:
                    self.nombre = self.nombre[:-1]
                    self.reproducir_sonido(self.snd_teclado) 

                elif self.campo_activo == "edad" and self.edad:
                    self.edad = self.edad[:-1]
                    self.reproducir_sonido(self.snd_teclado)

                return False

            elif evento.key in (pygame.K_TAB, pygame.K_RETURN):

                if self.campo_activo == "nombre":
                    self.campo_activo = "edad"
                else:
                    self.campo_activo = "nombre"

                self.reproducir_sonido(self.snd_grab)
                return False

        elif evento.type == pygame.TEXTINPUT:

            texto = evento.text

            if not texto:
                return False

            if self.campo_activo == "nombre":

                if len(self.nombre) < 20:
                    self.nombre += texto
                    self.reproducir_sonido(self.snd_teclado) 

            elif self.campo_activo == "edad":

                if texto.isdigit() and len(self.edad) < 2:
                    self.edad += texto
                    self.reproducir_sonido(self.snd_teclado) 

            return False

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
        ):

            posicion = evento.pos

            w_input = min(600, int(self.ancho * 0.5))
            h_input = int(self.alto * 0.07)
            x_input = self.ancho // 2 - w_input // 2

            campo_nombre = pygame.Rect(
                x_input,
                int(self.alto * 0.28),
                w_input,
                h_input
            )

            campo_edad = pygame.Rect(
                x_input,
                int(self.alto * 0.48),
                w_input,
                h_input
            )

            if campo_nombre.collidepoint(posicion):

                if self.campo_activo != "nombre":
                    self.campo_activo = "nombre"
                    self.reproducir_sonido(self.snd_grab)

            elif campo_edad.collidepoint(posicion):

                if self.campo_activo != "edad":
                    self.campo_activo = "edad"
                    self.reproducir_sonido(self.snd_grab)

            elif self.boton_comenzar.collidepoint(posicion):

                if self.nombre.strip() == "" or self.edad == "":
                    self.reproducir_sonido(self.snd_error)
                    return False

                self.reproducir_sonido(self.snd_correcto)
                pygame.key.stop_text_input()

                return True

            elif self.boton_volver.collidepoint(posicion):

                self.reproducir_sonido(self.snd_grab)
                pygame.key.stop_text_input()

                return "volver"

        return False

    def dibujar(self):

        FONDO_NEGRO = (8, 12, 16)
        GRILLA_COLOR = (18, 32, 28)
        VERDE_NEON = (0, 255, 102)
        VERDE_BRIGHT = (51, 255, 153)
        VERDE_OSCURO = (15, 60, 35)
        CIAN_NEON = (0, 229, 255)
        BLANCO = (230, 245, 235)

        self.pantalla.fill(FONDO_NEGRO)

        for x in range(0, self.ancho, 40):
            pygame.draw.line(
                self.pantalla,
                GRILLA_COLOR,
                (x, 0),
                (x, self.alto),
                1
            )

        for y in range(0, self.alto, 40):
            pygame.draw.line(
                self.pantalla,
                GRILLA_COLOR,
                (0, y),
                (self.ancho, y),
                1
            )

        pygame.draw.rect(
            self.pantalla,
            VERDE_NEON,
            (20, 20, self.ancho - 40, self.alto - 40),
            2
        )

        titulo = self.fuente_titulo.render(
            "> AUTENTIFICACIÓN_DE_USUARIO <",
            True,
            VERDE_NEON
        )

        self.pantalla.blit(
            titulo,
            titulo.get_rect(
                center=(
                    self.ancho // 2,
                    int(self.alto * 0.12)
                )
            )
        )

        w_input = min(600, int(self.ancho * 0.5))
        h_input = int(self.alto * 0.07)
        x_input = self.ancho // 2 - w_input // 2

        txt_n = self.fuente_texto.render(
            "$ Nombre o Apodo:",
            True,
            BLANCO
        )

        self.pantalla.blit(
            txt_n,
            (x_input, int(self.alto * 0.22))
        )

        r_nombre = pygame.Rect(
            x_input,
            int(self.alto * 0.28),
            w_input,
            h_input
        )

        bg_n = (
            VERDE_OSCURO
            if self.campo_activo == "nombre"
            else (15, 25, 30)
        )

        pygame.draw.rect(
            self.pantalla,
            bg_n,
            r_nombre
        )

        pygame.draw.rect(
            self.pantalla,
            (
                VERDE_NEON
                if self.campo_activo == "nombre"
                else CIAN_NEON
            ),
            r_nombre,
            2
        )

        cursor_n = "_" if self.campo_activo == "nombre" else ""

        val_n = self.fuente_texto.render(
            self.nombre + cursor_n,
            True,
            BLANCO
        )

        self.pantalla.blit(
            val_n,
            (
                r_nombre.x + 15,
                r_nombre.y
                + (r_nombre.height - val_n.get_height()) // 2
            )
        )

        txt_e = self.fuente_texto.render(
            "$ Edad:",
            True,
            BLANCO
        )

        self.pantalla.blit(
            txt_e,
            (x_input, int(self.alto * 0.42))
        )

        r_edad = pygame.Rect(
            x_input,
            int(self.alto * 0.48),
            w_input,
            h_input
        )

        bg_e = (
            VERDE_OSCURO
            if self.campo_activo == "edad"
            else (15, 25, 30)
        )

        pygame.draw.rect(
            self.pantalla,
            bg_e,
            r_edad
        )

        pygame.draw.rect(
            self.pantalla,
            (
                VERDE_NEON
                if self.campo_activo == "edad"
                else CIAN_NEON
            ),
            r_edad,
            2
        )

        cursor_e = "_" if self.campo_activo == "edad" else ""

        val_e = self.fuente_texto.render(
            self.edad + cursor_e,
            True,
            BLANCO
        )

        self.pantalla.blit(
            val_e,
            (
                r_edad.x + 15,
                r_edad.y
                + (r_edad.height - val_e.get_height()) // 2
            )
        )

        pos = pygame.mouse.get_pos()

        h_com = self.boton_comenzar.collidepoint(pos)

        pygame.draw.rect(
            self.pantalla,
            VERDE_BRIGHT if h_com else VERDE_OSCURO,
            self.boton_comenzar
        )

        pygame.draw.rect(
            self.pantalla,
            VERDE_NEON,
            self.boton_comenzar,
            3
        )

        t_com = self.fuente_boton.render(
            "> INICIAR_JUEGO",
            True,
            FONDO_NEGRO if h_com else BLANCO
        )

        self.pantalla.blit(
            t_com,
            t_com.get_rect(
                center=self.boton_comenzar.center
            )
        )

        h_vol = self.boton_volver.collidepoint(pos)

        pygame.draw.rect(
            self.pantalla,
            VERDE_BRIGHT if h_vol else (25, 35, 45),
            self.boton_volver
        )

        pygame.draw.rect(
            self.pantalla,
            CIAN_NEON,
            self.boton_volver,
            2
        )

        t_vol = self.fuente_boton.render(
            "> VOLVER_AL_MENU",
            True,
            FONDO_NEGRO if h_vol else BLANCO
        )

        self.pantalla.blit(
            t_vol,
            t_vol.get_rect(
                center=self.boton_volver.center
            )
        )