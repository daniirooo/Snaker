import random
import pygame
import pickle

# Инициализация Pygame
pygame.init()

# Установка размеров экрана и размеров сетки
SCREEN = WIDTH, HEIGHT = 288, 512
CELLSIZE = 16  # Размер ячейки
ROWS = HEIGHT // CELLSIZE  # Количество строк
COLS = WIDTH // CELLSIZE   # Количество столбцов

# Получение информации о дисплее для настройки игрового окна
info = pygame.display.Info()
width = info.current_w
height = info.current_h

# Создание окна игры в зависимости от размеров дисплея
if width >= height:
	win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)  # Окно без рамок
else:
	win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)  # Полноэкранный режим с масштабированием для портретного экрана

# Настройка частоты кадров (FPS)
FPS = 10
clock = pygame.time.Clock()

# ЦВЕТА *********************************************************************
BLACK = (0, 0, 0)  # Чёрный цвет
BLUE = (0, 0, 255)  # Синий цвет
RED = (255, 0, 0)  # Красный цвет
GREEN = (0, 255, 0)  # Зелёный цвет
WHITE = (255, 255, 255)  # Белый цвет

# ЗАГРУЗКА ШРИФТОВ **********************************************************
smallfont = pygame.font.SysFont('Corbel', 25)  # Шрифт для отображения текста

# РЕЖИМЫ ИГРЫ *****************************************************************
gameoptions = ['Classic', 'Boxed', 'Arcade', 'Exit']  # Варианты игры
cmode = 0  # Текущий выбранный режим

# ЗАГРУЗКА ИЗОБРАЖЕНИЙ ********************************************************
bg = pygame.image.load('Assets/bg.png')  # Задний фон
logo = pygame.image.load('Assets/logo.jpg')  # Логотип
logo2 = pygame.image.load('Assets/logo2.jpg')  # Второй логотип

gameover_img = pygame.image.load('Assets/gameover.png')  # Картинка "игра окончена"
bar_img = pygame.image.load('Assets/bar.png')  # Изображение для полоски прогресса в Arcade-режиме

# ЗАГРУЗКА ТАЙЛОВ ************************************************************
tile_list = []
for i in range(5):
	tile = pygame.image.load(f'Tiles/{i+1}.png')  # Загрузка изображений тайлов
	tile_list.append(tile)

tile_size = {
	1: (16, 64),  # Размеры каждого тайла
	2: (64, 16),
	3: (32, 32),
	4: (32, 32),
	5: (32, 32)
}

# ФУНКЦИИ И КЛАССЫ ***********************************************************

# Функция для отрисовки сетки
def drawGrid():
	for row in range(ROWS):
		pygame.draw.line(win, WHITE, (0, row * CELLSIZE), (WIDTH, row * CELLSIZE), 1)  # Линии по строкам
	for col in range(COLS):
		pygame.draw.line(win, WHITE, (col * CELLSIZE, 0), (col * CELLSIZE, HEIGHT), 1)  # Линии по столбцам

# Загрузка уровня игры
def loadlevel(level):
	if level == 'boxed':
		file = f'Levels/boxed'  # Загрузка уровня с "коробкой"
	else:
		file = f'Levels/level{level}_data'  # Загрузка других уровней
	with open(file, 'rb') as f:
		data = pickle.load(f)  # Чтение данных уровня из файла
		for y in range(len(data)):
			for x in range(len(data[0])):
				if data[y][x] >= 0:
					data[y][x] += 1
	return data, len(data[0])

# Проверка столкновения змейки с тайлами уровня
def tile_collide(leveld, head):
	for y in range(ROWS):
		for x in range(COLS):
			if leveld[y][x] > 0:  # Проверка, есть ли препятствие
				tile = leveldata[y][x]
				pos = (x * CELLSIZE, y * CELLSIZE)

				rect = pygame.Rect(pos[0], pos[1], tile_size[tile][0],
								tile_size[tile][1])
				if rect.collidepoint(head):  # Если змейка коснулась препятствия
					return True

	return False

