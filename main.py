import pygame
import random
import sys
import math

# Constants
WIDTH = 800
HEIGHT = 600
FADEOUT_TIME = 2000  # 2 seconds in milliseconds

# Colors
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
COLORS = [(255, 0, 0), (255, 255, 0), (0, 0, 255), (0, 255, 0), (128, 0, 128), (255, 165, 0), (255, 255, 255)]

def initialize_game():
    pygame.init()
    pygame.font.init()  # Initialize font module explicitly
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Happy New Year 2025")
    clock = pygame.time.Clock()
    
    # Load background image
    background = pygame.image.load('bg/bg1.jpg').convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    # Load target icon
    target_icon = pygame.image.load('icons/target.png').convert_alpha()
    
    # Initialize custom fonts
    fonts = {
        'large': pygame.font.Font('fonts/Bedicta Hosta Regular.ttf', 74),
        'medium': pygame.font.Font('fonts/Bedicta Hosta Regular.ttf', 50),
        'small': pygame.font.Font('fonts/Bedicta Hosta Regular.ttf', 36)
    }
    
    return screen, clock, fonts, background, target_icon

def draw_text(screen, text, x, y, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 5)
        self.radius = random.randint(2, 4)
        self.life = random.randint(20, 50)
        self.gravity = 0.1

    def update(self):
        self.life -= 1
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle) + self.gravity
        self.speed *= 0.95  # Slow down over time

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Firework:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.particles = []
        self.exploded = False
        self.x = start_x
        self.y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.angle = math.atan2(end_y - start_y, end_x - start_x)
        self.speed = 10
        self.color = random.choice(COLORS)

    def update(self):
        if not self.exploded:
            distance = math.hypot(self.end_x - self.x, self.end_y - self.y)
            if distance < self.speed:
                self.exploded = True
                self.create_particles()
            else:
                self.x += self.speed * math.cos(self.angle)
                self.y += self.speed * math.sin(self.angle)
        else:
            for particle in self.particles:
                particle.update()

    def create_particles(self):
        for _ in range(50):
            self.particles.append(Particle(self.x, self.y, self.color))

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
        else:
            for particle in self.particles:
                particle.draw(screen)

class Ripple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 50
        self.alpha = 255

    def update(self):
        if self.radius < self.max_radius:
            self.radius += 2
            self.alpha = max(255 - (self.radius / self.max_radius) * 255, 0)

    def draw(self, screen):
        if self.radius < self.max_radius:
            surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, self.alpha), (self.max_radius, self.max_radius), self.radius, 2)
            screen.blit(surface, (self.x - self.max_radius, self.y - self.max_radius))

class FlyingLetter:
    def __init__(self, letter, start_pos, end_pos, font, color):
        self.letter = letter
        self.x, self.y = start_pos
        self.end_x, self.end_y = end_pos
        self.font = font
        self.color = color
        self.speed = 5
        self.reached = False
        self.alpha = 255
        self.fadeout_start_time = None

    def update(self):
        if not self.reached:
            direction_x = self.end_x - self.x
            direction_y = self.end_y - self.y
            distance = math.hypot(direction_x, direction_y)
            if distance < self.speed:
                self.x, self.y = self.end_x, self.end_y
                self.reached = True
                self.fadeout_start_time = pygame.time.get_ticks()
            else:
                self.x += self.speed * direction_x / distance
                self.y += self.speed * direction_y / distance
        elif self.fadeout_start_time:
            elapsed_time = pygame.time.get_ticks() - self.fadeout_start_time
            if elapsed_time < FADEOUT_TIME:
                self.alpha = max(255 - (elapsed_time / FADEOUT_TIME) * 255, 0)
            else:
                self.alpha = 0

    def draw(self, screen):
        text_surface = self.font.render(self.letter, True, self.color)
        text_surface.set_alpha(self.alpha)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

def main():
    try:
        screen, clock, fonts, background, target_icon = initialize_game()
        running = True
        fireworks = []
        ripples = []
        flying_letters_sets = []  # List to manage multiple sets of flying letters
        mouse_x, mouse_y = WIDTH // 2, HEIGHT // 2

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    fireworks.append(Firework(WIDTH // 2, HEIGHT, x, y))
                    ripples.append(Ripple(x, y))
                    message = "From Chandra's family"
                    start_x, start_y = WIDTH // 2, HEIGHT // 2 + 200
                    end_y = HEIGHT // 2 + 100
                    new_flying_letters = []
                    for i, letter in enumerate(message):
                        end_x = WIDTH // 2 - len(message) * 12 + i * 26  # Adjusted spacing between letters
                        new_flying_letters.append(FlyingLetter(letter, (start_x, start_y), (end_x, end_y), fonts['small'], GOLD))
                    flying_letters_sets.append(new_flying_letters)

            screen.blit(background, (0, 0))  # Draw background image

            # Draw text with updated font references
            draw_text(screen, "Happy New Year", WIDTH // 2, HEIGHT // 2 - 50, fonts['large'], GOLD)
            draw_text(screen, "2025", WIDTH // 2, HEIGHT // 2 + 20, fonts['large'], GOLD)

            # Update and draw fireworks
            for firework in fireworks:
                firework.update()
                firework.draw(screen)

            # Update and draw ripples
            for ripple in ripples:
                ripple.update()
                ripple.draw(screen)

            # Display message at the bottom
            draw_text(screen, "Wishing You a Wonderful Year Ahead!", WIDTH // 2, HEIGHT - 50, fonts['small'], GOLD)

            # Update and draw all sets of flying letters
            for flying_letters in flying_letters_sets:
                for letter in flying_letters:
                    letter.update()
                    letter.draw(screen)

            # Remove fully faded out sets of flying letters
            flying_letters_sets = [letters for letters in flying_letters_sets if any(letter.alpha > 0 for letter in letters)]

            # Draw target icon at mouse position
            screen.blit(target_icon, (mouse_x - target_icon.get_width() // 2, mouse_y - target_icon.get_height() // 2))

            pygame.display.flip()
            clock.tick(60)  # 60 FPS

    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    finally:
        pygame.quit()
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
