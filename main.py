# title: Wolf in Sheep's Clothing
# author: Branden Secaira, Panharith Pov
# desc: 
# site: 
# license: MIT
# version: 1.0

import pyxel
import math

# Game setup
TITLE = "Wolf in Sheep's Clothing"
RESOURCES = "resources.pyxres"
SCRN_CLR = 11
SCRN_W = 256
SCRN_H = 192
FPS = 30

ANMTN_FRQ = 4
SHDW_CLR = 13

# Player
PLYR_SPD = 1.4
PLYR_H = 16
PLYR_W = 16

# Scare and attack range
SCARE_R = 28
SCARE_AOEW = SCARE_R * 2
SCARE_AOEH = SCARE_AOEW

ATK_R = 12
ATK_AOEW = ATK_R * 2
ATK_AOEH = ATK_AOEW

# Row of tiles, unmasked & masked
PLYR_UNMSKD = 0
PLYR_MSKD = 48

# Player front side
PLYR_FB = 0
PLYR_FIDLE = 144
PLYR_FM = 16

# Player back side
PLYR_BB = 80
PLYR_BIDLE = 176
PLYR_BM = 96

# Player side
PLYR_SB = 32
PLYR_SIDLE = 160
PLYR_SM = 48
PLYR_SM2 = 64

MOVE_TILES = {
    "U": [(PLYR_BM, 1), (PLYR_BM, -1)],
    "D": [(PLYR_FM, 1), (PLYR_FM, -1)],
    "L": [(PLYR_SM, -1), (PLYR_SM2, -1)],
    "R": [(PLYR_SM, 1), (PLYR_SM2, 1)]
}

IDLE_TILES = {
    "U": [(PLYR_BB, 1), (PLYR_BIDLE, 1)],
    "D": [(PLYR_FB, 1), (PLYR_FIDLE, 1)],
    "L": [(PLYR_SB, -1), (PLYR_SIDLE, -1)],
    "R": [(PLYR_SB, 1), (PLYR_SIDLE, 1)]
}

PLYR_ATK = 112
PLYR_ATK2 = 128
PLYR_ATK_DUR = 20
PLYR_ATK2_DUR = 30 # total attack duration

INDICATOR_DUR = 30

# Sheep
SHP_SPD = 0.5
SHP_H = 16
SHP_W = 16

SHP_PANIC_DUR = 30 * 2
SHP_DYING_DUR = 30 * 1

# Row of tiles, calm and panicked
SHP_C = 16
SHP_P = 64

SHP_B = 0
SHP_IDLE = 48
SHP_M = 16
SHP_M2 = 32
SHP_DYING_ALERT = 64

# Farmer
FRMR_SPD = 0.5
FRMR_H = 16
FRMR_W = 16

CHASE_R = 32
CHASE_AOEW = CHASE_R * 2
CHASE_AOEH = CHASE_AOEW

FRMR_TILE_ROW = 32
FRMR_B = 0
FRMR_IDLE = 16
FRMR_M = 32
FRMR_M2 = 48

FRMR_CHASE_DUR = 30 * 1

# Initial values
INIT_X = 20
INIT_Y = 20
INIT_DIR = 1

sheeps = []

def near(first, second, radius):
    f_x, f_y = first
    s_x, s_y = second
    dist_x = abs(f_x - s_x)
    dist_y = abs(f_y - s_y)
    dist = math.sqrt(pow(dist_x, 2) + pow(dist_y, 2))

    return dist < radius

