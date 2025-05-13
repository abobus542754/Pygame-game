import pygame
import os
import random
import math
import sys

pygame.init()
font = pygame.font.SysFont('arial', 36)
screen = pygame.display.set_mode((1280, 720))
BOSS_LEVEL = 3
PLAYER_MAX_HEALTH = 10

def load_images():
    images = {}
    try:
        images['bg'] = pygame.image.load(os.path.join("Photo", "фон.png"))
    except:
        print("Не удалось загрузить фон")
        images['bg'] = pygame.Surface((1280, 720))
        images['bg'].fill((50, 50, 50))
    images['walr_right'] = [
        pygame.image.load(os.path.join('images', 'player_mid_right', f'{i}.png')) for i in range(1, 9)
    ]
    images['walr_left'] = [
        pygame.image.load(os.path.join('images', 'mid_left', f'{i}.png')) for i in range(1, 9)
    ]
    images['idle'] = pygame.image.load(os.path.join('images', '1.png'))

    enemy_files = ['vodka.png', 'book.png', 'fruit.png', 'dumbbell.png']
    images['enemies'] = [
        pygame.transform.scale(pygame.image.load(f'Photo/{file}'), (64, 64)) for file in enemy_files
    ]
    images['special_enemy'] = pygame.transform.scale(
        pygame.image.load('Photo/special_enemy.png'), (64, 64))
    images['boss'] = pygame.transform.scale(pygame.image.load('Photo/boss.png'), (150, 150))
    images['saw'] = pygame.transform.scale(pygame.image.load('Photo/saw.png'), (80, 80))

    # Оружие
    weapons = {
        "wrench": "weapon.png",
        "hammer": "hammer.png",
        "gun": "gun.png"
    }
    images['weapons'] = {
        name: pygame.transform.scale(pygame.image.load(f"Photo/{file}"), (40, 20))
        for name, file in weapons.items()
    }

    images['heart'] = pygame.transform.scale(
        pygame.image.load("Photo/heart.png"), (40, 40))

    return images

def random_spawn(is_special=False, images=None):
    if images is None:
        images = {}
    if is_special:
        return {
            "x": random.randint(0, 1280),
            "y": -100,
            "dx": 0,
            "dy": random.uniform(2, 4),
            "collided": False,
            "image": images.get('special_enemy'),
            "health": 1,
            "is_special": True
        }

    side = random.choice(["left", "right", "top", "bottom"])
    if side == "left":
        x, y = -100, random.randint(0, 720)
        angle = random.uniform(-45, 45)
    elif side == "right":
        x, y = 1380, random.randint(0, 720)
        angle = random.uniform(135, 225)
    elif side == "top":
        x, y = random.randint(0, 1280), -100
        angle = random.uniform(225, 315)
    else:  # bottom
        x, y = random.randint(0, 1280), 820
        angle = random.uniform(45, 135)

    speed = random.uniform(3, 9)
    dx = math.cos(math.radians(angle)) * speed
    dy = math.sin(math.radians(angle)) * speed

    return {
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
        "collided": False,
        "image": random.choice(images.get('enemies', [])),
        "health": 1,
        "is_special": False
    }

def draw_exp_bar(screen, font, player_exp, max_exp, player_level):
    bar_width = 300
    bar_height = 20
    filled_width = int((player_exp / max_exp) * bar_width)
    bar_x, bar_y = 490, 680

    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
    pygame.draw.rect(screen, (0, 100, 255), (bar_x, bar_y, filled_width, bar_height), border_radius=10)
    level_text = font.render(f"Ур. {player_level}", True, (255, 255, 255))
    screen.blit(level_text, (bar_x + bar_width + 10, bar_y))


