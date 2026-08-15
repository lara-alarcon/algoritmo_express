import pygame
import random
import time
import os


class Juego:

    def __init__(self, pantalla, ancho, alto, escenario, nivel, snd_click=None, snd_grab=None, snd_success=None, snd_error=None):

        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto

        self.escenario = escenario
        self.nivel = nivel

        # Asignar/ Cargar audio
        if snd_click and snd_success and snd_error:
            self.snd_click = snd_click
            self.snd_grab = snd_grab if snd_grab else snd_click
            self.snd_drop = None
            self.snd_correcto = snd_success
            self.snd_error = snd_error
        else:
            pygame.mixer.init()
            self.cargar_sonidos()

        # Tipografías
        directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nombre_archivo_ttf = "PressStart2P-Regular.ttf" 
        path_fuente_pixel = os.path.join(directorio_base, "fonts", nombre_archivo_ttf)

        self.fuente_escenario = pygame.font.Font(path_fuente_pixel, int(self.alto * 0.028))
        self.fuente_titulo = pygame.font.Font(path_fuente_pixel, int(self.alto * 0.024))
        self.fuente_texto = pygame.font.SysFont("consolas", int(self.alto * 0.023), bold=True)
        self.fuente_explicacion = pygame.font.SysFont("consolas", int(self.alto * 0.023), bold=True)
        self.fuente_boton = pygame.font.Font(path_fuente_pixel, int(self.alto * 0.018))
        self.fuente_paso = pygame.font.SysFont("consolas", int(self.alto * 0.023), bold=True)

        self.pasos = escenario["pasos"].copy()
        random.shuffle(self.pasos)

        self.tarjetas = []

        self.tarjeta_arrastrada = None
        self.offset_x = 0
        self.offset_y = 0

        self.mensaje = ""
        self.explicacion = ""
        self.mostrar_resultado = False
        self.tarjetas_bloqueadas = False

        self.errores = 0
        self.tiempo_inicio = time.time()

        # Botón parte inferior
        w_btn = min(420, int(self.ancho * 0.32))
        h_btn = int(self.alto * 0.065)
        self.boton_comprobar = pygame.Rect(
            self.ancho // 2 - w_btn // 2, 
            self.alto - h_btn - int(self.alto * 0.035), 
            w_btn, 
            h_btn
        )
        self.boton_reintentar = pygame.Rect(
            self.ancho // 2 - w_btn // 2, 
            self.alto - h_btn - int(self.alto * 0.035), 
            w_btn, 
            h_btn
        )

        self.crear_tarjetas()

    def cargar_sonidos(self):
        self.snd_click = pygame.mixer.Sound("click.wav")
        self.snd_grab = pygame.mixer.Sound("click2.wav")
        self.snd_drop = pygame.mixer.Sound("drop.wav")
        self.snd_correcto = pygame.mixer.Sound("success.wav")
        self.snd_error = pygame.mixer.Sound("error.wav")
        self.snd_victoria = pygame.mixer.Sound("success_final.wav")

    def reproducir_sonido(self, sonido):
        if sonido is not None:
            sonido.play()

    def crear_tarjetas(self):
        cantidad = len(self.pasos)
        
        ancho_tarjeta = min(1100, int(self.ancho * 0.78))
        x = self.ancho // 2 - ancho_tarjeta // 2 

        if cantidad >= 6:
            alto_tarjeta = int(self.alto * 0.060)
            inicio_y = int(self.alto * 0.24)
            espacio = 6
        else:
            alto_tarjeta = int(self.alto * 0.070)
            inicio_y = int(self.alto * 0.27)
            espacio = 10

        self.tarjetas = []
        for i, paso in enumerate(self.pasos):
            rect = pygame.Rect(
                x,
                inicio_y + i * (alto_tarjeta + espacio),
                ancho_tarjeta,
                alto_tarjeta
            )
            self.tarjetas.append({"texto": paso, "rect": rect})

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            posicion = evento.pos

            # Sonido click botones
            if self.boton_comprobar.collidepoint(posicion):
                if self.mensaje == "":
                    self.comprobar_respuesta()
                    return
                elif self.mensaje == "ORDEN INCORRECTO":
                    self.reproducir_sonido(self.snd_click) 
                    self.mensaje = ""
                    self.mostrar_resultado = False
                    self.tarjetas_bloqueadas = False
                    return
                elif self.mensaje == "¡CORRECTO!":
                    self.reproducir_sonido(self.snd_click)
                    return "continuar"

            if self.tarjetas_bloqueadas:
                return

            # Sonido click tarjetas
            for tarjeta in self.tarjetas:
                if tarjeta["rect"].collidepoint(posicion):
                    self.tarjeta_arrastrada = tarjeta
                    self.offset_x = tarjeta["rect"].x - posicion[0]
                    self.offset_y = tarjeta["rect"].y - posicion[1]
                    self.reproducir_sonido(self.snd_grab)  
                    break

        elif evento.type == pygame.MOUSEMOTION:
            if self.tarjeta_arrastrada is not None:
                pos = evento.pos
                self.tarjeta_arrastrada["rect"].x = pos[0] + self.offset_x
                self.tarjeta_arrastrada["rect"].y = pos[1] + self.offset_y

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.tarjeta_arrastrada is not None:
                tarjeta_movida = self.tarjeta_arrastrada
                tarjeta_destino = None

                for tarjeta in self.tarjetas:
                    if tarjeta is tarjeta_movida:
                        continue
                    if tarjeta["rect"].collidepoint(evento.pos):
                        tarjeta_destino = tarjeta
                        break

                if tarjeta_destino is not None:
                    i1 = self.tarjetas.index(tarjeta_movida)
                    i2 = self.tarjetas.index(tarjeta_destino)
                    self.tarjetas[i1], self.tarjetas[i2] = self.tarjetas[i2], self.tarjetas[i1]

                self.reorganizar_tarjetas()
                self.tarjeta_arrastrada = None

    def reorganizar_tarjetas(self):
        cantidad = len(self.tarjetas)
        
        ancho_tarjeta = min(1100, int(self.ancho * 0.78))
        x = self.ancho // 2 - ancho_tarjeta // 2

        if cantidad >= 6:
            alto_tarjeta = int(self.alto * 0.060)
            inicio_y = int(self.alto * 0.24)
            espacio = 6
        else:
            alto_tarjeta = int(self.alto * 0.070)
            inicio_y = int(self.alto * 0.27)
            espacio = 10

        for i, tarjeta in enumerate(self.tarjetas):
            tarjeta["rect"].x = x
            tarjeta["rect"].y = inicio_y + i * (alto_tarjeta + espacio)
            tarjeta["rect"].width = ancho_tarjeta
            tarjeta["rect"].height = alto_tarjeta

    def comprobar_respuesta(self):
        orden_j = [t["texto"] for t in self.tarjetas]
        if orden_j == self.escenario["pasos"]:
            self.mensaje = "¡CORRECTO!"
            self.explicacion = self.escenario["explicacion"]
            self.mostrar_resultado = True
            self.tarjetas_bloqueadas = True
            self.reproducir_sonido(self.snd_correcto)
        else:
            self.mensaje = "ORDEN INCORRECTO"
            self.mostrar_resultado = True
            self.tarjetas_bloqueadas = True
            self.errores += 1
            self.reproducir_sonido(self.snd_error)

    def obtener_tiempo(self):
        return int(time.time() - self.tiempo_inicio)

    def obtener_errores(self):
        return self.errores

    def dividir_texto_balanceado(self, texto, fuente, ancho_maximo):
        palabras = texto.split(' ')
        lineas = []
        linea_actual = []

        for palabra in palabras:
            linea_test = ' '.join(linea_actual + [palabra])
            if fuente.size(linea_test)[0] <= ancho_maximo:
                linea_actual.append(palabra)
            else:
                if linea_actual:
                    lineas.append(' '.join(linea_actual))
                linea_actual = [palabra]

        if linea_actual:
            lineas.append(' '.join(linea_actual))

        return lineas

    def _dibujar_tarjeta(self, tarjeta, idx, pos_mouse):
        BLANCO = (230, 245, 235)
        VERDE_NEON = (0, 255, 102)
        CIAN_NEON = (0, 229, 255)

        rect = tarjeta["rect"]
        is_dragging = tarjeta is self.tarjeta_arrastrada
        is_hover = rect.collidepoint(pos_mouse)

        bg_color = (25, 45, 35) if is_dragging else ((20, 35, 40) if is_hover else (12, 22, 28))
        border_color = CIAN_NEON if is_dragging else (VERDE_NEON if is_hover else (35, 70, 55))

        pygame.draw.rect(self.pantalla, bg_color, rect)
        pygame.draw.rect(self.pantalla, border_color, rect, 2)

        str_paso = f"[{idx:02d}] > {tarjeta['texto']}"
        ancho_max = rect.width - 40
        if self.fuente_paso.size(str_paso)[0] > ancho_max:
            while self.fuente_paso.size(str_paso + "...")[0] > ancho_max and len(str_paso) > 0:
                str_paso = str_paso[:-1]
            str_paso += "..."

        t_txt = self.fuente_paso.render(str_paso, True, BLANCO)
        self.pantalla.blit(t_txt, (rect.x + 20, rect.y + (rect.height - t_txt.get_height()) // 2))

    def dibujar(self):

        FONDO_NEGRO = (8, 12, 16)
        GRILLA_COLOR = (18, 32, 28)
        VERDE_NEON = (0, 255, 102)
        VERDE_BRIGHT = (51, 255, 153)
        VERDE_OSCURO = (15, 60, 35)
        CIAN_NEON = (0, 229, 255)
        BLANCO = (230, 245, 235)
        ROJO_NEON = (255, 60, 90)

        self.pantalla.fill(FONDO_NEGRO)

        # Grilla
        for x in range(0, self.ancho, 40):
            pygame.draw.line(self.pantalla, GRILLA_COLOR, (x, 0), (x, self.alto), 1)
        for y in range(0, self.alto, 40):
            pygame.draw.line(self.pantalla, GRILLA_COLOR, (0, y), (self.ancho, y), 1)

        # Encabezado
        t_niv = self.fuente_titulo.render(f"[ LEVEL_0{self.nivel} ]", True, VERDE_NEON)
        self.pantalla.blit(t_niv, (40, 25))

        seg = self.obtener_tiempo()
        t_time = self.fuente_titulo.render(f"TIEMPO: {seg//60:02d}:{seg%60:02d}s", True, CIAN_NEON)
        self.pantalla.blit(t_time, (self.ancho - t_time.get_width() - 40, 25))

        # Título
        titulo_mayus = self.escenario['titulo'].upper()
        t_esc = self.fuente_escenario.render(f"DESAFÍO: {titulo_mayus}", True, VERDE_NEON)
        self.pantalla.blit(t_esc, t_esc.get_rect(center=(self.ancho // 2, int(self.alto * 0.085))))

        t_hist = self.fuente_texto.render(f" {self.escenario['historia']} ", True, BLANCO)
        self.pantalla.blit(t_hist, t_hist.get_rect(center=(self.ancho // 2, int(self.alto * 0.145))))

        t_inst = self.fuente_texto.render(">>> Arrastrá y ordená las tarjetas de arriba a abajo en el orden lógico correcto:", True, CIAN_NEON)
        self.pantalla.blit(t_inst, t_inst.get_rect(center=(self.ancho // 2, int(self.alto * 0.20))))

        # Tarjetas
        pos_mouse = pygame.mouse.get_pos()

        for idx, tarjeta in enumerate(self.tarjetas, 1):
            if tarjeta is not self.tarjeta_arrastrada:
                self._dibujar_tarjeta(tarjeta, idx, pos_mouse)

        if self.tarjeta_arrastrada is not None:
            idx_arr = self.tarjetas.index(self.tarjeta_arrastrada) + 1
            self._dibujar_tarjeta(self.tarjeta_arrastrada, idx_arr, pos_mouse)

        # Mensaje de resultado
        if self.mostrar_resultado:
            clr = VERDE_NEON if self.mensaje == "¡CORRECTO!" else ROJO_NEON
            t_msg = self.fuente_escenario.render(f"=== {self.mensaje} ===", True, clr)
            ult_tarjeta = self.tarjetas[-1]["rect"]
            pos_y_status = ult_tarjeta.bottom + int(self.alto * 0.08)
            self.pantalla.blit(t_msg, t_msg.get_rect(center=(self.ancho // 2, pos_y_status)))

            if self.mensaje == "¡CORRECTO!":
                ancho_max = min(1300, self.ancho - 100)
                lineas = self.dividir_texto_balanceado(self.explicacion, self.fuente_explicacion, ancho_max)
                pos_y_exp = pos_y_status + int(self.alto * 0.085)

                for l in lineas:
                    t_exp = self.fuente_explicacion.render(l, True, BLANCO)
                    self.pantalla.blit(t_exp, t_exp.get_rect(center=(self.ancho // 2, pos_y_exp)))
                    # Interlineado más ajustado (2.5% del alto)
                    pos_y_exp += int(self.alto * 0.025)

        # Botón acción
        if self.mensaje == "¡CORRECTO!":
            btn = self.boton_comprobar
            lbl = "> SIGUIENTE_NIVEL"
            c_bg = VERDE_BRIGHT
            c_fg = FONDO_NEGRO
        elif self.mensaje == "ORDEN INCORRECTO":
            btn = self.boton_reintentar
            lbl = "> REINTENTAR"
            c_bg = ROJO_NEON
            c_fg = BLANCO
        else:
            btn = self.boton_comprobar
            lbl = "> COMPROBAR"
            h = btn.collidepoint(pos_mouse)
            c_bg = VERDE_BRIGHT if h else VERDE_OSCURO
            c_fg = FONDO_NEGRO if h else BLANCO

        pygame.draw.rect(self.pantalla, c_bg, btn)
        pygame.draw.rect(self.pantalla, VERDE_NEON if self.mensaje != "ORDEN INCORRECTO" else ROJO_NEON, btn, 2)
        t_btn = self.fuente_boton.render(lbl, True, c_fg)
        self.pantalla.blit(t_btn, t_btn.get_rect(center=btn.center))