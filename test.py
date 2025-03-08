import pygame
import math

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load an image (placeholder rectangle)
player_img = pygame.Surface((50, 50), pygame.SRCALPHA)
player_img.fill("green")
# pygame.draw.rect(player_img, (0, 255, 0), (0))  # A simple triangle shape

# Player properties
player_x, player_y = WIDTH // 2, HEIGHT // 2
base_y = player_y  # Store the base Y position
time_elapsed = 0  # Track time for animation
moving = False  # Check if moving

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get keys
    keys = pygame.key.get_pressed()
    # moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]  # Moving when pressing keys
    moving = True
    if keys[pygame.K_LEFT]:
        player_x -= 3
    if keys[pygame.K_RIGHT]:
        player_x += 3

    # If moving, apply the animation
    if moving:
        time_elapsed += 0.01  # Adjusts animation speed
        bob_offset = math.sin(time_elapsed * 6) * 15  # Up/down movement
        tilt_angle = math.sin(time_elapsed * 6) * 15  # Tilting effect

        # Squash & Stretch Logic
        stretch_factor = 1 + math.sin(time_elapsed * 6) * 0.25  # Scale between 0.85 and 1.15
        if stretch_factor < 1:  # Squash when moving downward
            width_scale = 1 + (1 - stretch_factor) * 0.5
        else:  # Stretch when moving upward
            width_scale = 1 - (stretch_factor - 1) * 0.5

    else:
        time_elapsed = 0  # Reset when stopping
        bob_offset = 0
        tilt_angle = 0
        stretch_factor = 1
        width_scale = 1

    player_y = base_y + bob_offset  # Apply vertical movement

    # Scale image for squash/stretch effect
    scaled_image = pygame.transform.smoothscale(player_img, (int(50 * width_scale), int(50 * stretch_factor)))

    # Rotate the scaled image
    rotated_image = pygame.transform.rotate(scaled_image, tilt_angle)
    new_rect = rotated_image.get_rect(midbottom=(player_x + 25, player_y + 50))

    # Draw the rotated sprite
    screen.blit(rotated_image, new_rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()