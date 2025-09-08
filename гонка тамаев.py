import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROAD_WIDTH = 400
CAR_WIDTH = 60
CAR_HEIGHT = 100
PERSON_WIDTH = 30
PERSON_HEIGHT = 50
SPEED_INCREMENT = 0.2
MAX_SPEED = 15

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)

# Настройка экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Городское безумие")
clock = pygame.time.Clock()

# Загрузка изображений (заглушки, которые мы нарисуем сами)
def create_car_surface(color):
    surface = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
    # Кузов
    pygame.draw.rect(surface, color, (0, 10, CAR_WIDTH, CAR_HEIGHT - 20))
    # Лобовое стекло
    pygame.draw.rect(surface, (150, 220, 255), (5, 15, CAR_WIDTH - 10, 20))
    # Фары
    pygame.draw.rect(surface, YELLOW, (5, CAR_HEIGHT - 25, 10, 5))
    pygame.draw.rect(surface, YELLOW, (CAR_WIDTH - 15, CAR_HEIGHT - 25, 10, 5))
    # Колёса
    pygame.draw.rect(surface, BLACK, (5, 5, 15, 10))
    pygame.draw.rect(surface, BLACK, (CAR_WIDTH - 20, 5, 15, 10))
    pygame.draw.rect(surface, BLACK, (5, CAR_HEIGHT - 15, 15, 10))
    pygame.draw.rect(surface, BLACK, (CAR_WIDTH - 20, CAR_HEIGHT - 15, 15, 10))
    return surface

