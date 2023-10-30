import pygame
import random
import sqlite3


pygame.init()

WIDTH = 640
HEIGHT = 480


BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Player:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.direction = "right"
        self.score = 0
        self.name = name

    def move(self):
        if self.direction == "up":
            self.y -= 20
        elif self.direction == "down":
            self.y += 20
        elif self.direction == "left":
            self.x -= 20
        elif self.direction == "right":
            self.x += 20

    def change_direction(self, direction):
        if direction in ["up", "down", "left", "right"]:
            if (direction == "up" and self.direction != "down" or
                direction == "down" and self.direction != "up" or
                direction == "left" and self.direction != "right" or
                direction == "right" and self.direction != "left"):
                self.direction = direction

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, self.y, 20, 20))


class Food:
    def __init__(self):
        self.x = random.randrange(1, WIDTH // 20) * 20
        self.y = random.randrange(1, HEIGHT // 20) * 20

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, 20, 20))


class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.player = None
        self.food = None
        self.running = True
        self.database = Database()

    def get_name(self):
        running = True
        name = ""
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

            self.window.fill(BLACK)
            font = pygame.font.Font(None, 36)
            text = font.render("Enter your name: " + name, True, GREEN)
            self.window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()

        return name

    def game_over(self):
        self.running = False
        self.database.insert_score(self.player.name, self.player.score)
        top_players = self.database.get_top_scores()

        self.window.fill(BLACK)
        font = pygame.font.Font(None, 36)
        text = font.render("Game Over", True, GREEN)
        self.window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 30))

        if self.player.score == 4:
            victory_text = font.render("Победа!", True, GREEN)
            self.window.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - victory_text.get_height() // 2 + 30))

        top_players_text = font.render("Top Players:", True, GREEN)
        self.window.blit(top_players_text, (WIDTH // 2 - top_players_text.get_width() // 2, HEIGHT // 2 - top_players_text.get_height() // 2 + 60))

        y_pos = HEIGHT // 2 - top_players_text.get_height() // 2 + 90
        for i, player in enumerate(top_players):
            player_text = font.render(f"{i+1}. {player[0]} - {player[1]}", True, GREEN)
            self.window.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, y_pos))
            y_pos += 30

        pygame.display.update()
        pygame.time.wait(5000)

    def run(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2, self.get_name())
        self.food = Food()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player.change_direction("up")
                    elif event.key == pygame.K_DOWN:
                        self.player.change_direction("down")
                    elif event.key == pygame.K_LEFT:
                        self.player.change_direction("left")
                    elif event.key == pygame.K_RIGHT:
                        self.player.change_direction("right")

            self.player.move()

            if self.player.x == self.food.x and self.player.y == self.food.y:
                self.player.score += 1
                self.food = Food()

            if self.player.x < 0 or self.player.x >= WIDTH or self.player.y < 0 or self.player.y >= HEIGHT:
                self.game_over()

            self.window.fill(BLACK)
            self.player.draw(self.window)
            self.food.draw(self.window)
            pygame.display.update()

            self.clock.tick(10)

        pygame.quit()


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("scores.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS scores (name TEXT, score INTEGER)")

    def insert_score(self, name, score):
        self.cursor.execute("INSERT INTO scores VALUES (?, ?)", (name, score))
        self.connection.commit()

    def get_top_scores(self):
        self.cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 5")
        return self.cursor.fetchall()


if __name__ == "__main__":
    game = Game()
    game.run()
    