class Farmer:
    def __init__(self, x, y, dir = INIT_DIR):
        self.x = x
        self.y = y
        self.dir = dir
        self.speed = FRMR_SPD

        self.alive = True
        self.chase = False
        self.chase_timer = 0

        self.tile_row = FRMR_TILE_ROW
        self.tile_col = 0
        self.animate_timer = 0
        
        # wait, roam, chase
        self.activity = "wait"
        self.to_wait = 0
        self.dest = None

        self.update_wait_time()

    def update_wait_time(self):
        # wait between 10 and 20 seconds
        new_wait_time = pyxel.rndi(30 * 5, 30 * 10)
        self.to_wait = new_wait_time

    def update_roam_point(self):
        rdm_x = pyxel.rndi(0, pyxel.width - SHP_W)
        rdm_y = pyxel.rndi(0, pyxel.height - SHP_H)
        self.dest = (rdm_x, rdm_y)

    def roam(self):
        if self.dest == None:
            self.update_roam_point()
        elif (self.x, self.y) != self.dest:
            if self.x > self.dest[0]:
                self.x -= self.speed
                self.dir = -1
            elif self.x < self.dest[0]:
                self.x += self.speed
                self.dir = 1
            if self.y > self.dest[1]:
                self.y -= self.speed
            elif self.y < self.dest[1]:
                self.y += self.speed
        else:
            self.activity = "wait"
            self.update_wait_time()

    def update(self):
        if self.activity == "wait":
            if self.to_wait == 0:
                self.activity = "roam"
                self.update_roam_point()
            else:
                self.to_wait -= 1
        elif self.activity == "roam":
            self.roam()
            
        if self.chase == True:
            self.speed = FRMR_SPD * 2

            if near((self.x, self.y), self.dest, 1):
                if self.chase_timer == FRMR_CHASE_DUR:
                    self.chase = False
                    self.chase_timer = 0
                    self.update_roam_point()
                else:
                    self.chase_timer += 1
        else:
            self.speed = FRMR_SPD
        
        self.animate()

    def animate(self):
        if self.animate_timer == ANMTN_FRQ:
            if self.activity == "roam":
                if self.tile_col == FRMR_M:
                    self.tile_col = FRMR_M2
                else:
                    self.tile_col = FRMR_M
            else:
                if self.tile_col == FRMR_B:
                    self.tile_col = FRMR_IDLE
                else:
                    self.tile_col = FRMR_B
            self.animate_timer = 0
        else:
            self.animate_timer += 1

    def draw(self):
        # pyxel.ellib(self.x - (CHASE_AOEW / 2) + (FRMR_W / 2),
        #             self.y - (CHASE_AOEH / 2) + (FRMR_H / 2),
        #             CHASE_AOEW, CHASE_AOEH, 2)
        
        pyxel.elli(self.x + 1, self.y + 15, 14, 3, SHDW_CLR)
        pyxel.blt(self.x, self.y, 0, self.tile_col, self.tile_row, FRMR_W * self.dir, FRMR_W, 0)

