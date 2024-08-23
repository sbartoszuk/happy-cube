import pygame
from random import randint
import os

screen_heigth = 800
screen_width = 800
ground_heigth = 150
new_block_time = 1200
game_title = 'Happy Cube'
ground_level = screen_heigth - ground_heigth

#config files
if os.path.exists('highscore.dat'):
    with open('highscore.dat', 'r') as file:
        highscore = file.read().strip()
else:
    highscore = '0'
    with open('highscore.dat', 'w', encoding='utf-8') as file:
        file.write('0')


score_counter_int = 0
pause = False

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((screen_width, screen_heigth), pygame.NOFRAME)
clock = pygame.time.Clock()
pygame.display.set_caption(game_title)

font1 = pygame.font.Font(None, 30)
font2 = pygame.font.Font('font/Minecraft.ttf', 90)
font3 = pygame.font.Font('font/Origicide.ttf', 15)
font4 = pygame.font.Font('font/Minecraft.ttf', 30)

player_character = pygame.image.load('graphics/player.png').convert()
player_character = pygame.transform.scale(player_character, (70, 70))
player_rect = player_character.get_rect(midbottom = (screen_width//2, ground_level))

filter_surf = pygame.image.load('graphics/filter.png').convert_alpha()
filter_rect = filter_surf.get_rect(bottomleft=(0, screen_heigth))

black_surf = pygame.Surface((screen_width, screen_heigth), pygame.SRCALPHA)
black_surf.fill('Black')

ground_surface = pygame.Surface((screen_width, ground_heigth))
ground_surface.fill((255,0,230))
ground_rect = ground_surface.get_rect(topleft=(0,ground_level))

obstacles_surface = pygame.Surface((25, 25))
obstacles_surface.fill(('Black'))
obstacles_rect = []

death_sound = pygame.mixer.Sound('sounds/death.mp3')
soundtrack = pygame.mixer.Sound('sounds/soundtrack.mp3')
soundtrack.play(loops=-1)

for i in range(5):
    obstacles_rect.append(obstacles_surface.get_rect(center=(randint(10, screen_width-9), -13)))

score_surf = font2.render('0', True, 'White')
score_rect = score_surf.get_rect(center=(screen_width//2, 120))

highscore_surf = font4.render('highscore: ' + highscore, False, 'White')
highscore_rect = highscore_surf.get_rect(topright=(screen_width - 15,15))

manual_surf = font3.render('move: arrows    restart: "r"    pause: "p"  exit: "e"', True, 'White')
manual_rect = manual_surf.get_rect(midbottom=(screen_width//2, screen_heigth - 20))



class Velocity:
    __move_constant = 15
    __jump_constant = 32
    __jump_heigth = 5
    __gravity = 25

    def __init__(self, object):
        self.jump_counter = 0
        self.object = object

    def update(self):
        global pause
        if pause == False:
            if  0 < self.jump_counter:
                self.jump_counter -= 1
                self.object.bottom -= self.__jump_constant
            elif self.object.bottom <= ground_level - self.__gravity:
                self.object.bottom += self.__gravity
            elif self.object.bottom < ground_level:
                self.object.bottom = ground_level

    def moveRight(self):
        if self.object.right < screen_width:
            self.object.right += self.__move_constant
    def moveLeft(self):
        if self.object.left > 0:
            self.object.left -= self.__move_constant
    def jump(self):
        self.jump_counter = self.__jump_heigth


class ObstacleVel():
    __gravity = 5
    __roll_velocity = 8
    __left = True
    def __init__(self, object):
        self.object = object
    def generateObstacle(self):
        self.object.center = (randint(10, screen_width-9), -13)
    def update(self):
        global score_counter_int
        global pause
        if pause == False:
            if self.object.bottom <= ground_level - self.__gravity:
                self.object.bottom += self.__gravity
            elif self.object.bottom < ground_level:
                self.object.bottom = ground_level
            elif self.object.bottom == ground_level:
                if self.__left:
                    self.object.right -= self.__roll_velocity
                else:
                    self.object.right += self.__roll_velocity
            if self.object.right <= 0 or self.object.left >= screen_width:
                self.generateObstacle()
                score_counter_int += 1
                self.__left = not self.__left

player_velocity = Velocity(player_rect)

obstacles_velocity = list(map(lambda x: ObstacleVel(x), obstacles_rect))

def highscore_update():
    global highscore
    with open('highscore.dat', 'r') as file:
        highscore_dat = int(file.read().strip())
    if highscore_dat < score_counter_int:
        highscore = str(score_counter_int)
        with open('highscore.dat', 'w') as file:
            file.write(str(score_counter_int))
def restart():
    global score_counter_int, obstacles_velocity, obstacles_rect
    black_surf.set_alpha(255)
    obstacles_rect = []
    score_counter_int = 0
    player_velocity.object.midbottom = (screen_width//2, ground_level)
    for i in range(5):
        obstacles_rect.append(obstacles_surface.get_rect(center=(randint(10, screen_width-9), -13)))
    obstacles_velocity = list(map(lambda x: ObstacleVel(x), obstacles_rect))
    mainLoop()

def mainLoop():
    global pause

    new_block_counter = 1          

    while True:
        score_surf = font2.render(str(score_counter_int), False, 'White')
        highscore_surf = font4.render('highscore: ' + highscore, False, 'White')
        score_rect = score_surf.get_rect(center=(screen_width//2, 120))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart()
                if event.key == pygame.K_p:
                    pause = not pause
                    if pause:
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
                if event.key == pygame.K_e:
                    exit()

        screen.fill((255,100,180))
        screen.blit(player_character, player_rect)
        screen.blit(ground_surface, ground_rect)
        screen.blit(score_surf, score_rect)
        screen.blit(highscore_surf, highscore_rect)
        screen.blit(manual_surf, manual_rect)
        screen.blit(black_surf, (0,0))

        for i in range(5):
            if new_block_counter > new_block_time * i:
                screen.blit(obstacles_surface, obstacles_rect[i])
            else:
                break

        if filter_rect.top >= 0:
            filter_rect.bottom = screen_heigth
        else:
            filter_rect.top += 5

        screen.blit(filter_surf, filter_rect)

        black_opacity = black_surf.get_alpha() - 5
        if black_opacity < 0:
            black_opacity = 0
        black_surf.set_alpha(black_opacity)

        if black_opacity == 0 and pause == False:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                player_velocity.moveRight()
            if keys[pygame.K_LEFT]:
                player_velocity.moveLeft()
            if keys[pygame.K_UP] and player_rect.bottom == ground_level:
                player_velocity.jump()
        
        for elem in obstacles_rect:
            if player_rect.colliderect(elem):
                death_sound.play()
                highscore_update()
                restart()
                break
        
        for i in range(5):
            if new_block_counter > new_block_time * i:
                obstacles_velocity[i].update()

        player_velocity.update()
        if pause == False:
            if new_block_counter < 5*new_block_time + 1:
                new_block_counter += 1
            pygame.display.update()
        else:
            pygame.display.update(filter_rect)
        clock.tick(60)

mainLoop()