import pygame
import os

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("")
input_icon = pygame.image.load("images\начальный.png")
pygame.display.set_icon(input_icon)
bg = pygame.image.load("images/начальный.png")
kno = pygame.image.load("images/Банка жигулевского.png")

# Музыка (закомментировано)
# pygame.mixer.music.load("Muzika\топчик.mp3")
# pygame.mixer.music.play(-1)
flPause = False
f = True
vol = 0.1
x = 0

while f:
    screen.blit(bg, (0, 0))
    H = 405 + x
    screen.blit(kno, (290, H))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            f = False
            pygame.quit()

        if event.type == pygame.KEYDOWN:
            # Управление музыкой (закомментировано)
            # if event.key == pygame.K_f:
            #     flPause = not flPause
            #     if flPause:
            #         pygame.mixer.music.pause()
            #     else:
            #         pygame.mixer.music.unpause()

            # if event.key == pygame.K_o:
            #     vol -= 0.01
            #     pygame.mixer.music.set_volume(vol)
            #     print(pygame.mixer.music.get_volume())

            # if event.key == pygame.K_p:
            #     vol += 0.01
            #     pygame.mixer.music.set_volume(vol)
            #     print(pygame.mixer.music.get_volume())

            if event.key == pygame.K_DOWN:
                x += 115
                if x > 230:
                    x = 0

            if event.key == pygame.K_UP:
                x -= 115
                if x < 0:
                    x = 230

            elif event.key == pygame.K_SPACE and x == 0:
                f = False
                pygame.quit()
                os.system('python game.py')

            elif event.key == pygame.K_SPACE and x == 230:
                os.system('taskkill /f /im python.exe')