class Sheep:
    def __init__(self, x, y, dir = INIT_DIR):
        self.x = x
        self.y = y
        self.dir = dir
        self.speed = SHP_SPD

        self.alive = True
        self.state = "calm"

        self.tile_row = SHP_C
        self.tile_col = 0
        self.animate_timer = 0
        
        # wait, roam, dying
        self.activity = "wait"
        self.dying_timer = 0
        self.panic_timer = 0
        self.to_wait = 0
        self.dest = None

        self.update_wait_time()
        sheeps.append(self)

    def update_wait_time(self):
        # wait between 10 and 20 seconds
        new_wait_time = pyxel.rndi(30 * 3, 30 * 7)
        self.to_wait = new_wait_time

    def update_roam_point(self):
        rdm_x = pyxel.rndi(0, pyxel.width - SHP_W)
        rdm_y = pyxel.rndi(0, pyxel.height - SHP_H)
        self.dest = (rdm_x, rdm_y)

    def roam(self):
        if self.dest == None:
            self.update_roam_point()
        elif (self.x, self.y) != self.dest:
            if self.x > self.dest[0]:
                self.x -= self.speed
                self.dir = 1
            elif self.x < self.dest[0]:
                self.x += self.speed
                self.dir = -1
            if self.y > self.dest[1]:
                self.y -= self.speed
            elif self.y < self.dest[1]:
                self.y += self.speed
        else:
            self.activity = "wait"
            self.update_wait_time()

    def update(self):
        if not self.alive:
            sheeps.remove(self)

        if self.activity == "dying":
            if self.dying_timer == SHP_DYING_DUR:
                self.alive = False
            else:
                self.dying_timer += 1
        elif self.activity == "wait":
            if self.to_wait == 0:
                self.activity = "roam"
                self.update_roam_point()
            else:
                self.to_wait -= 1
        elif self.activity == "roam":
            self.roam()
            
        if self.state == "panic":
            self.speed = SHP_SPD * 2
            self.tile_row = SHP_P

            if near((self.x, self.y), self.dest, 1):
                if self.panic_timer == SHP_PANIC_DUR:
                    self.state = "calm"
                    self.panic_timer = 0
                else:
                    self.panic_timer += 1
        else:
            self.speed = SHP_SPD
            self.tile_row = SHP_C

        if self.animate_timer == ANMTN_FRQ:
            if self.activity == "dying":
                self.tile_col = SHP_DYING_ALERT
            elif self.activity == "roam":
                if self.tile_col == SHP_M:
                    self.tile_col = SHP_M2
                else:
                    self.tile_col = SHP_M
            else:
                if self.tile_col == SHP_B:
                    self.tile_col = SHP_IDLE
                else:
                    self.tile_col = SHP_B
            self.animate_timer = 0
        else:
            self.animate_timer += 1

    def draw(self):
        pyxel.elli(self.x + 1, self.y + 15, 14, 3, SHDW_CLR)
        pyxel.blt(self.x, self.y, 0, self.tile_col, self.tile_row, SHP_W * self.dir, SHP_H, 0)
        
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = "D"
        
        self.alive = True
        self.masked = True
        self.moving = False
        self.can_attack = False
        self.attacking = False
        self.attack_counter = 0

        self.tile_row = PLYR_MSKD
        self.tile_col = IDLE_TILES[self.dir][0]
        self.animate_timer = 0
        self.animator = 0
        self.indicator_timer = 0

    def controls(self):
        if not self.attacking:
            if pyxel.btn(pyxel.KEY_UP) and self.y > 0:
                self.y -= PLYR_SPD
                self.dir = "U"
            if pyxel.btn(pyxel.KEY_DOWN) and self.y < pyxel.height - PLYR_H:
                self.y += PLYR_SPD
                self.dir = "D"
            if pyxel.btn(pyxel.KEY_LEFT) and self.x > 0:
                self.x -= PLYR_SPD
                self.dir = "L"
            if pyxel.btn(pyxel.KEY_RIGHT) and self.x < pyxel.width - PLYR_W:
                self.x += PLYR_SPD
                self.dir = "R"

            if (pyxel.btn(pyxel.KEY_UP) or
                pyxel.btn(pyxel.KEY_DOWN) or
                pyxel.btn(pyxel.KEY_LEFT) or
                pyxel.btn(pyxel.KEY_RIGHT)):
                self.moving = True
            else:
                self.moving = False

            if pyxel.btnp(pyxel.KEY_X):
                if self.masked:
                    self.masked = False
                else:
                    self.masked = True
            
            if pyxel.btnp(pyxel.KEY_Z):
                if not self.masked:
                    self.attacking = True

    def update(self):
        self.controls()

        if self.masked:
            self.tile_row = PLYR_MSKD
        else:
            self.tile_row = PLYR_UNMSKD

        if self.attacking:
            if self.attack_counter == PLYR_ATK2_DUR:
                self.attacking = False
                self.attack_counter = 0
            else:
                self.attack_counter += 1

        if self.animate_timer == ANMTN_FRQ:
            if self.animator == 1:
                self.animator = 0
            else:
                self.animator = 1

            if self.attacking:
                if self.attack_counter < PLYR_ATK_DUR:
                    self.tile_col = (PLYR_ATK, 1)
                else:
                    self.tile_col = (PLYR_ATK2, 1)
            elif self.moving:
                self.tile_col = MOVE_TILES[self.dir][self.animator]
            else:
                self.tile_col = IDLE_TILES[self.dir][self.animator]
            self.animate_timer = 0
        else:
            self.animate_timer += 1

        if self.indicator_timer == INDICATOR_DUR:
            self.indicator_timer = 0
        else:
            self.indicator_timer += 1

    def draw(self):
        if not self.masked and self.indicator_timer < (INDICATOR_DUR / 2):
            pyxel.ellib(self.x - (SCARE_AOEW / 2) + (PLYR_W / 2),
                        self.y - (SCARE_AOEH / 2) + (PLYR_H / 2),
                        SCARE_AOEW, SCARE_AOEH, 2)
            
        if self.can_attack:
            pyxel.ellib(self.x - (ATK_AOEW / 2) + (PLYR_W / 2),
                        self.y - (ATK_AOEH / 2) + (PLYR_H / 2),
                        ATK_AOEW, ATK_AOEH, 8)

        pyxel.elli(self.x + 1, self.y + 15, 14, 3, SHDW_CLR)
        pyxel.blt(self.x, self.y, 0, self.tile_col[0], self.tile_row, PLYR_W * self.tile_col[1], PLYR_H, 0)

