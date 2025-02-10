from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Создаем землю
ground = Entity(
    model='plane',
    texture='white_cube',
    collider='box',
    scale=(20, 1, 20),
    color=color.green
)

# Создаем дверь
door = Entity(
    model='cube',
    color=color.brown,
    collider='box',
    position=(3, 1.5, 3),
    scale=(0.2, 3, 2),
    rotation_y=45
)

# Создаем несколько кубов как препятствия
for i in range(10):
    cube = Entity(
        model='cube',
        color=color.azure,
        collider='box',
        position=(random.randint(-8, 8), 0.5, random.randint(-8, 8)),
        scale=(1, random.uniform(1, 3), 1)
    )

class SimplePlayer(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 5  # Обычная скорость
        self.run_speed = 12  # Скорость бега
        self.height = 2  # Обычная высота
        self.crouch_height = 1  # Высота при приседании
        self.camera_pivot.y = self.height
        self.mouse_sensitivity = Vec2(300, 300)  # Увеличенная чувствительность
        
        # Параметры прыжка и физики
        self.jump_force = 15
        self.gravity = 35
        self.velocity_y = 0
        self.can_jump = True
        self.double_jump_available = True
        
        # Параметры рывка
        self.boost_available = True
        self.boost_cooldown = 1.0
        self.boost_timer = 0
        self.boost_speed = 0
        self.boost_direction = Vec3(0, 0, 0)
        
        # Баланс
        self.balance = 50
        
        # Дополнительные параметры
        self.zoom_level = 90
        self.near_door = False
        
    def update(self):
        # Проверяем бег (shift)
        if held_keys['shift']:
            self.speed = self.run_speed
        else:
            self.speed = 5

        # Проверяем приседание (control)
        if held_keys['control']:
            self.camera_pivot.y = lerp(self.camera_pivot.y, self.crouch_height, time.dt * 5)
            self.speed = 3
        else:
            self.camera_pivot.y = lerp(self.camera_pivot.y, self.height, time.dt * 5)

        # Обновляем движение
        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s']) +
            self.right * (held_keys['d'] - held_keys['a'])
        ).normalized()

        # Применяем обычное движение и рывок
        if self.direction:
            self.position += self.direction * self.speed * time.dt
        
        if self.boost_speed > 0:
            self.position += self.boost_direction * self.boost_speed * time.dt
            self.boost_speed = lerp(self.boost_speed, 0, time.dt * 4)

        # Обновляем поворот камеры
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity.x * time.dt
            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity.y * time.dt
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        # Физика прыжка
        self.velocity_y -= self.gravity * time.dt
        self.y += self.velocity_y * time.dt

        # Проверка приземления
        if self.y <= 0:
            self.y = 0
            self.velocity_y = 0
            self.can_jump = True
            self.double_jump_available = True

        # Обновление буста
        if self.boost_timer > 0:
            self.boost_timer -= time.dt
        else:
            self.boost_available = True

        # Обновление зума
        if held_keys['right mouse']:
            camera.fov = lerp(camera.fov, 30, time.dt * 5)
        else:
            camera.fov = lerp(camera.fov, 90, time.dt * 5)
            
        # Проверка близости к двери
        distance_to_door = distance(self.position, door.position)
        if distance_to_door < 3 and not self.near_door:
            self.near_door = True
            door_text.enabled = True
        elif distance_to_door >= 3 and self.near_door:
            self.near_door = False
            door_text.enabled = False

    def input(self, key):
        # Прыжок
        if key == 'space':
            if self.can_jump:
                self.velocity_y = self.jump_force
                self.can_jump = False
            elif self.double_jump_available:
                self.velocity_y = self.jump_force * 0.8
                self.double_jump_available = False

        # Плавный рывок вперед
        if key == 'f' and self.boost_available:
            self.boost_speed = 20
            self.boost_direction = self.forward
            self.boost_available = False
            self.boost_timer = self.boost_cooldown
            
        # Взаимодействие с дверью
        if key == 'e' and self.near_door:
            if door.rotation_y == 45:  # Дверь закрыта
                invoke(setattr, door, 'rotation_y', 135, duration=0.4)
            else:  # Дверь открыта
                invoke(setattr, door, 'rotation_y', 45, duration=0.4)

# Создаем игрока
player = SimplePlayer(position=(0, 0, 0))

# Настройка мыши
mouse.locked = True
window.fullscreen = True

# Создаем текст с управлением
controls_text = dedent('''
    [W,A,S,D] - Движение
    [Shift] - Бег
    [Control] - Присесть
    [Space] - Прыжок
    [Space x2] - Двойной прыжок
    [F] - Рывок вперед
    [ПКМ] - Прицел
    [Escape] - Курсор
    [E] - Взаимодействие
''').strip()

controls = Text(
    text=controls_text,
    position=(-0.85, 0.4),
    color=color.white,
    scale=1.2
)

# Создаем текст с балансом
balance_text = Text(
    text=f'${player.balance}',
    position=(0.75, 0.45),
    color=color.green,
    scale=2
)

# Создаем текст для двери
door_text = Text(
    text='[E] Открыть/Закрыть',
    position=(-0.85, -0.4),
    color=color.white,
    scale=1.2,
    enabled=False
)

def update():
    balance_text.text = f'${player.balance}'

def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked

app.run()
