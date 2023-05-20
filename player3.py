from multiprocessing.connection import Client
from multiprocessing import Value
import traceback
import pygame
import sys, os
from os import path

img_dir = path.join(path.dirname(__file__), 'img') #El directorio donde estarán las imágenes
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
PLAYER_WIDTH = 30
BALL_COLOR = WHITE
BALL_SIZE = 5
FPS = 60
SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]


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
        self.id = None

    def get_pos(self):
        return self.pos
    
    def get_id(self):
        return self.id

    def set_pos(self, pos):
        self.pos = pos
    
    def set_id(self, id):
        self.id = id
        
    def __str__(self):
        return f"B<{self.pos}>"


class Game():

    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.ballsleft = []
        self.ballsright = []
        self.indexleft = Value('i', 0)
        self.indexright = Value('i', 0)
        self.score = [0,0]
        self.running = True
        self.id_malos = []
        

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)


    def set_ball_pos_left(self, pos):
       for i in pos:
           self.ballsleft.append(Ball())
           self.ballsleft[self.indexleft.value].set_pos(i[0]) 
           self.ballsleft[self.indexleft.value].set_id(i[1])
           self.indexleft.value += 1

    def set_ball_pos_right(self, pos):
       for i in pos:
           self.ballsright.append(Ball())
           self.ballsright[self.indexright.value].set_pos(i[0])
           self.ballsright[self.indexright.value].set_id(i[1])
           self.indexright.value += 1

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
    
    def set_id_malos(self, id_malos):
        self.id_malos = id_malos

    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos_left(gameinfo['pos_left_ball'])
        self.set_ball_pos_right(gameinfo['pos_right_ball'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
        self.set_id_malos(gameinfo['id_malos'])
        
    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}>"


class Paddle(pygame.sprite.Sprite):

    def __init__(self, player, side):
      super().__init__()
      self.player1_img = pygame.image.load(path.join(img_dir, "player1.png")).convert()
      self.player2_img = pygame.image.load(path.join(img_dir, "player2.png")).convert()
      if side == LEFT_PLAYER:
         self.image = pygame.transform.scale(self.player1_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
         self.image.set_colorkey(BLACK)
      else:
         self.image = pygame.transform.scale(self.player2_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
         self.image.set_colorkey(BLACK)
      self.player = player
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BallSprite(pygame.sprite.Sprite):

    def __init__(self, ball, side):
        super().__init__()
        self.ball = ball
        self.id = self.ball.get_id()
        self.bullet_img = pygame.image.load(path.join(img_dir, "laser.png")).convert()
        self.image = pygame.transform.scale(self.bullet_img, (10, BALL_SIZE))
        self.image.set_colorkey(BLACK)       
        self.rect = self.image.get_rect()
        if self.ball == None:
            pos = [None, None]
            self.speedx = 0
        else:
            pos = self.ball.get_pos()
            self.rect.centerx, self.rect.centery = pos
            if side == LEFT_PLAYER:
                self.speedx = 10
            else:
                self.speedx = -10
        self.update()
        
    def get_id(self):
        return self.id
    
    def update(self):
        self.rect.x += self.speedx
        if self.rect.x < 0 or self.rect.x > SIZE[0]:
            self.kill()


class Display():

    def __init__(self, game):
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load(path.join(img_dir, "background.png")).convert()
        background_rect = self.background.get_rect()
        pygame.init()
        self.all_sprites = pygame.sprite.Group()
        self.balls1 = []
        self.balls2 = []
        self.balls1_group = pygame.sprite.Group()
        self.balls2_group = pygame.sprite.Group()
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i), i) for i in range(2)]
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)   
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
          hit = pygame.sprite.spritecollide(self.paddles[LEFT_PLAYER], self.balls2_group, False)
          if hit:
             events.append("collide")           
        else:
          hit = pygame.sprite.spritecollide(self.paddles[RIGHT_PLAYER], self.balls1_group, False)
          if hit:
             events.append("collide")             
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        for i in self.game.ballsleft:          
            self.balls1.append(BallSprite(i, 0))          
        for i in self.game.ballsright:
            self.balls2.append(BallSprite(i, 1))
        self.balls1aux = self.balls1
        self.balls2aux = self.balls2
        self.index1 = 0
        self.index2 = 0
        for ball in self.balls1aux:
            for id in self.game.id_malos:
                if ball.get_id() == id:
                  self.balls1.pop(self.index1)
            self.index1 += 1            
        for ball in self.balls2aux:
            for id in self.game.id_malos:
                if ball.get_id() == id:
                  self.balls2.pop(self.index2)
            self.index2 += 1                
        for ball in self.balls1:
            self.all_sprites.add(ball)
            self.balls1_group.add(ball)
        for ball in self.balls2:
            self.all_sprites.add(ball) 
            self.balls2_group.add(ball)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

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
                display.refresh()
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
