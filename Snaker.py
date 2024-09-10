def drawGrid():
    """
    Рисует сетку на игровом поле. Используется для визуального деления игрового экрана на клетки.
    """
    for row in range(ROWS):
        pygame.draw.line(win, WHITE, (0, row*CELLSIZE), (WIDTH, row*CELLSIZE), 1)  # Горизонтальные линии
    for col in range(COLS):
        pygame.draw.line(win, WHITE, (col*CELLSIZE, 0), (col*CELLSIZE, HEIGHT), 1)  # Вертикальные линии

def loadlevel(level):
    """
    Загружает уровень игры из файла.
    
    Аргументы:
    level -- название уровня, которое указывает, какой файл использовать для загрузки уровня.
    
    Возвращает:
    data -- двумерный массив с данными уровня.
    len(data[0]) -- количество колонок в уровне.
    """
    if level == 'boxed':
        file = f'Levels/boxed'
    else:
        file = f'Levels/level{level}_data'
    with open(file, 'rb') as f:
        data = pickle.load(f)  # Загружаем данные уровня из файла
        for y in range(len(data)):
            for x in range(len(data[0])):
                if data[y][x] >= 0:
                    data[y][x] += 1  # Инкрементируем значения для работы с тайлами
    return data, len(data[0])

def tile_collide(leveld, head):
    """
    Проверяет столкновение головы змеи с тайлом.
    
    Аргументы:
    leveld -- массив с данными уровня.
    head -- позиция головы змеи.
    
    Возвращает:
    True, если произошло столкновение, иначе False.
    """
    for y in range(ROWS):
        for x in range(COLS):
            if leveld[y][x] > 0:  # Если тайл существует
                tile = leveldata[y][x]  # Определяем тип тайла
                pos = (x*CELLSIZE, y*CELLSIZE)  # Позиция тайла на экране

                rect = pygame.Rect(pos[0], pos[1], tile_size[tile][0], tile_size[tile][1])  # Создаем прямоугольник тайла
                if rect.collidepoint(head):  # Проверяем столкновение с головой змеи
                    return True
    return False

class Snake:
    """
    Класс, описывающий змею.
    """
    def __init__(self):
        """
        Конструктор класса Snake. Инициализирует змею с длиной 3 клетки и положением в центре экрана.
        """
        self.length = 3  # Длина змеи
        self.direction = None  # Направление движения
        self.x = COLS // 2  # Позиция головы по горизонтали
        self.y = ROWS // 2  # Позиция головы по вертикали
        self.head = COLS // 2 * CELLSIZE, ROWS // 2 * CELLSIZE  # Положение головы в пикселях
        self.body = [[self.head[0] - 2*CELLSIZE, self.head[1]],  # Координаты частей тела змеи
                     [self.head[0] - CELLSIZE, self.head[1]],
                     self.head]

        # Загрузка изображений для головы змеи в разных направлениях
        self.headup = pygame.image.load('Assets/body/uhead.png')
        self.headdown = pygame.image.load('Assets/body/dhead.png')
        self.headleft = pygame.image.load('Assets/body/lhead.png')
        self.headright = pygame.image.load('Assets/body/rhead.png')

    def update(self):
        """
        Обновляет положение змеи на основе направления движения.
        """
        head = self.body[-1]  # Берем последнюю часть змеи (голову)
        if self.direction == 'up':
            head = [head[0], head[1] - CELLSIZE]  # Двигаем вверх
        elif self.direction == 'down':
            head = [head[0], head[1] + CELLSIZE]  # Двигаем вниз
        elif self.direction == 'left':
            head = [head[0] - CELLSIZE, head[1]]  # Двигаем влево
        elif self.direction == 'right':
            head = [head[0] + CELLSIZE, head[1]]  # Двигаем вправо

        self.head = head  # Обновляем позицию головы
        self.body.append(self.head)  # Добавляем новую позицию головы к телу
        if self.length < len(self.body):  # Убираем хвост, если длина тела превышает допустимую
            self.body.pop(0)

        self.outOfBound()  # Проверяем выход за пределы экрана

    def outOfBound(self):
        """
        Проверяет, вышла ли змея за пределы экрана, и возвращает ее с другой стороны.
        """
        for index, block in enumerate(self.body):
            if block[0] > WIDTH:
                self.body[index][0] = 0
            elif block[0] < 0:
                self.body[index][0] = WIDTH - CELLSIZE
            elif block[1] > HEIGHT:
                self.body[index][1] = 0
            elif block[1] < 0:
                self.body[index][1] = HEIGHT - CELLSIZE

    def eatFood(self):
        """
        Увеличивает длину змеи при поедании пищи.
        """
        self.length += 1

    def checkFood(self, food):
        """
        Проверяет, съела ли змея еду.
        
        Аргументы:
        food -- объект класса Food (пища).
        
        Возвращает:
        True, если змея съела еду, иначе False.
        """
        if self.head[0] == food.x and self.head[1] == food.y:
            return True
        return False

    def tailCollision(self):
        """
        Проверяет столкновение головы змеи с ее собственным телом.
        
        Возвращает:
        True, если змея столкнулась с телом, иначе False.
        """
        head = self.body[-1]
        has_eaten_tail = False

        for i in range(len(self.body) - 2):  # Проверяем, не столкнулась ли голова с телом
            block = self.body[i]
            if head[0] == block[0] and head[1] == block[1]:
                has_eaten_tail = True

        return has_eaten_tail

    def draw(self):
        """
        Отображает змею на экране.
        """
        for index, block in enumerate(self.body):
            x, y = block
            rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            if index == self.length - 1:  # Отображаем голову
                head = self.body[index]
                neck = self.body[index - 1]
                image = self.headright
                if head[0] == neck[0] and head[1] < neck[1]:
                    image = self.headup
                elif head[0] == neck[0] and head[1] > neck[1]:
                    image = self.headdown
                elif head[1] == neck[1] and head[0] < neck[0]:
                    image = self.headleft
                elif head[1] == neck[1] and head[0] > neck[0]:
                    image = self.headright
                win.blit(image, (x, y))  # Рисуем изображение головы

