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
            model="sports-car.obj",
            scale=scale,
            texture="sports-black.png",
            collider="box",
            position=position,
            rotation=rotation,
        )

        # Car attributes and controls
        self.speed = Vec3(0, 0, 0)
        self.rotation_speed = 0
        self.topspeed = topspeed
        self.acceleration = acceleration
        self.braking_strength = braking_strength
        self.friction = friction
        self.camera_speed = camera_speed
        self.drift_speed = drift_speed
        self.rotation_decay = rotation_decay  # Decay factor for rotation speed
        self.is_drifting = False  # Flag to indicate if the car is drifting
        self.default_attributes = {
            'topspeed': topspeed,
            'acceleration': acceleration,
            'friction': friction,
            'drift_speed': drift_speed,
            'rotation_decay': rotation_decay
        }
        self.in_water = False  # Flag to indicate if the car is in water

        # Gravity
        self.velocity_y = 0

        # Rotation parent for smoother rotation
        self.rotation_parent = Entity(parent=self, y=1.4)

    def update(self):
        # Check if the car is in water
        self.in_water = self.is_in_water()

        # Update car movement
        self.update_movement()

        # Reset car attributes if not in water
        if not self.in_water:
            self.reset_attributes()

    def is_in_water(self):
        water_pad_coordinates = [
        (45, -46, 37.21),
        (21, -46, 60),
        (36, -46, 85.6),
        (67, -46, 62)
        ]

        # Extract x and z coordinates of the water pad corners
        x_coords = [coord[0] for coord in water_pad_coordinates]
        z_coords = [coord[2] for coord in water_pad_coordinates]

        # Check if the car's position is inside the bounding box formed by water pad coordinates
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        x_car, _, z_car = self.position
        return x_car >= x_min and x_car <= x_max and z_car >= z_min and z_car <= z_max

    def is_in_mud(self):
        mud_coordinates = [
        (-62.6, -46, 38),
        (-40.41, -46, -2.1),
        (-56.6, -46, -33.8),
        (-77, -46, -13)
        ]

        # Extract x and z coordinates of the mud area corners
        x_coords = [coord[0] for coord in mud_coordinates]
        z_coords = [coord[2] for coord in mud_coordinates]

        # Check if the car's position is inside the bounding box formed by mud area coordinates
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        x_car, _, z_car = self.position
        return x_car >= x_min and x_car <= x_max and z_car >= z_min and z_car <= z_max

    def is_in_sand(self):
        sand_coordinates = [
            (38, -46, -68),
            (47, -46, -49.28),
            (70.6, -46, -52),
            (53.15, -46, -89)
        ]

        # Extract x and z coordinates of the sand area corners
        x_coords = [coord[0] for coord in sand_coordinates]
        z_coords = [coord[2] for coord in sand_coordinates]

        # Check if the car's position is inside the bounding box formed by sand area coordinates
        x_min, x_max = min(x_coords), max(x_coords)
        z_min, z_max = min(z_coords), max(z_coords)
        
        x_car, _, z_car = self.position
        return x_car >= x_min and x_car <= x_max and z_car >= z_min and z_car <= z_max


    def update_movement(self):
        acceleration = self.acceleration if held_keys['w'] or held_keys['up arrow'] else 0
        deceleration = self.braking_strength if held_keys['s'] or held_keys['down arrow'] else self.friction

        # Apply reverse acceleration when 's' is pressed
        if held_keys['s'] or held_keys['down arrow']:
            self.speed -= self.forward * self.acceleration * time.dt
            self.topspeed = 3  # Reset topspeed when reversing
        else:
            self.speed -= self.speed * self.friction * time.dt

        # Set the speed based on acceleration and deceleration only when 'w' is pressed
        if held_keys['w'] or held_keys['up arrow']:
            self.speed += self.forward * self.acceleration * time.dt
            self.topspeed = 6  # Reset topspeed when accelerating
        else:
            # Slow down gradually when 'w' is released
            self.speed -= self.speed * self.friction * time.dt

        rotation_direction = 0

        if held_keys['d'] or held_keys['right arrow']:
            rotation_direction = 1
        elif held_keys['a'] or held_keys['left arrow']:
            rotation_direction = -1
        else:
            rotation_direction = 0

        # Update rotation speed regardless of drifting
        self.rotation_speed += rotation_direction * self.drift_speed * time.dt

        # Check if the car is drifting
        if abs(rotation_direction) > 0 and self.speed.length() > self.topspeed * 0.9:
            self.is_drifting = True
        else:
            self.is_drifting = False

        if self.is_drifting:
            self.rotation_speed += rotation_direction * self.drift_speed * time.dt

        # Apply rotation decay if no rotation keys are pressed
        if rotation_direction == 0:
            self.rotation_speed -= self.rotation_speed * self.rotation_decay * time.dt

        # Limit the speed to the topspeed
        self.speed = Vec3(
            min(max(self.speed[0], -self.topspeed), self.topspeed),
            self.speed[1],
            min(max(self.speed[2], -self.topspeed), self.topspeed)
        )

        # Move the car based on the calculated speed
        self.position += self.speed

        # Rotate the car based on the rotation speed
        self.rotation_y += self.rotation_speed * time.dt

        # Collision detection with box outline
        if self.intersects().hit:
            self.position -= self.speed  # Revert position if intersects with any entity
            self.reset_prompt.visible = True

        # Check if car is hitting the ground
        if self.visible:
            y_movement = self.velocity_y * 50 * time.dt
            y_ray = raycast(origin=self.position, direction=(0, -1, 0), ignore=[self])
            if y_ray.hit and y_ray.distance <= self.scale_y * 1.7 + abs(y_movement):
                self.velocity_y = 0
                # Calculate the ground normal directly from the collision raycast
                self.ground_normal = y_ray.world_normal

                # Check if hitting a wall or steep slope
                if self.ground_normal.y > 0.7 and y_ray.world_point.y - self.world_y < 0.5:
                    # Set the y value to the ground's y value
                    self.y = y_ray.world_point.y + 1.4
                    self.hitting_wall = False
                else:
                    # Car is hitting a wall
                    self.hitting_wall = True

                # Rotates the car according to the ground's normals
                if not self.hitting_wall:
                    look_at_direction = self.ground_normal - self.rotation_parent.position
                else:
                    self.rotation_parent.rotation = self.rotation

        if self.y > -45.99:
            # Apply gravity to the car when it's not on the ground
            self.y += y_movement
            self.velocity_y -= 50 * time.dt
            self.rotation_parent.rotation = self.rotation
            self.start_fall = True
        
        # Adjust car attributes while in water
        if self.in_water:
            self.topspeed = 1
            self.acceleration = 0.01
            self.friction = 0.8
            self.drift_speed = 0.1
            self.rotation_decay = 0.9

            # Limit the speed to the topspeed with adjusted values
            self.speed = Vec3(
                min(max(self.speed[0], -self.topspeed), self.topspeed),
                self.speed[1],
                min(max(self.speed[2], -self.topspeed), self.topspeed)
            )
        
        # Adjust car attributes while in water
        if self.is_in_mud:
            self.topspeed = 6
            self.acceleration = 0.03
            self.friction = 0.3
            self.drift_speed = 11
            self.rotation_decay = 0.1
        
        # Adjust car attributes while in sand
        if self.is_in_sand():
            self.topspeed = 8  # Adjust top speed on sand
            self.acceleration = 0.05  # Adjust acceleration on sand
            self.friction = 0.5  # Adjust friction on sand
            self.drift_speed = 15  # Adjust drift speed on sand
            self.rotation_decay = 0.3  # Adjust rotation decay on sand

        

    def reset_car(self):
        self.position = (22, 90, 0)
        self.speed = Vec3(0, 0, 0)
        self.rotation_speed = 0
        self.rotation = (0, 0, 0)
        self.reset_prompt.visible = False

    def reset_attributes(self):
        # Reset car attributes to default values
        self.topspeed = self.default_attributes['topspeed']
        self.acceleration = self.default_attributes['acceleration']
        self.friction = self.default_attributes['friction']
        self.drift_speed = self.default_attributes['drift_speed']
        self.rotation_decay = self.default_attributes['rotation_decay']


