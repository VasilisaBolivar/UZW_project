import pygame
from environment import GameEnvironment
from agents import PlayerAgent, EnemyAgent

def check_restart(event, button_rect):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        return button_rect.collidepoint(mouse_pos)
    return False

def render_text(screen, text, position, font, color=(255, 255, 255)):
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, position)

def draw_restart_button(screen, font):
    restart_text = font.render("Restart", True, (255, 255, 255))
    button_rect = restart_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    pygame.draw.rect(screen, (0, 0, 255), button_rect.inflate(20, 10))
    screen.blit(restart_text, button_rect.topleft)
    return button_rect

pygame.init()
screen = pygame.display.set_mode((750, 750))
pygame.display.set_caption("Pacman-Like Game")

level = 1
env = GameEnvironment(screen, level)
player = PlayerAgent(env)

clock = pygame.time.Clock()
lives = 3
font = pygame.font.Font(None, 40)
running = True
game_over = False

# Enemies are instantiated with Q-learning in place
enemies = [EnemyAgent(env) for _ in range(3)]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over and check_restart(event, restart_button_rect):
            level = 1
            lives = 3
            env = GameEnvironment(screen, level)
            player = PlayerAgent(env)
            enemies = [EnemyAgent(env) for _ in range(3)]
            game_over = False

    if game_over:
        screen.fill((0, 0, 0))
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2,
                                     screen.get_height() // 2 - game_over_text.get_height() // 2))
        restart_button_rect = draw_restart_button(screen, font)
        pygame.display.flip()
        continue

    # Update player and enemies
    player.update()
    for enemy in enemies:
        enemy.update()

    # Check collisions
    player_rect = pygame.Rect(player.x, player.y, env.grid_size, env.grid_size)
    for enemy in enemies:
        enemy_rect = pygame.Rect(enemy.x, enemy.y, env.grid_size, env.grid_size)
        if player_rect.colliderect(enemy_rect):
            lives -= 1
            if lives <= 0:
                game_over = True
            player.x, player.y = env.start[1] * env.grid_size, env.start[0] * env.grid_size

    # Render the game
    screen.fill((0, 0, 0))
    env.render()
    player.draw()
    for enemy in enemies:
        enemy.draw()

    render_text(screen, f"Lives: {lives}", (screen.get_width() - 120, 20), font)
    render_text(screen, f"Level: {env.level}", (20, 20), font)

    if env.check_finish(player):
        level += 1
        lives = env.lives  # Синхронизируем значение жизней

    pygame.display.flip()
    clock.tick(30)

pygame.quit()


''' добавить функцию убивать противника , и чтобы противники после убийства появлялись
'''