class Food:
    """
    Класс, описывающий пищу для змеи.
    """
    def __init__(self):
        """
        Конструктор класса Food. Инициализирует еду с рандомным типом и местоположением.
        """
        type_ = random.randint(1, 3)
        self.image = self.temp = pygame.image.load(f'Assets/{type_}.png')  # Загрузка изображения еды
        self.size = 16
        self.ds = 1
        self.counter = 0
        self.respawn()

    def respawn(self):
        """
        Перемещает еду на новое случайное место на игровом поле.
        """
        self.x = random.randint(0, COLS - 1) * CELLSIZE
        self.y = random.randint(0, ROWS - 1) * CELLSIZE

        if tile_collide(leveldata, (self.x, self.y)):  # Проверяем, не находится ли еда на тайле
            self.respawn()

    def update(self):
        """
        Обновляет состояние еды: увеличивает или уменьшает размер для анимации.
        """
        self.counter += 1
        if self.counter % 3 == 0:
            self.size += self.ds
            if self.size < 15 or self.size > 17:
                self.ds *= -1

            self.temp = pygame.transform.scale(self.image, (self.size, self.size))  # Изменяем размер изображения еды

    def draw(self):
        """
        Отображает еду на экране.
        """
        win.blit(self.temp, (self.x + (CELLSIZE - self.size) // 2, self.y + (CELLSIZE - self.size) // 2))
class Tree:
    """
    Класс, описывающий дерево, которое используется как элемент декорации на игровом поле.
    """
    def __init__(self, x, y):
        """
        Конструктор класса Tree. Инициализирует дерево с заданной позицией и загружает изображения для анимации.
        
        Аргументы:
        x -- позиция дерева по горизонтали.
        y -- позиция дерева по вертикали.
        """
        self.x = x
        self.y = y
        self.counter = self.index = 0

        self.imglist = []
        for i in range(4):
            img = pygame.image.load(f'Assets/tree{i}.png')  # Загрузка изображений дерева
            self.imglist.append(img)
        self.image = self.imglist[self.index]

    def update(self):
        """
        Обновляет состояние дерева: изменяет изображение для создания анимации.
        """
        self.counter += 1
        if self.counter % 3 == 0:
            self.index = (self.index + 1) % 4  # Переключаем изображение
            self.counter = 0
            self.image = self.imglist[self.index]

    def draw(self):
        """
        Отображает дерево на экране.
        """
        win.blit(self.image, (self.x, self.y))

# Переменные игры
level = 1
MAX_LEVEL = 4
score = 0

snake = Snake()
tree = Tree(WIDTH // 2 - 8, HEIGHT // 2 - 52)

homepage = True
gamepage = False
gameover = False

running = True
while running:
    selected = False
    win.fill(BLACK)
    win.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if homepage:
                if event.key == pygame.K_UP:
                    cmode -= 1
                    if cmode < 0:
                        cmode = 3

                if event.key == pygame.K_DOWN:
                    cmode += 1
                    if cmode > 3:
                        cmode = 0

                if event.key == pygame.K_RETURN:
                    selected = True
                    if cmode == 3:
                        running = False

            if event.key == pygame.K_RIGHT and snake.direction != 'left':
                snake.direction = 'right'

            if event.key == pygame.K_LEFT and snake.direction != 'right':
                snake.direction = 'left'

            if event.key == pygame.K_UP and snake.direction != 'down':
                snake.direction = 'up'

            if event.key == pygame.K_DOWN and snake.direction != 'up':
                snake.direction = 'down'

    if homepage:
        # Отображение главного меню
        win.blit(logo, (0, 0))
        win.blit(logo2, (0, 225))

        for index, mode in enumerate(gameoptions):
            color = (32, 32, 32)
            if cmode == index:
                color = WHITE
            shadow = smallfont.render(mode, True, color)
            text = smallfont.render(mode, True, WHITE)
            win.blit(text, (WIDTH // 2 - text.get_width() // 2 + 1, HEIGHT // 2 + 55 * index + 1))
            win.blit(shadow, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 55 * index))

        if selected:
            if cmode == 0:
                leveldata = [[0 for i in range(COLS)] for j in range(ROWS)]  # Пустой уровень

            if cmode == 1:
                level = 'boxed'
                leveldata, length = loadlevel(level)

            if cmode == 2:
                level = 1
                leveldata, length = loadlevel(level)
                
            snake.__init__()  # Перезапуск змеи
            food = Food()

            homepage = False
            gamepage = True
            score = 0            

        pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 2)  # Рисуем рамку вокруг экрана

    if gamepage:
        # Отображение игрового процесса
        if not gameover:    
            # Рисуем уровень
            for y in range(ROWS):
                for x in range(COLS):
                    if leveldata[y][x] > 0:
                        tile = leveldata[y][x]
                        pos = (x * CELLSIZE, y * CELLSIZE)
                        rect = pygame.Rect(pos[0], pos[1], tile_size[tile][0], tile_size[tile][1])

                        if tile != 3:
                            pygame.draw.rect(win, (18, 18, 18), (rect.x + 2, rect.y + 2, rect.width, rect.height))
                        win.blit(tile_list[tile - 1], pos)
                        if rect.collidepoint(snake.head):
                            gameover = True

            snake.update()  # Обновляем состояние змеи
            snake.checkFood(food)  # Проверяем, съела ли змея еду
            snake.draw()  # Отображаем змею
            food.update()  # Обновляем состояние еды
            food.draw()  # Отображаем еду

            if snake.checkFood(food):
                snake.eatFood()  # Увеличиваем длину змеи
                food.respawn()  # Перемещаем еду
                score += 1

            if cmode == 0 or cmode == 1:
                tree.update()  # Обновляем состояние дерева
                tree.draw()  # Отображаем дерево

                score_img = smallfont.render(f'{score}', True, WHITE)
                win.blit(score_img, (WIDTH - 30 - score_img.get_width() // 2, HEIGHT - 50))

            elif cmode == 2:
                bar = pygame.transform.scale(bar_img, (score * 10, 10))
                win.blit(bar, (WIDTH // 2 - 50, HEIGHT - 50))
                pygame.draw.rect(win, WHITE, (WIDTH // 2 - 50, HEIGHT - 51, 100, 10), 1, border_radius=10)

                if score and score % 10 == 0:
                    level += 1
                    if level <= MAX_LEVEL:
                        leveldata, length = loadlevel(level)
                        score = 0
                        snake.__init__()
                    else:
                        gameover = True
        else:
            win.blit(gameover_img, (WIDTH // 2 - gameover_img.get_width() // 2, 80))
            pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 2)

    clock.tick(FPS)  # Устанавливаем частоту кадров
    pygame.display.update()  # Обновляем экран

pygame.quit()
