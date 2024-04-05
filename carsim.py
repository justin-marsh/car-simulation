from ursina import *

app = Ursina()

# Load car and racetrack models
car_model = 'assets/sports-car.obj'
track_model = 'assets/racetrack.obj'

class Car(Entity):
    def __init__(self, model, scale, position, texture):
        super().__init__(
            model=model,
            scale=scale,
            position=position,
            texture=texture
        )

        # Set up gravity
        self.gravity = 0.05
        self.vertical_speed = 0

        # Car physics parameters
        self.max_velocity = 4  # Reduced max velocity
        self.max_acceleration = 10.0
        self.brake_deceleration = 20  # Increased brake deceleration
        self.free_deceleration = 5  # Increased free deceleration
        self.max_steering = 170

        # Car state variables
        self.velocity = Vec3(0.0, 0.0, 0.0)
        self.rotation_speed = 170
        self.rotation_y = 0.0

    def update(self):
        dt = time.dt

        # Update car movement
        if held_keys['w']:
            self.velocity.z += self.max_acceleration * dt
        elif self.velocity.z > 0:
            self.velocity.z -= self.brake_deceleration * dt
            if self.velocity.z < 0:
                self.velocity.z = 0
        if held_keys['a']:
            self.velocity.x -= self.max_acceleration * dt
        if held_keys['d']:
            self.velocity.x += self.max_acceleration * dt

        # Update car rotation
        if held_keys['d']:
            self.rotation_y -= self.rotation_speed * dt
        elif held_keys['a']:
            self.rotation_y += self.rotation_speed * dt

        # Rotate the car
        self.rotation_y = max(-self.max_steering, min(self.rotation_y, self.max_steering))
        self.rotation_y = round(self.rotation_y, 2)
        self.rotation = (0, self.rotation_y, 0)

        # Update car physics
        self.position += self.velocity * dt

        # Apply gravity
        self.vertical_speed -= self.gravity
        self.y += self.vertical_speed

        # Check if the car is on the ground
        if self.y < 0:
            self.y = 0
            self.vertical_speed = 0

# Create car entity
car = Car(model=car_model, scale=(0.3, 0.3, 0.3), position=(-11, 20, -110), texture="assets/sports-black.png")

# Create racetrack entity
racetrack = Entity(model="assets/racetrack.obj", scale=(12, 12, 12), position=(0, -50, 0), texture="assets/racetrack.png")

# Initialize camera position and rotation
camera.position = (0, 50, -300)
camera.rotation = (0, 0, 0)

# Function to update camera position
def update_camera():
    camera.position = car.position + (0, 20, -50)  # Set camera position relative to car
    camera.look_at(car.position)  # Make camera look at the car

# Create Text object to display camera position
camera_position_text = Text(text='', origin=(0, 0), y=-0.45)

def update():
    # Update car movement
    car.update()

    # Update camera position
    update_camera()

    # Update camera position text
    camera_position_text.text = f"Camera Position: {camera.position}"

# Run the app
app.run()
