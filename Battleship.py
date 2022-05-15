
from asyncio.windows_events import NULL
from cProfile import run
from pickle import TRUE
import random
import pygame
import threading
import time
pygame.init()
# Se definen colores para usarlos mas facilmente
white = (255, 255, 255)
red = (255, 0, 0)
gray = (128, 128, 128)
blue = (0, 0, 139)
black = (0, 0, 0)
green=(0, 143, 57)

screen = pygame.display.set_mode((1000, 680))
pygame.display.set_caption('BattleShip')

# Se definen algunas fuentes
fuente = pygame.font.SysFont('Courier', 20)
fuenteBold = pygame.font.SysFont('Courier', 20, bold=1)
fuenteTitulo = pygame.font.SysFont('Courier', 30, bold=1)

# Se definen las rutas de las imagenes
sightPath = "img/sight(small).png"
daPath = "img/disparoAcertado.png"
dfPath = "img/xAzul.png"
sPath = "img/submarino.png"
dvPath = "img/destructorVertical.png"
dhPath = "img/destructorHorizontal.png"
cvPath = "img/cruceroVertical.png"
chPath = "img/cruceroHorizontal.png"
pvPath = "img/portaavionesVertical.png"
phPath = "img/portaavionesHorizontal.png"


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, font, text, action):
        super().__init__()
        text_surf = font.render(text, True, (0, 0, 0))
        self.button_image = pygame.Surface((w, h))
        self.button_image.fill((96, 96, 96))
        self.button_image.blit(
            text_surf, text_surf.get_rect(center=(w // 2, h // 2)))
        self.hover_image = pygame.Surface((w, h))
        self.hover_image.fill((96, 96, 96))
        self.hover_image.blit(
            text_surf, text_surf.get_rect(center=(w // 2, h // 2)))
        pygame.draw.rect(self.hover_image, (96, 196, 96),
                         self.hover_image.get_rect(), 3)
        self.image = self.button_image
        self.rect = pygame.Rect(x, y, w, h)
        self.action = action

    def update(self, event_list):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hover and event.button == 1:
                    self.action()
        self.image = self.hover_image if hover else self.button_image

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

BackGround = Background('img/BattleShip.png', [0,0])

class OptionBox():

    def __init__(self, x, y, w, h, color, highlight_color, font, option_list, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(
            surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i ==
                                 self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height,
                          self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1


def dibujar_texto(texto, contenedor_imagen, contenedor_rec, fuente_render, color):
    text = fuente_render.render(texto, 1, color)
    centro = text.get_rect()
    diferencia_x = contenedor_imagen.center[0] - centro.center[0]
    diferencia_y = contenedor_imagen.center[1] - centro.center[1]
    screen.blit(text, [contenedor_rec.left + diferencia_x,
                contenedor_rec.top + diferencia_y])


def validaEntrada():
    global jugadores
    j1 = Jugador("1", n1+1, n2+1, n3+1, n4+1)
    j2 = Jugador("2", n1+1, n2+1, n3+1, n4+1)
    jugadores = [j1, j2]


class Barco:
    def __init__(self, tamaño) -> None:
        self.tamaño = tamaño
        self.coord = []
        self.orient = -1
        self.destroyed = False
        # se define qué tipo de barco es según su tamaño
        self.tipo = "Submarino" if (
            self.tamaño == 1) else "Destructor" if self.tamaño == 2 else "Crucero" if self.tamaño == 3 else "Portaaviones"

    def __str__(self):
        return self.tipo

    def set_destroyed(self):
        self.destroyed = True

    def is_destroyed(self):
        destroyed = True
        for coord in self.coord:
            if str(coord[1]) == "False":
                destroyed = False
                break
        return destroyed

    def mod_coord(self, x, y):
        pos = 0
        for coord in self.coord:
            if str(coord[0]) == str(f"({x}, {y})"):
                coord = [f"{x,y}", True]
                break
            pos += 1
        self.coord[pos][1] = True

    def set_coord(self, x, y):
        self.coord.append([f"{x,y}", False])

    def get_coord(self):
        co = []
        for coord in self.coord:
            co.append(coord[0])
        return co

    def set_orient(self, o):
        self.orient = o


class Jugador:
    def __init__(self, nombre, n1, n2, n3, n4) -> None:
        self.matriz = obtener_matriz()  # genera una matriz vacía para el jugador
        self.nombre = nombre
        self.barcos = []  # arreglo de barcos del jugador
        # se agregan tantos barcos haya según la cantidad de cada uno
        for i in range(n1):
            self.barcos.append(Barco(1))

        for i in range(n2):
            self.barcos.append(Barco(2))

        for i in range(n3):
            self.barcos.append(Barco(3))
        for i in range(n4):
            self.barcos.append(Barco(4))
        # se ubican los barcos en la matriz del jugador
        for barco in self.barcos:
            ubicar_barco(self.matriz, barco)
            
            #Para imprimir las coordenadas de los barcos si desea hacer pruebas
            # print(barco)
            # print(barco.get_coord())

    def __str__(self):
        return str(self.matriz)

    def is_lose(self):
        perder = True
        for barco in self.barcos:
            if barco.destroyed == False:
                perder = False
                break
        return perder


def obtener_matriz():  # se inicializa una matriz vacía de acuerdo al número de filas y columnas
    matriz = []
    for i in range(filas):
        matriz.append([])
        for j in range(columnas):
            matriz[i].append(espacio)
    return matriz

#Espera un segundo antes de pasar el turno al siguiente jugador
def cedeTurno():
    time.sleep(1)
    global jugadorActivo
    global cediendoTurno
    jugadorActivo = 0 if jugadorActivo == 1 else 1
    cediendoTurno=False

# Funcion para los disparos
def shoot(p, jugador):
    global jugadorActivo
    global cediendoTurno
    pos = findPosition(p)
    jugOpuesto = 0 if jugadorActivo == 1 else 1
    if(pos != -1):
        a = False
        b = True
        # se mira en todos los barcos sus posiciones y se compara con la posición del disparo
        while(b):
            for barco in jugador[jugOpuesto].barcos:
                if a:
                    break
                for coord in barco.get_coord():
                    if(str(pos) == str(coord)):  # dispara en una posición donde hay un barco
                        a = True
                        b = False
                        barco.mod_coord(pos[0], pos[1])
                        # Se dibuja el disparo si acierta
                        jugador[jugadorActivo].matriz[pos[0]
                                                      ][pos[1]] = disparo_acertado
                        if barco.is_destroyed():  # se verifica si el barco está completamente destruido
                            barco.set_destroyed()
                            # si al jugador le han destruido todos sus barcos
                            if jugador[jugOpuesto].is_lose():
                                return True
                        break
                    else:
                        a = False
            if (not a):  # si no encuentra ningún barco
                if jugador[jugadorActivo].matriz[pos[0]][pos[1]] != disparo_fallado:
                    b = False
                    # Se dibuja el disparo si falla
                    jugador[jugadorActivo].matriz[pos[0]
                                                  ][pos[1]] = disparo_fallado
                    # se pasa el control al siguiente jugador
                    cediendoTurno=True
                    t = threading.Thread(target=cedeTurno)
                    t.start()
            return False

# Funcion que devuelve la casilla donde se presionó el click
def findPosition(p):
    for i in range(10):
        for j in range(10):
            # Se analiza si la posicion está dentro del rango de cada casilla
            if(p[0] > 10+j*65 and p[0] < 10+j*65+64.9 and p[1] > 20+i*65 and p[1] < 20+i*65+64.9):
                return i, j
    # retorna -1 si no está en ninguna casilla
    return -1


def is_espacio(x, y, matriz):  # indica si en las coordenadas dadas hay espacio vacío
    return matriz[x][y] == espacio


def is_rango(x, y):  # valida que las coordenadas dadas estén en el rango de las filas y columnas
    return x >= 0 and x <= columnas-1 and y >= 0 and y <= filas-1

#Cuenta la cantidad de barcos sin destruir que quedan
def contar_barcos(jugador):
    cont = [0, 0, 0, 0]
    for barco in jugador.barcos:
        if not barco.is_destroyed(): 
            if barco.tamaño == 1:
                cont[0] = cont[0]+1
            elif barco.tamaño == 2:
                cont[1] = cont[1]+1
            elif barco.tamaño == 3:
                cont[2] = cont[2]+1
            elif barco.tamaño == 4:
                cont[3] = cont[3]+1
    return cont

# función que ubica aleatorialmente un barco (no se detiene hasta que logra ubicarlo en el tablero)
def ubicar_barco(matriz, barco):
    while True:
        x = random.randint(0, filas-1)
        y = random.randint(0, columnas-1)
        # variable que de forma aleatoria determina la orientación del barco
        orientacion = random.randint(0, 1)
        # se verifica que en las coordenadas obtenidas no haya ningún otro barco
        if is_espacio(x, y, matriz):
            if barco.tamaño == 1:  # si el barco es de tamaño 1 no importa la orientación por ende se ubica en la matriz
                matriz[x][y] = str(barco.tamaño)
                barco.set_coord(x, y)
                break
            if orientacion == 1:  # Si la orientación es horizontal
                # se valida que sea posible ubicar el barco en la matriz según su tamaño
                if barco.tamaño == 2 and is_rango(x, y+1):
                    # se valida que no hayan barcos en las posiciones que se ubicará el barco
                    if is_espacio(x, y+1, matriz):
                        # se ubica el barco en su posición
                        matriz[x][y] = str(barco.tamaño)
                        matriz[x][y+1] = str(barco.tamaño)
                        # se asignan las coordenadas del barco
                        barco.set_coord(x, y)
                        barco.set_coord(x, y+1)
                        barco.set_orient(orientacion)
                        break
                if barco.tamaño == 3 and is_rango(x, y+1) and is_rango(x, y-1):
                    if is_espacio(x, y+1, matriz) and is_espacio(x, y-1, matriz):
                        matriz[x][y] = str(barco.tamaño)
                        matriz[x][y+1] = str(barco.tamaño)
                        matriz[x][y-1] = str(barco.tamaño)
                        barco.set_coord(x, y)
                        barco.set_coord(x, y+1)
                        barco.set_coord(x, y-1)
                        barco.set_orient(orientacion)
                        break
                if barco.tamaño == 4 and is_rango(x, y+1) and is_rango(x, y+2) and is_rango(x, y-1):
                    if is_espacio(x, y+1, matriz) and is_espacio(x, y+2, matriz) and is_espacio(x, y-1, matriz):
                        matriz[x][y] = str(barco.tamaño)
                        matriz[x][y+1] = str(barco.tamaño)
                        matriz[x][y-1] = str(barco.tamaño)
                        matriz[x][y+2] = str(barco.tamaño)
                        barco.set_coord(x, y)
                        barco.set_coord(x, y+1)
                        barco.set_coord(x, y-1)
                        barco.set_coord(x, y+2)
                        barco.set_orient(orientacion)
                        break
            else:  # si la orientación es vertical
                if barco.tamaño == 2 and is_rango(x+1, y):
                    if is_espacio(x+1, y, matriz):
                        matriz[x][y] = str(barco.tamaño)
                        matriz[x+1][y] = str(barco.tamaño)
                        barco.set_coord(x, y)
                        barco.set_coord(x+1, y)
                        barco.set_orient(orientacion)
                        break
                if barco.tamaño == 3 and is_rango(x+1, y) and is_rango(x-1, y):
                    if is_espacio(x+1, y, matriz) and is_espacio(x-1, y, matriz):
                        matriz[x][y] = str(barco.tamaño)
                        matriz[x+1][y] = str(barco.tamaño)
                        matriz[x-1][y] = str(barco.tamaño)
                        barco.set_coord(x, y)
                        barco.set_coord(x+1, y)
                        barco.set_coord(x-1, y)
                        barco.set_orient(orientacion)
                        break
                if barco.tamaño == 4 and is_rango(x+1, y) and is_rango(x+2, y) and is_rango(x-1, y):
                    if is_espacio(x+1, y, matriz) and is_espacio(x+2, y, matriz) and is_espacio(x-1, y, matriz):
                        matriz[x][y] = str(barco.tamaño)
                        matriz[x+1][y] = str(barco.tamaño)
                        matriz[x-1][y] = str(barco.tamaño)
                        matriz[x+2][y] = str(barco.tamaño)
                        barco.set_coord(x, y)
                        barco.set_coord(x+1, y)
                        barco.set_coord(x-1, y)
                        barco.set_coord(x+2, y)
                        barco.set_orient(orientacion)
                        break

#Pantalla de inicio del juego
def portada():
    global run
    run = True
    botonJugar = Button(screen.get_width(
    )/2-100, screen.get_height()-150, 200, 60, fuenteBold, "Jugar", continuar)
    group = pygame.sprite.Group(botonJugar)
    group.draw
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
        screen.fill([255, 255, 255])
        screen.blit(BackGround.image, BackGround.rect)
        group.update(events)
        group.draw(screen)
        pygame.display.flip()


def continuar():
    global run
    run = False

#Ventana en donde se piden los datos
def menuInicial():
    global n1
    global n2
    global n3
    global n4
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    run = True
    botonContinuar = Button(screen.get_width(
    )/2-100, screen.get_height()-150, 200, 60, fuenteBold, "Continuar", validaEntrada)
    group = pygame.sprite.Group(botonContinuar)
    group.draw
    list1 = OptionBox(
        screen.get_width()/2-80-200, screen.get_height()/2-20-200, 160, 40, (150,
                                                                             150, 150), (100, 200, 255), pygame.font.SysFont(None, 30),
        ["1", "2", "3", "4"])
    list2 = OptionBox(
        screen.get_width()/2-80-200, screen.get_height()/2-20+100, 160, 40, (150,
                                                                             150, 150), (100, 200, 255), pygame.font.SysFont(None, 30),
        ["1", "2", "3", "4"])
    list3 = OptionBox(
        screen.get_width()/2-80+200, screen.get_height()/2-20-200, 160, 40, (150,
                                                                             150, 150), (100, 200, 255), pygame.font.SysFont(None, 30),
        ["1", "2", "3", "4"])
    list4 = OptionBox(
        screen.get_width()/2-80+200, screen.get_height()/2-20+100, 160, 40, (150,
                                                                             150, 150), (100, 200, 255), pygame.font.SysFont(None, 30),
        ["1", "2", "3", "4"])
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
        if(len(jugadores) == 2):
            run = False
        list1.update(events)
        list2.update(events)
        list3.update(events)
        list4.update(events)
        group.update(events)
        n1 = list1.selected
        n2 = list2.selected
        n3 = list3.selected
        n4 = list4.selected
        screen.fill(white)
        group.draw(screen)
        dibujar_texto("Digite la cantidad de barcos para el juego", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect(screen.get_width()/2-50, 10, 100, 40), fuenteTitulo, black)
        dibujar_texto("Numero de Submarinos", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([list1.rect[0]+40, list1.rect[1]-40, list1.rect[2], list1.rect[3]]), fuente, black)
        list1.draw(screen)
        dibujar_texto("Numero de Desctructores", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([list2.rect[0]+40, list2.rect[1]-40, list2.rect[2], list2.rect[3]]), fuente, black)
        list2.draw(screen)
        dibujar_texto("Numero de Cruceros", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([list3.rect[0]+40, list3.rect[1]-40, list3.rect[2], list3.rect[3]]), fuente, black)
        list3.draw(screen)
        dibujar_texto("Numero de Portaaviones", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([list4.rect[0]+40, list4.rect[1]-40, list4.rect[2], list4.rect[3]]), fuente, black)
        list4.draw(screen)
        pygame.display.flip()

#Ventana principal del juego
def main(jugador):
    run = True
    global cediendoTurno
    ganar=False
    sight = pygame.image.load(sightPath)
    sightRect = sight.get_rect()
    disparoA = pygame.image.load(daPath)
    disparoARect = disparoA.get_rect()
    disparoF = pygame.image.load(dfPath)
    disparoFRect = disparoF.get_rect()
    submarino = pygame.image.load(sPath)
    submarinoRect = submarino.get_rect()
    destructorV = pygame.image.load(dvPath)
    destructorVRect = destructorV.get_rect()
    destructorH = pygame.image.load(dhPath)
    destructorHRect = destructorH.get_rect()
    cruceroV = pygame.image.load(cvPath)
    cruceroVRect = cruceroV.get_rect()
    cruceroH = pygame.image.load(chPath)
    cruceroHRect = cruceroH.get_rect()
    portaavionesH = pygame.image.load(phPath)
    portaavionesHRect = portaavionesH.get_rect()
    portaavionesV = pygame.image.load(pvPath)
    portaavionesVRect = portaavionesV.get_rect()

    while run:
        jugOpuesto = 0 if jugadorActivo == 1 else 1
        contBarcos=contar_barcos(jugador[jugOpuesto])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Eventos de presionar mouse
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Click izquierdo
                if event.button == 1:
                    p = pygame.mouse.get_pos()
                    if(p[0] > 10 and p[0] < 660 and p[1] > 20 and p[1] < 670 and not cediendoTurno):
                        if(shoot(p, jugador)):
                            cediendoTurno=True
                            ganar=True
            # Eventos de mover el mouse
            elif event.type == pygame.MOUSEMOTION:
                # Se actualiza la posicion de la mira
                sightRect.center = event.pos
        screen.fill(white)

        # Se recorren todos los barcos para ver cuales fueron destruidos y mostrarlos
        for barco in jugador[jugOpuesto].barcos:
            if barco.is_destroyed():
                # Si es un submarino no tenemos que mirar la orientacion
                if barco.tamaño == 1:
                    submarinoRect.center = (
                        10+65*int(barco.get_coord()[0][4])+32, 20+65*int(barco.get_coord()[0][1])+32)
                    screen.blit(submarino, submarinoRect)
                # Si la orientacion es horizontal
                if barco.orient == 1:
                    # Si es un destructor
                    if barco.tamaño == 2:
                        destructorHRect.topleft = (
                            10+65*int(barco.get_coord()[0][4]), 20+65*int(barco.get_coord()[0][1]))
                        screen.blit(destructorH, destructorHRect)
                    # Si es un crucero
                    elif barco.tamaño == 3:
                        cruceroHRect.topleft = (
                            10+65*int(barco.get_coord()[2][4]), 20+65*int(barco.get_coord()[2][1]))
                        screen.blit(cruceroH, cruceroHRect)
                    # Si es un portaaviones
                    elif barco.tamaño == 4:
                        portaavionesHRect.topleft = (
                            10+65*int(barco.get_coord()[2][4]), 20+65*int(barco.get_coord()[2][1]))
                        screen.blit(portaavionesH, portaavionesHRect)
                # Si la orientacion es vertical
                elif barco.orient == 0:
                    # Si es un destructor
                    if barco.tamaño == 2:
                        destructorVRect.topleft = (
                            10+65*int(barco.get_coord()[0][4]), 20+65*int(barco.get_coord()[0][1]))
                        screen.blit(destructorV, destructorVRect)
                    # Si es un crucero
                    elif barco.tamaño == 3:
                        cruceroVRect.topleft = (
                            10+65*int(barco.get_coord()[2][4]), 20+65*int(barco.get_coord()[2][1]))
                        screen.blit(cruceroV, cruceroVRect)
                    # Si es un portaaviones
                    elif barco.tamaño == 4:
                        portaavionesVRect.topleft = (
                            10+65*int(barco.get_coord()[2][4]), 20+65*int(barco.get_coord()[2][1]))
                        screen.blit(portaavionesV, portaavionesVRect)

        for i in range(10):
            for j in range(10):
                # Se dibujan las casillas en blanco
                pygame.draw.rect(
                    screen, gray, [10+j*65, 20+i*65, 64.9, 64.9], 1)

                #
                if(jugador[jugadorActivo].matriz[i][j] == disparo_fallado):
                    disparoFRect.center = (10+65*j+32, 20+65*i+32)
                    screen.blit(disparoF, disparoFRect)
                    # pygame.draw.rect(
                    #     screen, blue, [10+j*65, 20+i*65, 64.9, 64.9], 3)
                elif(jugador[jugadorActivo].matriz[i][j] == disparo_acertado):
                    disparoARect.center = (10+65*j+32, 20+65*i+32)
                    screen.blit(disparoA, disparoARect)
        if ganar:
            dibujar_texto("Has ganado", pygame.Surface([100, 40]).get_rect(),
                        pygame.Rect([screen.get_width()-200, 50, 100, 100]), fuenteTitulo, green)
            dibujar_texto("FIN DEL JUEGO", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-200, screen.get_height()-100, 100, 100]), fuenteTitulo, red)

        dibujar_texto("Jugador activo: "+str(jugadorActivo+1), pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-200, 20, 100, 100]), fuenteBold, black)
        dibujar_texto("# de Barcos restantes:", pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-250, 120, 100, 100]), fuenteBold, black)
        dibujar_texto("Submarinos: "+str(contBarcos[0]), pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-200, 180, 100, 100]), fuente, black)
        dibujar_texto("Destructores: "+str(contBarcos[1]), pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-200, 240, 100, 100]), fuente, black)
        dibujar_texto("Cruceros: "+str(contBarcos[2]), pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-200, 300, 100, 100]), fuente, black)
        dibujar_texto("Portaaviones: "+str(contBarcos[3]), pygame.Surface([100, 40]).get_rect(),
                      pygame.Rect([screen.get_width()-200, 360, 100, 100]), fuente, black)
        screen.blit(sight, sightRect)
        pygame.display.flip() 

portada()
filas = 10
columnas = 10
espacio = "   "
disparo_fallado = "-"
disparo_acertado = "*"
global jugadorActivo
global jugadores
global cediendoTurno
cediendoTurno=False
jugadores = []
menuInicial()
jugadorActivo = 0
main(jugadores)
pygame.quit()
