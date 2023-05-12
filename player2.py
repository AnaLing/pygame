from multiprocessing.connection import Client
from multiprocessing import Value
import traceback
import pygame
import sys, os
from os import path

img_dir = path.join(path.dirname(__file__), 'img') #El directorio donde estarán las imágenes
pygame.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 10
BALL_COLOR = WHITE
BALL_SIZE = 5
FPS = 60
SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

screen = pygame.display.set_mode(SIZE)
clock =  pygame.time.Clock()  #FPS
background = pygame.image.load(path.join(img_dir, "background.png")).convert()
background_rect = background.get_rect()
font_name = pygame.font.match_font('arial') #El tipo de letra del texto que aparecerá en la ventana


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def show_go_screen_end(self): #Esta es la pantalla del game over
    screen.blit(background, background_rect)
    draw_text(screen, "GAME OVER", 64, SIZE[0] / 2, SIZE[1] / 4)
    draw_text(screen, "Player 1: "+str(self.score[0])+" | "+ "Player 2: "+str(self.score[1]), 22,
              SIZE[0] / 2, SIZE[1] / 2)
    pygame.display.flip()


class Player():

    def __init__(self, side):
        self.side = side
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"


class Ball():

    def __init__(self):
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"


class Game():

    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.ballsleft = []
        self.ballsright = []
        self.indexleft = Value('i', 0)
        self.indexright = Value('i', 0)
        self.indexleftaux = Value('i', 0)
        self.indexrightaux = Value('i', 0)
        self.score = [0,0]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def get_ball_left(self):
       return self.ballsleft[self.indexleftaux.value]
       
    def get_ball_right(self):
       return self.ballsright[self.indexrightaux.value]

    def set_ball_pos_left(self, pos):
       for i in pos:
           self.ballsleft.append(Ball())
           self.ballsleft[self.indexleft.value].set_pos(i) 
           self.indexleft.value += 1

    def set_ball_pos_right(self, pos):
       for i in pos:
           self.ballsright.append(Ball())
           self.ballsright[self.indexright.value].set_pos(i)
           self.indexright.value += 1

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos_left(gameinfo['pos_left_ball'])
        self.set_ball_pos_right(gameinfo['pos_right_ball'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}>"


class Paddle(pygame.sprite.Sprite):

    def __init__(self, player, side):
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
      self.rect = self.image.get_rect()
      self.update(side)

    def update(self, side):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BallSprite(pygame.sprite.Sprite):

    def __init__(self, ball, side):
        super().__init__()
        self.ball = ball
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        if self.ball == None:
            pos = [None, None]
        else:
            pos = self.ball.get_pos()
            self.rect.centerx, self.rect.centery = pos
            if side == LEFT_PLAYER:
                self.speedx = 10
            else:
                self.speedx = -10

    def update(self, side):
        if side == LEFT_PLAYER:
            self.rect.x += self.speedx
        else:
            self.rect.x += self.speedx
        if self.rect.centerx < 0 or self.rect.centerx > SIZE[0]:
            self.kill()


class Display():

    def __init__(self, game):
        self.all_sprites = pygame.sprite.Group()
        self.balls1 = []
        self.balls2 = []
        self.balls_group = pygame.sprite.Group()
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i), i) for i in range(2)]
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        for i in range(len(self.game.ballsleft)):
            self.balls1.append(BallSprite(self.game.get_ball_left(), 0))
            self.game.indexleftaux.value += 1
        for i in range(len(self.game.ballsright)):
            self.balls2.append(BallSprite(self.game.get_ball_right(), 1))
            self.game.indexrightaux.value += 1   
        for ball in self.balls1:
            self.all_sprites.add(ball)
            self.balls_group.add(ball)
        for ball in self.balls2:
            self.all_sprites.add(ball) 
            self.balls_group.add(ball)   
        self.score = [0,0]

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
                elif event.key == pygame.K_SPACE:
                    events.append("shoot")
            elif event.type == pygame.QUIT:
                events.append("quit")
        if side == LEFT_PLAYER:
          hit = pygame.sprite.spritecollide(self.paddles[LEFT_PLAYER], self.balls_group, False)
          if hit:
             events.append("collide")
             show_go_screen_end(self)
        else:
          hit = pygame.sprite.spritecollide(self.paddles[RIGHT_PLAYER], self.balls_group, False)
          if hit:
             events.append("collide")
             show_go_screen_end(self)
        return events

    def refresh(self, side):
        self.all_sprites.update(side)
        screen.blit(background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        screen.blit(text, (250, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprites.draw(screen)
        pygame.display.flip()

    def tick(self):
        clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                print('c1', gameinfo)
                game.update(gameinfo)
                display.refresh(side)
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
