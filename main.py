import pygame
import os
from os import path
import time
import random
pygame.font.init()
pygame.mixer.init()

HS = "highscore.txt"

# set the display
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Last Hope")

# load images
SHIP = pygame.image.load(os.path.join("assets", "ship.png"))
ASTEROID = pygame.image.load(os.path.join("assets", "asteroid.png"))
SHOOT = pygame.image.load(os.path.join("assets", "shoot.png"))
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "background.png")), (WIDTH, HEIGHT))

# load sounds
fire_sound = pygame.mixer.Sound("assets/fire.wav")
hit_sound = pygame.mixer.Sound("assets/get_hit.wav")
start = pygame.mixer.Sound("assets/game_start.wav")
death = pygame.mixer.Sound("assets/death.wav")
exp = pygame.mixer.Sound("assets/explosion.wav")

# this class define all the shoot methods and attributes


class Shoot:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not self.y <= height and self.y >= 0

    def collision(self, obj):
        return collide(obj, self)

# class for all the interactive objects in the game (player ship, asteroids)


class interactive:

    COOLDOWN = 30

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = None
        self.shoot_img = None
        self.cooldown = 0
        self.shoots = []

    def Cooldown(self):
        if self.cooldown >= self.COOLDOWN:
            self.cooldown = 0
        elif self.cooldown > 0:
            self.cooldown += 1

    def shooter(self):
        if self.cooldown == 0:
            shoot = Shoot(self.x, self.y, self.shoot_img)
            pygame.mixer.Sound.play(fire_sound)
            self.shoots.append(shoot)
            self.cooldown = 1

    def get_height(self):
        return self.img.get_height()

    def get_width(self):
        return self.img.get_width()

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        for shoot in self.shoots:
            shoot.draw(window)

# class for the player ship


class Player(interactive):
    global score

    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = SHIP
        self.shoot_img = SHOOT
        self.mask = pygame.mask.from_surface(self.img)

    def move_shoots(self, vel, objs):
        global score
        self.Cooldown()
        for shoot in self.shoots:
            shoot.move(vel)
            if shoot.off_screen(HEIGHT):
                self.shoots.remove(shoot)
            else:
                for obj in objs:
                    if shoot.collision(obj):
                        objs.remove(obj)
                        score += 5
                        pygame.mixer.Sound.play(exp)
                        if shoot in self.shoots:
                            self.shoots.remove(shoot)

# class for the asteroids


class Asteroid(interactive):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = ASTEROID
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# main function of the game


def main():
    global score
    score = 0
    run = True
    FPS = 60
    lives = 3
    level = 0
    main_font = pygame.font.Font("assets/prstart.TTF", 20)
    lost_font = pygame.font.Font("assets/prstart.TTF", 50)
    hs_font = pygame.font.Font("assets/prstart.TTF", 30)
    player = Player(275, 500)
    player_vel = 6
    laser_vel = 10
    asteroids = []
    wave_lenght = 5
    ast_vel = 1.0
    lost = False
    lost_count = 0

    clock = pygame.time.Clock()
    pygame.mixer.music.load("assets/Condamned.mp3")
    pygame.mixer.music.play(-1)

    def redraw_window():
        # draw text
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"LIVES:{lives}", 1, (255, 255, 255))
        score_label = main_font.render(f"SCORE:{score}", 1, (255, 255, 255))
        level_label = main_font.render(f"LEVEL:{level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - 10, 10))
        WIN.blit(level_label, (WIDTH/2 - level_label.get_width()/2 - 10, 570))

        for asteroid in asteroids:
            asteroid.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 -
                     lost_label.get_width()/2, HEIGHT/2 - 100))
            pygame.mixer.music.stop()
            pygame.mixer.Sound.stop(hit_sound)
            pygame.mixer.Sound.play(death)

            dir = path.dirname(__file__)
            with open(path.join(dir, HS), "r") as f:
                try:
                    high_score = int(f.read())
                except:
                    high_score = 0
                if score > high_score:
                    hs_label = hs_font.render(
                        "NEW HIGHSCORE", 1, (255, 255, 255))
                    WIN.blit(
                        hs_label, (WIDTH/2 - lost_label.get_width()/2 + 30, HEIGHT/2 - 25))
                    with open(path.join(dir, HS), "w") as f:
                        f.writelines(str(score))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        redraw_window()
        if lives <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(asteroids) == 0 and level >= 1:
            score += (5 * lives) * level

        if len(asteroids) == 0:
            level += 1
            wave_lenght += 3
            ast_vel += 0.25
            for i in range(wave_lenght):
                asteroid = Asteroid(random.randrange(
                    50, WIDTH - 100, 70), random.randrange(-1400, -100, 70))

                asteroids.append(asteroid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # movment
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player.y + player_vel - 6 > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_a] and player.x + player_vel - 6 > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shooter()

        for asteroid in asteroids[:]:
            asteroid.move(ast_vel)
            if asteroid.y + asteroid.get_height() > HEIGHT + 60:
                asteroids.remove(asteroid)
            if collide(asteroid, player):
                pygame.mixer.Sound.play(hit_sound)
                lives -= 1
                asteroids.remove(asteroid)

        player.move_shoots(-laser_vel, asteroids)

# main menu function


def main_menu():
    menu_font1 = pygame.font.Font("assets/prstart.TTF", 30)
    menu_font2 = pygame.font.Font("assets/prstart.TTF", 20)
    menu_font3 = pygame.font.Font("assets/prstart.TTF", 15)
    run = True
    pygame.mixer.Sound.play(start)
    while run:
        WIN.blit(BG, (0, 0))
        pygame.mixer.music.stop()
        menu_label1 = menu_font1.render("THE LAST HOPE", 1, (255, 255, 255))
        WIN.blit(menu_label1, (WIDTH/2 - menu_label1.get_width()/2, 250))
        menu_label2 = menu_font2.render(
            "Press space to begin", 1, (255, 255, 255))
        WIN.blit(menu_label2, (WIDTH/2 - menu_label1.get_width()/2, 300))
        menu_label3 = menu_font3.render(
            "Press H to go to High Scores", 1, (255, 255, 255))
        WIN.blit(menu_label3, (WIDTH/2 - menu_label3.get_width()/2, 500))
        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if keys[pygame.K_SPACE]:
                main()
            if keys[pygame.K_h]:
                run = False
                scores()

# highscore window function


def scores():
    global high_score
    menu_font4 = pygame.font.Font("assets/prstart.TTF", 20)
    menu_font5 = pygame.font.Font("assets/prstart.TTF", 10)
    menu_font6 = pygame.font.Font("assets/prstart.TTF", 25)
    run = True
    dir = path.dirname(__file__)
    with open(path.join(dir, HS), "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0
    while run:
        WIN.blit(BG, (0, 0))
        menu_label4 = menu_font4.render("HIGH SCORE", 1, (255, 255, 255))
        WIN.blit(menu_label4, (WIDTH/2 - menu_label4.get_width()/2, 50))
        menu_label6 = menu_font6.render(
            f"{str(high_score)}", 1, (255, 255, 255))
        WIN.blit(menu_label6, (WIDTH/2 - menu_label6.get_width()/2, 100))
        # qui ci va l'high score...
        menu_label5 = menu_font5.render(
            "Press esc to return", 1, (255, 255, 255))
        WIN.blit(menu_label5, (WIDTH/2 - menu_label5.get_width()/2, 500))
        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if keys[pygame.K_ESCAPE]:
                run = False
                main_menu()


main_menu()
