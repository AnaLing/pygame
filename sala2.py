from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 30


class Player():

    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [5, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 5, SIZE[Y]//2]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"

    def shoot(self, side):
        ball = Ball(side, self.pos)
        return ball


class Ball():

    def __init__(self, side, pos):
        self.pos = pos
        if side == LEFT_PLAYER:
           self.velocity = 10
        else:
           self.velocity = -10

    def get_pos(self): 
        return self.pos

    def update(self, side):
        if side == LEFT_PLAYER:
           self.pos[X] += self.velocity
        else:
           self.pos[X] -= self.velocity

    def __str__(self):
        return f"B<{self.pos, self.velocity}>"


class Game():

    def __init__(self, manager):
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)] )
        self.score = manager.list( [0,0] )
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()
        self.ballsleft = manager.list([])
        self.ballsright = manager.list([])

    def get_player(self, side):
        return self.players[side]

    def get_ball_left(self):
       return self.ballsleft[self.indexleft.value]

    def get_ball_right(self):
       return self.ballsright[self.indexright.value]

    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0

    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()

    def collide_player(self, side):
        self.lock.acquire()
        if side == LEFT_PLAYER:
            self.score[RIGHT_PLAYER] += 1
        else:
            self.score[LEFT_PLAYER] += 1
        self.running = 0
        self.lock.release()

    def shoot_player(self, side):
        self.lock.acquire()
        if side == LEFT_PLAYER:
            self.ballsleft.append(self.players[side].shoot(side))
        else:
            self.ballsright.append(self.players[side].shoot(side))
        self.lock.release()

    def get_info(self):
        if self.ballsleft == []:
           pos_left_ball = [[None,None]]
        else:
           pos_left_ball = [b.get_pos() for b in self.ballsleft]
        if self.ballsright == []:
           pos_right_ball = [[None,None]]
        else:
           pos_right_ball = [b.get_pos() for b in self.ballsright]
           
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_left_ball': pos_left_ball,
            'pos_right_ball': pos_right_ball,
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        return info

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.running.value}>"


def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()))
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "collide":
                    game.collide_player(side)
                elif command == "shoot":
                    game.shoot_player(side)
                elif command == "quit":
                    game.stop()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)
    except Exception as e:
        traceback.print_exc()


if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