class Game:
    def __init__(self):
        pyxel.init(SCRN_W, SCRN_H, title=TITLE, fps=FPS)
        pyxel.load(RESOURCES)

        self.game_over = True
        self.player = Player(INIT_X, INIT_Y)
        self.farmer = Farmer(pyxel.rndi(0, pyxel.width - SHP_W), pyxel.rndi(0, pyxel.height - SHP_H))
        # self.sheep = Sheep(pyxel.rndi(0, pyxel.width - SHP_W), pyxel.rndi(0, pyxel.height - SHP_H))
        self.spawn_sheep(5)

        pyxel.run(self.update, self.draw)

    def spawn_sheep(self, num):
        for x in range(num):
            Sheep(pyxel.rndi(0, pyxel.width - SHP_W), pyxel.rndi(0, pyxel.height - SHP_H))

    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.game_over = False

        self.player.update()
        self.farmer.update()

        if near((self.player.x, self.player.y), (self.farmer.x, self.farmer.y), 4) and not self.player.masked:
            self.game_over = True

        if (near((self.player.x, self.player.y), (self.farmer.x, self.farmer.y), CHASE_R)
            and not self.player.masked):
            self.farmer.chase = True
            self.farmer.activity = "roam"
            self.farmer.dest = self.player.x, self.player.y
        else:
            pass

        for sheep in sheeps:
            if near((self.player.x, self.player.y), (sheep.x, sheep.y), ATK_R):
                self.player.can_attack = True

                if self.player.attacking and self.player.attack_counter > PLYR_ATK_DUR:
                    sheep.state = "calm"
                    sheep.activity = "dying"
            elif near((self.player.x, self.player.y), (sheep.x, sheep.y), SCARE_R) and not self.player.masked:
                if ((sheep.state == "calm" or sheep.state == "panic" and (sheep.x, sheep.y) == sheep.dest)
                and sheep.activity != "dying"):
                    sheep.state = "panic"
                    sheep.tile_col = SHP_DYING_ALERT
                    sheep.activity = "roam"
                    sheep.update_roam_point()
                    sheep.roam()
            else:
                self.player.can_attack = False

            sheep.update()

    def draw(self):
        if not self.game_over:
            pyxel.cls(SCRN_CLR)
            pyxel.blt(0, 0, 1, 0, 0, SCRN_W, SCRN_H)
            
            self.player.draw()
            self.farmer.draw()
            for sheep in sheeps:
                sheep.draw()
        else:
            pyxel.blt(0, 0, 2, 0, 0, SCRN_W, SCRN_H)

Game()