def create_person_surface():
    surface = pygame.Surface((PERSON_WIDTH, PERSON_HEIGHT), pygame.SRCALPHA)
    # Голова
    pygame.draw.circle(surface, (255, 200, 150), (PERSON_WIDTH // 2, 10), 8)
    # Тело
    pygame.draw.rect(surface, BLUE, (10, 18, PERSON_WIDTH - 20, 20))
    # Ноги
    pygame.draw.rect(surface, BLACK, (8, 38, 5, 12))
    pygame.draw.rect(surface, BLACK, (PERSON_WIDTH - 13, 38, 5, 12))
    return surface

# Класс машины
class Car:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
        self.y = SCREEN_HEIGHT - CAR_HEIGHT - 20
        self.speed = 5
        self.color = RED
        self.surface = create_car_surface(self.color)
    
    def move(self, direction):
        if direction == "left" and self.x > (SCREEN_WIDTH - ROAD_WIDTH) // 2:
            self.x -= self.speed
        if direction == "right" and self.x < (SCREEN_WIDTH + ROAD_WIDTH) // 2 - CAR_WIDTH:
            self.x += self.speed
    
    def draw(self):
        screen.blit(self.surface, (self.x, self.y))
    
    def increase_speed(self):
        if self.speed < MAX_SPEED:
            self.speed += SPEED_INCREMENT

# Класс человека
class Person:
    def __init__(self):
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        self.x = random.randint(road_left, road_left + ROAD_WIDTH - PERSON_WIDTH)
        self.y = -PERSON_HEIGHT
        self.speed = random.randint(2, 5)
        self.surface = create_person_surface()
        self.hit = False
    
    def update(self):
        self.y += self.speed
    
    def draw(self):
        if not self.hit:
            screen.blit(self.surface, (self.x, self.y))
    
    def check_collision(self, car):
        if (not self.hit and 
            self.x < car.x + CAR_WIDTH and 
            self.x + PERSON_WIDTH > car.x and 
            self.y < car.y + CAR_HEIGHT and 
            self.y + PERSON_HEIGHT > car.y):
            self.hit = True
            return True
        return False

# Класс игры
class Game:
    def __init__(self):
        self.car = Car()
        self.people = []
        self.score = 0
        self.level = 1
        self.target = 10  # Цель для первого уровня
        self.game_over = False
        self.win = False
        self.spawn_timer = 0
        self.road_lines = []
        self.init_road_lines()
    
    def init_road_lines(self):
        # Создаем линии разметки на дороге
        road_center = SCREEN_WIDTH // 2
        line_spacing = 50
        for y in range(-40, SCREEN_HEIGHT + 40, line_spacing):
            self.road_lines.append({"x": road_center - 5, "y": y, "width": 10, "height": 20})
    
    def update_road_lines(self):
        # Обновляем позиции линий разметки
        for line in self.road_lines:
            line["y"] += self.car.speed / 2
            if line["y"] > SCREEN_HEIGHT:
                line["y"] = -40
    
    def draw_road(self):
        # Рисуем дорогу
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        pygame.draw.rect(screen, GRAY, (road_left, 0, ROAD_WIDTH, SCREEN_HEIGHT))
        
        # Рисуем обочину
        pygame.draw.rect(screen, BROWN, (0, 0, road_left, SCREEN_HEIGHT))
        pygame.draw.rect(screen, BROWN, (road_left + ROAD_WIDTH, 0, road_left, SCREEN_HEIGHT))
        
        # Рисуем линии разметки
        for line in self.road_lines:
            pygame.draw.rect(screen, YELLOW, (line["x"], line["y"], line["width"], line["height"]))
    
    def spawn_person(self):
        self.spawn_timer += 1
        if self.spawn_timer >= 30 - min(self.level * 2, 25):  # Увеличиваем частоту появления с уровнем
            self.people.append(Person())
            self.spawn_timer = 0
    
    def update(self):
        if self.game_over or self.win:
            return
        
        # Увеличиваем скорость машины со временем
        if pygame.time.get_ticks() % 100 == 0:
            self.car.increase_speed()
        
        # Обновляем линии разметки
        self.update_road_lines()
        
        # Создаем новых людей
        self.spawn_person()
        
        # Обновляем позиции людей
        for person in self.people[:]:
            person.update()
            
            # Проверяем столкновение
            if person.check_collision(self.car):
                self.score += 1
                # Увеличиваем скорость машины при наезде
                self.car.increase_speed()
            
            # Удаляем людей, ушедших за экран
            if person.y > SCREEN_HEIGHT:
                self.people.remove(person)
        
        # Проверяем завершение уровня
        if self.score >= self.target:
            self.level += 1
            self.target = self.level * 10
            self.people = []  # Очищаем людей
            
            # Если достигли 3 уровня, победа
            if self.level > 3:
                self.win = True
    
    def draw(self):
        # Рисуем дорогу
        self.draw_road()
        
        # Рисуем людей
        for person in self.people:
            person.draw()
        
        # Рисуем машину
        self.car.draw()
        
        # Рисуем интерфейс
        self.draw_ui()
        
        # Рисуем экран завершения игры
        if self.game_over:
            self.draw_game_over()
        elif self.win:
            self.draw_win_screen()
    
    def draw_ui(self):
        # Рисуем счет
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Сбито: {self.score}/{self.target}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        level_text = font.render(f"Уровень: {self.level}/3", True, WHITE)
        screen.blit(level_text, (20, 60))
        
        speed_text = font.render(f"Скорость: {int(self.car.speed)}", True, WHITE)
        screen.blit(speed_text, (20, 100))
        
        # Рисуем инструкции
        small_font = pygame.font.SysFont(None, 24)
        instr1 = small_font.render("Управление: ← →", True, WHITE)
        instr2 = small_font.render("Цель: сбить 10, 20, затем 30 человек", True, WHITE)
        screen.blit(instr1, (SCREEN_WIDTH - instr1.get_width() - 20, 20))
        screen.blit(instr2, (SCREEN_WIDTH - instr2.get_width() - 20, 50))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont(None, 72)
        text = font.render("ИГРА ОКОНЧЕНА", True, RED)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        font = pygame.font.SysFont(None, 36)
        restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_win_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont(None, 72)
        text = font.render("ПОБЕДА!", True, GREEN)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Итоговый счет: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        
        restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

# Основная функция игры
def main():
    game = Game()
    running = True
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game.game_over or game.win):
                    game = Game()  # Перезапуск игры
        
        # Получаем нажатые клавиши
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.car.move("left")
        if keys[pygame.K_RIGHT]:
            game.car.move("right")
        
        # Обновление игры
        game.update()
        
        # Отрисовка
        screen.fill(BLACK)
        game.draw()
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()