# Класс "Змейка"
class Snake:
	def __init__(self):
		self.length = 3  # Начальная длина змейки
		self.direction = None  # Направление движения
		self.x = COLS // 2
		self.y = ROWS // 2
		self.head = COLS // 2 * CELLSIZE, ROWS // 2 * CELLSIZE  # Позиция головы
		self.body = [[self.head[0] - 2 * CELLSIZE, self.head[1]],  # Координаты тела змейки
					[self.head[0] - CELLSIZE, self.head[1]],
					self.head]
		print(self.body)

		# Загрузка изображений головы змейки для разных направлений
		self.headup = pygame.image.load('Assets/body/uhead.png')
		self.headdown = pygame.image.load('Assets/body/dhead.png')
		self.headleft = pygame.image.load('Assets/body/lhead.png')
		self.headright = pygame.image.load('Assets/body/rhead.png')

	# Обновление позиции змейки
	def update(self):
		head = self.body[-1]  # Получение текущей головы змейки
		if self.direction == 'up':
			head = [head[0], head[1] - CELLSIZE]  # Движение вверх
		elif self.direction == 'down':
			head = [head[0], head[1] + CELLSIZE]  # Движение вниз
		elif self.direction == 'left':
			head = [head[0] - CELLSIZE, head[1]]  # Движение влево
		elif self.direction == 'right':
			head = [head[0] + CELLSIZE, head[1]]  # Движение вправо

		self.head = head  # Обновление головы змейки
		self.body.append(self.head)  # Добавление головы к телу
		if self.length < len(self.body):  # Удаление последнего элемента, если длина превышена
			self.body.pop(0)

		# Проверка на выход за границы экрана
		snake.outOfBound()

	# Проверка на выход за границы экрана
	def outOfBound(self):
		for index, block in enumerate(self.body):
			if block[0] > WIDTH:
				self.body[index][0] = 0  # Если змейка вышла справа, появляется слева
			elif block[0] < 0:
				self.body[index][0] = WIDTH - CELLSIZE  # Если вышла слева, появляется справа
			elif block[1] > HEIGHT:
				self.body[index][1] = 0  # Если вышла снизу, появляется сверху
			elif block[1] < 0:
				self.body[index][1] = HEIGHT - CELLSIZE  # Если вышла сверху, появляется снизу

	# Увеличение длины змейки при съедании еды
	def eatFood(self):
		self.length += 1

	# Проверка, съела ли змейка еду
	def checkFood(self, food):
		if self.head[0] == food.x and self.head[1] == food.y:
			return True
		return False

	# Проверка, столкнулась ли змейка со своим хвостом
	def tailCollision(self):
		head = self.body[-1]  # Координаты головы
		has_eaten_tail = False

		for i in range(len(self.body)-2):  # Проверка по каждому блоку тела, кроме головы
			block = self.body[i]
			if head[0] == block[0] or head[1] == block[1]:  # Если координаты совпадают
				has_eaten_tail = True

		return has_eaten_tail

	# Отрисовка змейки
	def draw(self):
		for index, block in enumerate(self.body):
			x, y = block
			rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)  # Создание блока тела
			if index == self.length - 1:  # Отображение головы змейки
				head = self.body[index]
				neck = self.body[index-1]
				image = self.headright  # Изображение головы по умолчанию (вправо)
				if head[0] == neck[0] and head[1] < neck[1]:
					image = self.headup  # Если движется вверх
				elif head[0] == neck[0] and head[1] > neck[1]:
					image = self.headdown  # Если движется вниз
				elif head[0] < neck[0] and head[1] == neck[1]:
					image = self.headleft  # Если движется влево
				win.blit(image, (x, y))  # Отображение головы
			else:
				pygame.draw.rect(win, GREEN, rect)  # Отображение тела змейки
