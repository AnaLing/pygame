import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img') #El directorio donde estarán las imágenes

WIDTH = 480
HEIGHT = 600
FPS = 60


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# Inicializamos pygame y creamos una ventana
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial') #El tipo de letra del texto que aparecerá en la ventana
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
    
def newmob(): #Esto es para los meteoritos
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Jugador 1
class Player1(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player1_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 4
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def move_left(self):
        self.rect.x += -8

    def move_right(self):
        self.rect.x += 8

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -8
        if keystate[pygame.K_d]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet1 = Bullet(self.rect.centerx, self.rect.top) #El jugador 1 tiene sus propias balas que se meterán en el grupo bullets1.
        all_sprites.add(bullet1)
        bullets1.add(bullet1)

# Jugador 2
class Player2(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player2_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH * 3 / 4
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def move_left(self):
        self.rect.x += -8

    def move_right(self):
        self.rect.x += 8

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet2 = Bullet(self.rect.centerx, self.rect.top) #El jugador 2 tiene sus propias balas que se meterán en el grupo bullets2.
        all_sprites.add(bullet2)
        bullets2.add(bullet2)

class Bullet(pygame.sprite.Sprite): #Balas que dispara cada jugador
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Mob(pygame.sprite.Sprite): #Meteoritos a los que deben disparar los jugadores
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = meteor_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

def show_go_screen(): #Esta es la pantalla del inicio
    screen.blit(background, background_rect)
    draw_text(screen, "Galaxy", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Player 1: A D keys to move, S to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Player 2: Arrow keys to move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2+50)
    draw_text(screen, "Press ESC to exit. Press SPACE to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False              
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    running = False              
                    pygame.quit()
                    exit()
                
def show_go_screen_end(): #Esta es la pantalla del game over, se puede reiniciar el juego presionando space
    screen.blit(background, background_rect)
    draw_text(screen, "GAME OVER", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Player 1: "+str(score[0])+" | "+ "Player 2: "+str(score[1]), 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press ESC to exit. Press SPACE to restart" , 18, WIDTH / 2, HEIGHT * 3 / 4)

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False              
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    running = False              
                    pygame.quit()
                    exit()
class Network:
    def __init__(self): ##this will connect to the server initially
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1' #server ip #<---
        self.port = 5555   #server port #<---
        self.addr = (self.server, self.port)
        self.p = self.connect()
    def getP(self):
        return self.p
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)

#Ejecutamos ahora el proceso del juego
#Primero cargamos todas las imágenes

background = pygame.image.load(path.join(img_dir, "backgroundshooter.png")).convert()
background_rect = background.get_rect()
player1_img = pygame.image.load(path.join(img_dir, "playershooter1.png")).convert()
player2_img = pygame.image.load(path.join(img_dir, "playershooter2.png")).convert()
meteor_img = pygame.image.load(path.join(img_dir, "meteorshooter.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "lasershooter.png")).convert()


# Creación de los sprites
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets1 = pygame.sprite.Group()
bullets2 = pygame.sprite.Group()
for i in range(5):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Reloj
clock = pygame.time.Clock()

# Variables del juego
score = [0,0]
game_over = True
running = True
spawn_timer = 0
spawn_delay = 30

# Bucle principal
while running:
    # Procesamiento de eventos
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets1 = pygame.sprite.Group()
        bullets2 = pygame.sprite.Group()
        players = pygame.sprite.Group()
        player1 = Player1()
        player2 = Player2()
        all_sprites.add(player1)
        all_sprites.add(player2)
        for i in range(5):
            newmob()
        score = [0,0]

    clock.tick(FPS)
    
    #Analizamos los eventos, es decir, las teclas que se presionan y sus consecuentes efectos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False
            running = False              
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player1.move_left()
            elif event.key == pygame.K_d:
                player1.move_right()
            elif event.key == pygame.K_s:
                player1.shoot()
            elif event.key == pygame.K_LEFT:
                player2.move_left()
            elif event.key == pygame.K_RIGHT:
                player2.move_right()
            elif event.key == pygame.K_SPACE:
                player2.shoot()
            elif event.key == pygame.K_ESCAPE:
                game_over = False
                running = False              
                pygame.quit()
                exit() 

    # Actualización de sprites
    all_sprites.update()

    # Colisiones de los sprites
    hits1 = pygame.sprite.groupcollide(mobs, bullets1, True, True) #Estos son los meteoritos que destruye el jugador 1
    for hit in hits1:
       score[0] += 1
       m = Mob()  #Cuando se le da a un meteorito, este desaparece y debemos crear más
       all_sprites.add(m)
       mobs.add(m)

    hits2 = pygame.sprite.groupcollide(mobs, bullets2, True, True) #Estos son los meteoritos que destruye el jugador 2
    for hit in hits2:
       score[1] += 1
       m = Mob()
       all_sprites.add(m)
       mobs.add(m)

    #Si a alguno de los jugadores le da un meteorito se acaba el juego
    hits = pygame.sprite.spritecollide(player1, mobs, False) #Si le da al jugador 1
    if hits:
        show_go_screen_end()
        game_over = True

    hits = pygame.sprite.spritecollide(player2, mobs, False) #Si le da al jugador 2
    if hits:
        show_go_screen_end()
        game_over = True

    #Este sería el refresh
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score[0]), 18, WIDTH // 3, 10)
    draw_text(screen, str(score[1]), 18, 2*(WIDTH) // 3, 10)
    pygame.display.flip()   

pygame.quit()