def draw_boss_health(screen, font, boss_health, max_boss_health):
    bar_width = 500
    bar_height = 30
    filled_width = int((boss_health / max_boss_health) * bar_width)
    bar_x, bar_y = (1280 - bar_width) // 2, 100
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, filled_width, bar_height), border_radius=5)
    health_text = font.render(f"Босс: {boss_health}/{max_boss_health}", True, (255, 255, 255))
    screen.blit(health_text, (bar_x + bar_width // 2 - health_text.get_width() // 2, bar_y + 30))


def draw_weapon_select(screen, font, weapons_imgs, weapons_stats, ammo, max_ammo, weapon_options, selected_option):
    s = pygame.Surface((1280, 720), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))
    title = font.render("Выберите оружие", True, (255, 255, 255))
    screen.blit(title, (1280 // 2 - title.get_width() // 2 - 100, 150))

    for i, weapon in enumerate(weapon_options):
        img = pygame.transform.scale(weapons_imgs[weapon], (180, 90))
        screen.blit(img, (300 + i * 250, 300))
        stats = weapons_stats[weapon]
        text1 = font.render(f"Урон: {stats['damage']}", True, (255, 255, 255))
        text2 = font.render(f"Скорость: {stats['speed']}", True, (255, 255, 255))
        text3 = font.render(f"Боезапас: {ammo[weapon]}/{max_ammo[weapon]}", True, (255, 255, 255))

        screen.blit(text1, (300 + i * 250 - text1.get_width() // 2 + 90, 410))
        screen.blit(text2, (300 + i * 250 - text2.get_width() // 2 + 90, 450))
        screen.blit(text3, (300 + i * 250 - text3.get_width() // 2 + 90, 490))
        key_text = font.render(f"[{i + 1}]", True, (255, 255, 0))
        screen.blit(key_text, (300 + i * 250 + 70, 530))

def throw_weapon(weapon_cooldown, current_weapon, ammo, weapons_stats, direction, player_x, player_y, weapons_imgs):
    new_wrenches = []
    cooldown = weapon_cooldown

    if cooldown <= 0 and ammo[current_weapon] > 0:
        stats = weapons_stats[current_weapon]
        new_wrenches.append({
            "x": player_x + (50 if direction == "right" else -10),
            "y": player_y + 110,
            "dx": stats["speed"] if direction == "right" else -stats["speed"],
            "dy": -5,
            "angle": 0,
            "rotation_speed": 10,
            "damage": stats["damage"],
            "image": weapons_imgs[current_weapon]
        })
        cooldown = stats["cooldown"]
        ammo[current_weapon] -= 1

    return new_wrenches, cooldown

def main():
    images = load_images()
    clock = pygame.time.Clock()
    player_count = 0
    flPause = False
    running = True
    direction = "right"
    player_x = 620
    player_y = 430
    jump = False
    jump_count = 8
    bg_x = 0
    speed = 3
    player_exp = 0
    max_exp = 10
    player_level = 1
    player_health = PLAYER_MAX_HEALTH
    max_health = PLAYER_MAX_HEALTH

    weapons_stats = {
        "wrench": {"damage": 1, "speed": 10, "cooldown": 15},
        "hammer": {"damage": 3, "speed": 6, "cooldown": 30},
        "gun": {"damage": 1, "speed": 15, "cooldown": 5}
    }

    ammo = {
        "wrench": 10,
        "hammer": 5,
        "gun": 20
    }

    max_ammo = {
        "wrench": 20,
        "hammer": 10,
        "gun": 30
    }

    current_weapon = "wrench"
    weapon_cooldown = 0
    show_weapon_select = False
    weapon_options = ["wrench", "hammer", "gun"]
    selected_option = 0

    # Враги и снаряды
    wrenches = []
    objects = [random_spawn(images=images) for _ in range(6)]
    special_enemy_spawn_timer = 0
    special_enemy_spawn_interval = 100

    # Босс
    boss_active = False
    boss_health = 50
    max_boss_health = 50
    boss_x = 640
    boss_y = 100
    boss_speed = 2
    boss_direction = 1
    boss_move_timer = 0
    boss_move_interval = 60
    boss_attack_cooldown = 0
    boss_attack_interval = 120
    boss_close_attack_timer = 0
    boss_close_attack_interval = 180
    saws = []
    saw_damage_cooldown = 0


    while running:
        clock.tick(25)
        boss_damage_cooldown = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    flPause = not flPause
                elif event.key == pygame.K_l:
                    new_wrenches, weapon_cooldown = throw_weapon(
                        weapon_cooldown, current_weapon, ammo, weapons_stats,
                        direction, player_x, player_y, images['weapons'])
                    wrenches.extend(new_wrenches)
                elif show_weapon_select and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    selected = int(event.unicode) - 1
                    if 0 <= selected < len(weapon_options):
                        current_weapon = weapon_options[selected]
                        show_weapon_select = False
                elif event.key == pygame.K_1 and not show_weapon_select:
                    current_weapon = "wrench"
                elif event.key == pygame.K_2 and not show_weapon_select:
                    current_weapon = "hammer"
                elif event.key == pygame.K_3 and not show_weapon_select:
                    current_weapon = "gun"

        if flPause:
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            direction = "left"
            player_x -= speed
            player_count = (player_count + 1) % len(images['walr_left'])
        elif keys[pygame.K_d]:
            direction = "right"
            player_x += speed
            player_count = (player_count + 1) % len(images['walr_right'])
        else:
            player_count = 0

        if not jump:
            if keys[pygame.K_SPACE]:
                jump = True
        else:
            if jump_count >= -8:
                if jump_count > 0:
                    player_y -= (jump_count ** 2) / 2
                else:
                    player_y += (jump_count ** 2) / 2
                jump_count -= 1
            else:
                jump = False
                jump_count = 8

        player_x = max(0, min(player_x, 1280 - 100))
        player_y = max(0, min(player_y, 720 - 150))

        if keys[pygame.K_a] or keys[pygame.K_d]:
            bg_x -= 1
            if bg_x <= -1280:
                bg_x = 0
        screen.blit(images['bg'], (bg_x, 0))
        screen.blit(images['bg'], (bg_x + 1280, 0))

        if player_level >= BOSS_LEVEL and not boss_active:
            boss_active = True
            objects = []
            wrenches = []
            boss_health = max_boss_health
            boss_x = 640
            boss_y = -200
            saws = []

        if boss_active:
            boss_move_timer += 1
            boss_close_attack_timer += 1

            if boss_y < 100:
                boss_y += 2
            else:

                if boss_move_timer > boss_move_interval:
                    boss_move_timer = 0
                    boss_direction *= -1

                if boss_close_attack_timer > boss_close_attack_interval:
                    boss_close_attack_timer = 0
                    side = random.choice(["left", "right"])
                    if side == "left":
                        boss_x = player_x - 200
                    else:
                        boss_x = player_x + 200
                    boss_y = player_y + 50

                boss_x += boss_speed * boss_direction

                if boss_x < 100 or boss_x > 1280 - 200:
                    boss_direction *= -1
                    boss_x = max(100, min(boss_x, 1280 - 200))

            screen.blit(images['boss'], (boss_x - 100, boss_y))

            if boss_damage_cooldown <= 0:
                boss_rect = pygame.Rect(boss_x - 100, boss_y, 200, 150)
                player_rect = pygame.Rect(player_x + 25, player_y + 110, 40, 90)

                if boss_rect.colliderect(player_rect):
                    player_health -= 0.5
                    boss_damage_cooldown = 60

            if boss_damage_cooldown > 0:
                boss_damage_cooldown -= 1

            boss_attack_cooldown += 1
            if boss_attack_cooldown >= boss_attack_interval:
                saws.append({
                    "x": 0 if random.random() < 0.5 else 1280,
                    "y": random.randint(570, 570),
                    "speed": random.choice([-10, 10]),
                    "image": images['saw']
                })
                boss_attack_cooldown = 0

            if saw_damage_cooldown > 0:
                saw_damage_cooldown -= 1

            for saw in saws[:]:
                saw["x"] += saw["speed"]
                if saw["x"] < -100 or saw["x"] > 1380:
                    saws.remove(saw)
                else:
                    screen.blit(saw["image"], (saw["x"], saw["y"]))
                    saw_rect = pygame.Rect(saw["x"], saw["y"], 80, 40)
                    player_rect = pygame.Rect(player_x, player_y, 100, 150)
                    if saw_rect.colliderect(player_rect) and saw_damage_cooldown == 0:
                        player_health -= 1
                        saw_damage_cooldown = 30

            for wrench in wrenches[:]:
                wrench_rect = pygame.Rect(wrench["x"], wrench["y"], 40, 20)
                boss_rect = pygame.Rect(boss_x - 100, boss_y, 200, 150)
                if wrench_rect.colliderect(boss_rect):
                    boss_health -= wrench["damage"]
                    wrenches.remove(wrench)
                    if boss_health <= 0:
                        boss_active = False
                        player_exp += 20
                        objects = [random_spawn(images=images) for _ in range(8)]

            draw_boss_health(screen, font, boss_health, max_boss_health)
        else:
            special_enemy_spawn_timer += 1
            if special_enemy_spawn_timer >= special_enemy_spawn_interval:
                if random.random() < 0.8:
                    objects.append(random_spawn(is_special=True, images=images))
                special_enemy_spawn_timer = 0

            for obj in objects[:]:
                obj["x"] += obj["dx"]
                obj["y"] += obj["dy"]

                player_rect = pygame.Rect(player_x + 25, player_y + 110, 40, 90)
                obj_rect = pygame.Rect(int(obj["x"]), int(obj["y"]), 64, 64)

                if player_rect.colliderect(obj_rect) and not obj["collided"]:
                    obj["collided"] = True
                    player_health -= 1

                if obj["x"] < -200 or obj["x"] > 1400 or obj["y"] < -200 or obj["y"] > 900:
                    objects.remove(obj)
                    objects.append(random_spawn(images=images))

                screen.blit(obj["image"], (obj["x"], obj["y"]))

        if keys[pygame.K_a]:
            screen.blit(images['walr_left'][player_count], (player_x, player_y))
        elif keys[pygame.K_d]:
            screen.blit(images['walr_right'][player_count], (player_x, player_y))
        else:
            screen.blit(images['idle'], (player_x, player_y))

        if weapon_cooldown > 0:
            weapon_cooldown -= 1

        for wrench in wrenches[:]:
            wrench["x"] += wrench["dx"]
            wrench["y"] += wrench["dy"]
            wrench["dy"] += 0.3
            wrench["angle"] += wrench["rotation_speed"]
            wrench_rect = pygame.Rect(wrench["x"], wrench["y"], 40, 20)
            should_remove = False

            if not boss_active:
                for obj in objects[:]:
                    obj_rect = pygame.Rect(int(obj["x"]), int(obj["y"]), 64, 64)
                    if wrench_rect.colliderect(obj_rect):
                        obj["health"] -= wrench["damage"]

                        if obj["health"] <= 0:
                            if obj.get("is_special", False):
                                for weapon_type in ammo:
                                    ammo[weapon_type] = min(
                                        max_ammo[weapon_type],
                                        ammo[weapon_type] + 3
                                    )
                            objects.remove(obj)
                            player_exp += 1
                            if player_exp >= max_exp:
                                player_level += 1
                                player_exp = 0
                                max_exp = max_exp * 2
                                show_weapon_select = True
                                player_health = min(max_health, player_health + 2)
                            objects.append(random_spawn(images=images))
                        should_remove = True
                        break

            if not should_remove and (wrench["x"] < -50 or wrench["x"] > 1350 or wrench["y"] > 800):
                should_remove = True

            if should_remove and wrench in wrenches:
                wrenches.remove(wrench)
            else:
                rotated_weapon = pygame.transform.rotate(wrench["image"], wrench["angle"])
                screen.blit(rotated_weapon, (wrench["x"], wrench["y"]))

        for i in range(PLAYER_MAX_HEALTH):
            heart_color = (255, 255, 255) if i < player_health else (100, 100, 100)
            heart_img = images['heart'].copy()
            heart_img.fill(heart_color, special_flags=pygame.BLEND_MULT)
            screen.blit(heart_img, (20 + i * (40 + 5), 20))

        weapon_icon = pygame.transform.scale(images['weapons'][current_weapon], (60, 30))
        screen.blit(weapon_icon, (20, 70))
        ammo_text = font.render(f"{ammo[current_weapon]}/{max_ammo[current_weapon]}", True, (255, 255, 255))
        screen.blit(ammo_text, (90, 80))

        draw_exp_bar(screen, font, player_exp, max_exp, player_level)

        if show_weapon_select:
            draw_weapon_select(
                screen, font, images['weapons'], weapons_stats,
                ammo, max_ammo, weapon_options, selected_option
            )

        if player_health <= 0:
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (1280 // 2 - game_over_text.get_width() // 2, 720 // 2 - 50))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()