# Create start menu
start_menu = StartMenu()
start_menu.parent = scene  # Add the start menu to the scene graph

# Create car simulation scene
car_simulation = Entity(enabled=False)  # Initially disabled until the game starts
car_simulation.parent = scene  # Add the car simulation to the scene graph

# Create racetrack entity
racetrack = Entity(model="assets/testtrack.obj", scale=(12, 12, 12), position=(0, -50, 0), rotation=(0, 270, 0), texture="assets/testtrack.png", collider="mesh")
racetrack.parent = scene  # Add the racetrack to the scene graph

# Create box outline
left_wall = Entity(model='cube', visible=False, scale=(0.1, 2, 40), position=(-1.2, -47, 17.5))
bottom_wall = Entity(model='cube', visible=False, scale=(77, 2, 0.1), position=(-18.6, -47, 17))
top_wall = Entity(model='cube', visible=False, scale=(18.93, 2, 29.8), position=(7.1, -47, 23.8))
right_wall = Entity(model='cube', visible=False, scale=(0.1, 2, 39.7), position=(15.65, -47, 2.65))

# Initialize car
car = Car()

# Initialize camera position and rotation
camera.position = (0, 50, 0)
camera.rotation = (0, 0, 0)

# Function to update camera position
def update_camera():
    # Update only the horizontal position of the camera
    camera.position.y = 50  # Set the y position of the camera to a fixed value
    camera.look_at(car.position)  # Make camera look at the car

# Create Text objects to display car and camera position
car_position_text = Text(text='', origin=(0, 0), y=0.45)
camera_position_text = Text(text='', origin=(0, 0), y=-0.45)

def update():
    # Update car movement
    car.update()

    # Update camera position
    update_camera()

    # Update car and camera position text
    car_position_text.text = f"Car Position: {car.position}"
    camera_position_text.text = f"Camera Position: {camera.position}"

# Prompt to reset car
car.reset_prompt = Text(text='Press R to reset car', position=(-0.2, 0.2), color=color.red, scale=2, background=False, visible=False)

def input(key):
    if key == 'r':
        car.reset_car()
    elif key == 'left mouse down':
        start_menu.start_game()

# Run the app
app.run()