# Класс "Еда"
class Food:
	def __init__(self):
		type_ = random.randint(1, 3)  # Выбор случайного типа еды
		self.image = self.temp = pygame.image.load(f'Assets/{type_}.png')  # Загрузка изображения еды
		self.size = 16  # Начальный размер еды
		self.ds = 1  # Направление изменения размера
		self.counter = 0  # Счётчик для изменения размера
		self.respawn()  # Появление еды на экране

	# Установка новой позиции еды
	def respawn(self):
		self.x = random.randint(0, COLS - 1) * CELLSIZE  # Случайная координата X
		self.y = random.randint(0, ROWS - 1) * CELLSIZE  # Случайная координата Y

		if tile_collide(leveldata, (self.x, self.y)):  # Если еда попадает на препятствие, появится снова
			self.respawn()

	# Обновление состояния еды
	def update(self):
		self.counter += 1
		if self.counter % 3 == 0:  # Изменение размера еды каждые 3 кадра
			self.size += self.ds
			if self.size < 15 or self.size > 17:  # Если размер выходит за пределы, меняем направление
				self.ds *= -1

			self.temp = pygame.transform.scale(self.image, (self.size, self.size))  # Масштабирование изображения

	# Отрисовка еды
	def draw(self):
		win.blit(self.temp, (self.x, self.y))  # Отображение еды на экране

# Класс "Дерево" (используется только в классическом и коробочном режимах)
class Tree:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.counter = self.index = 0

		# Загрузка изображений для анимации дерева
		self.imglist = []
		for i in range(4):
			img = pygame.image.load(f'Assets/tree{i}.png')
			self.imglist.append(img)
		self.image = self.imglist[self.index]

	# Обновление состояния дерева (анимация)
	def update(self):
		self.counter += 1
		if self.counter % 3 == 0:  # Изменение изображения каждые 3 кадра
			self.index = (self.index + 1) % 3
			self.counter = 0
			self.image = self.imglist[self.index]

	# Отрисовка дерева
	def draw(self):
		win.blit(self.image, (self.x, self.y))  # Отображение дерева на экране

# ИГРОВЫЕ ПЕРЕМЕННЫЕ *********************************************************
level = 1  # Начальный уровень
MAX_LEVEL = 4  # Максимальный уровень для режима Arcade
score = 0  # Начальный счёт

