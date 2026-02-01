import pygame
import sys

# -------------------- INIT --------------------
pygame.init()
pygame.mixer.init()

# -------------------- WINDOW --------------------
SCREEN_W, SCREEN_H = 400, 200
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Sound Tester")

# -------------------- COLORS --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -------------------- FONT --------------------
font = pygame.font.Font(None, 32)

# -------------------- VARIABLES --------------------
sound_file = "gunshot12.wav"  # ضع هنا اسم ملف الصوت، مثلا "laser.wav"
sound = None

# -------------------- DRAW TEXT --------------------
def draw_text(text, pos):
    label = font.render(text, True, BLACK)
    screen.blit(label, pos)

# -------------------- MAIN LOOP --------------------
while True:
    screen.fill(WHITE)

    draw_text("Press SPACE to play sound", (50, 50))
    draw_text(f"Current sound: {sound_file if sound_file else 'None'}", (50, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if sound_file:
                    try:
                        sound = pygame.mixer.Sound(sound_file)
                        sound.play()
                    except Exception as e:
                        print("Error loading sound:", e)

    pygame.display.update()
