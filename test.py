from ursina import *

app = Ursina()

class StartMenu(Entity):
    def __init__(self):
        super().__init__(
            model='quad',
            scale=(3, 1, 1),
            color=color.white,
            position=(0, 0, 0),
            collider='box'
        )
        self.start_button = Button(text='Start', scale=0.1, color=color.black, parent=self, position=(0, 0))

    def start_game(self):
        self.disable()
        car_simulation.enabled = True  # Enable the car simulation when the game starts

class Car(Entity):
    def __init__(self, position=(22, 90, 0), scale=(0.6, 0.6, 0.6), rotation=(0, 0, 0), topspeed=12, acceleration=0.08, braking_strength=10, friction=0.6, camera_speed=8, drift_speed=19, rotation_decay=0.4):
        super().__init__(
            model="sphere",
            scale=scale,
            collider="box",
            position=position,
            rotation=rotation,
        )
        self.speed = Vec3(0, 0, 0)
        self.rotation_speed = 0
        self.topspeed = topspeed
        self.acceleration = acceleration
        self.braking_strength = braking_strength
        self.friction = friction
        self.camera_speed = camera_speed
        self.drift_speed = drift_speed
        self.rotation_decay = rotation_decay
        self.is_drifting = False
        self.default_attributes = {
            'topspeed': topspeed,
            'acceleration': acceleration,
            'friction': friction,
            'drift_speed': drift_speed,
            'rotation_decay': rotation_decay
        }

# Create start menu
start_menu = StartMenu()

# Create car simulation scene
car_simulation = Entity(enabled=False)  # Initially disabled until the game starts

# Create racetrack entity
racetrack = Entity(model="quad", scale=(12, 12, 12), position=(0, -50, 0), rotation=(90, 0, 0), color=color.gray, collider="box")

# Create box outline
left_wall = Entity(model='cube', visible=False, scale=(0.1, 2, 40), position=(-1.2, -47, 17.5))
bottom_wall = Entity(model='cube', visible=False, scale=(77, 2, 0.1), position=(-18.6, -47, 17))
top_wall = Entity(model='cube', visible=False, scale=(18.93, 2, 29.8), position=(7.1, -47, 23.8))
right_wall = Entity(model='cube', visible=False, scale=(0.1, 2, 39.7), position=(15.65, -47, 2.65))

# Initialize car
car = Car()

# Run the app
app.run()