snake = Snake()  # Создание объекта змейки
tree = Tree(WIDTH // 2 - 8, HEIGHT // 2 - 52)  # Создание объекта дерева

homepage = True  # Начальное состояние: главная страница
gamepage = False  # Начальное состояние: игровая страница
gameover = False  # Начальное состояние: игра не окончена

# Основной игровой цикл
running = True
while running:
	selected = False
	win.fill(BLACK)  # Очистка экрана
	win.blit(bg, (0, 0))  # Отображение фона
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False  # Закрытие игры при выходе

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False  # Закрытие игры при нажатии Esc

			if homepage:
				if event.key == pygame.K_UP:
					cmode -= 1  # Выбор предыдущего режима
					if cmode < 0:
						cmode = 3  # Зацикливание выбора

				if event.key == pygame.K_DOWN:
					cmode += 1  # Выбор следующего режима
					if cmode > 3:
						cmode = 0  # Зацикливание выбора

				if event.key == pygame.K_RETURN:
					selected = True  # Подтверждение выбора режима
					if cmode == 3:
						running = False  # Закрытие игры при выборе выхода

			if event.key == pygame.K_RIGHT and snake.direction != 'left':
				snake.direction = 'right'  # Изменение направления движения змейки

			if event.key == pygame.K_LEFT and snake.direction != 'right':
				snake.direction = 'left'

			if event.key == pygame.K_UP and snake.direction != 'down':
				snake.direction = 'up'

			if event.key == pygame.K_DOWN and snake.direction != 'up':
				snake.direction = 'down'

	# Отображение главной страницы
	if homepage:
		win.blit(logo, (0, 0))  # Отображение логотипа
		win.blit(logo2, (0, 225))  # Отображение второго логотипа

		for index, mode in enumerate(gameoptions):
			color = (32, 32, 32)  # Цвет текста для неактивного варианта
			if cmode == index:
				color = WHITE  # Цвет текста для активного варианта
			shadow = smallfont.render(mode, True, color)  # Тень текста
			text = smallfont.render(mode, True, WHITE)  # Текст
			win.blit(text, (WIDTH // 2 - text.get_width() // 2 + 1, HEIGHT // 2 + 55 * index + 1))  # Отображение тени
			win.blit(shadow, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 55 * index))  # Отображение текста

		if selected:
			if cmode == 0:
				leveldata = [[0 for i in range(COLS)] for j in range(ROWS)]  # Создание пустого уровня

			if cmode == 1:
				level = 'boxed'
				leveldata, length = loadlevel(level)  # Загрузка уровня с "коробкой"

			if cmode == 2:
				level = 1
				leveldata, length = loadlevel(level)  # Загрузка уровня для режима Arcade

			snake.__init__()  # Инициализация змейки
			food = Food()  # Создание объекта еды

			homepage = False  # Переход к игровому экрану
			gamepage = True
			score = 0  # Сброс счёта

		pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 2)  # Рисование рамки вокруг экрана

	# Отображение игрового экрана
	if gamepage:
		# drawGrid()  # Отрисовка сетки (закомментировано)

		if not gameover:
			# Отображение уровня
			for y in range(ROWS):
				for x in range(COLS):
					if leveldata[y][x] > 0:
						tile = leveldata[y][x]
						pos = (x * CELLSIZE, y * CELLSIZE)
						rect = pygame.Rect(pos[0], pos[1], tile_size[tile][0],
								tile_size[tile][1])

						if tile != 3:
							pygame.draw.rect(win, (18, 18, 18), (rect.x + 2, rect.y + 2,
										 rect.width, rect.height))  # Рисование фона для тайлов
						win.blit(tile_list[tile - 1], pos)  # Отображение тайлов
						if rect.collidepoint(snake.head):
							gameover = True  # Завершение игры, если змейка столкнулась с тайлом

			snake.update()  # Обновление состояния змейки
			snake.checkFood(food)  # Проверка, съела ли змейка еду
			snake.draw()  # Отображение змейки
			food.update()  # Обновление состояния еды
			food.draw()  # Отображение еды

			if snake.checkFood(food):
				snake.eatFood()  # Увеличение длины змейки
				food.respawn()  # Появление новой еды
				score += 1  # Увеличение счёта

			if cmode == 0 or cmode == 1:
				tree.update()  # Обновление состояния дерева
				tree.draw()  # Отображение дерева

				score_img = smallfont.render(f'{score}', True, WHITE)  # Отображение счёта
				win.blit(score_img, (WIDTH - 30 - score_img.get_width() // 2, HEIGHT - 50))

			elif cmode == 2:
				bar = pygame.transform.scale(bar_img, (score * 10, 10))  # Полоска прогресса для Arcade-режима
				win.blit(bar, (WIDTH // 2 - 50, HEIGHT - 50))
				pygame.draw.rect(win, WHITE, (WIDTH // 2 - 50, HEIGHT - 51, 100, 10), 1, border_radius=10)  # Рисование рамки для полоски

				if score and score % 10 == 0:
					level += 1
					if level <= MAX_LEVEL:
						leveldata, length = loadlevel(level)  # Загрузка нового уровня
						score = 0  # Сброс счёта
						snake.__init__()  # Инициализация змейки
					else:
						gameover = True  # Завершение игры, если достигнут максимальный уровень

		else:
			win.blit(gameover_img, (WIDTH // 2 - gameover_img.get_width() // 2, 80))  # Отображение экрана окончания игры
			pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 2)  # Рисование рамки для экрана окончания игры

	clock.tick(FPS)  # Контроль частоты кадров
	pygame.display.update()  # Обновление экрана

pygame.quit()  # Завершение работы Pygame
