from ursina import *

app = Ursina()

class Car(Entity):
    def __init__(self, position=(22, 90, 0), scale=(0.3, 0.3, 0.3), rotation=(0, 0, 0), topspeed=5, acceleration=0.05, braking_strength=30, friction=0.9, camera_speed=8, drift_speed=10, rotation_decay=0.5):
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

        # Gravity
        self.velocity_y = 0

        # Rotation parent for smoother rotation
        self.rotation_parent = Entity(parent=self, y=1.4)

    def update(self):
        acceleration = self.acceleration if held_keys['w'] or held_keys['up arrow'] else 0
        deceleration = self.braking_strength if held_keys['s'] or held_keys['down arrow'] else self.friction

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
        self.speed = Vec3(min(max(self.speed[0], -self.topspeed), self.topspeed),
                          self.speed[1],
                          min(max(self.speed[2], -self.topspeed), self.topspeed))

        # Move the car based on the calculated speed
        self.position += self.speed

        # Rotate the car based on the rotation speed
        self.rotation_y += self.rotation_speed * time.dt

        # Collision Detection
        x_movement = self.speed[0]
        x_direction = 1 if x_movement > 0 else -1 if x_movement < 0 else 0
        x_ray = raycast(origin=self.position, direction=(x_direction, 0, 0), ignore=[self])
        if x_ray.hit:
            self.position.x = x_ray.world_point.x - x_direction * (self.scale_x / 2 + 0.01)

        z_movement = self.speed[2]
        z_direction = 1 if z_movement > 0 else -1 if z_movement < 0 else 0
        z_ray = raycast(origin=self.position, direction=(0, 0, z_direction), ignore=[self])
        if z_ray.hit:
            self.position.z = z_ray.world_point.z - z_direction * (self.scale_z / 2 + 0.01)

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
                    self.rotation_parent.look_at(look_at_direction, axis="up")
                    self.rotation_parent.rotation += Vec3(0, self.rotation_y + 180, 0)
                else:
                    self.rotation_parent.rotation = self.rotation

            else:
                # Apply gravity to the car when it's not on the ground
                self.y += y_movement
                self.velocity_y -= 50 * time.dt
                self.rotation_parent.rotation = self.rotation
                self.start_fall = True


# Create racetrack entity
racetrack = Entity(model="assets/testtrack.obj", scale=(12, 12, 12), position=(0, -50, 0), rotation=(0, 270, 0), texture="assets/testtrack.png", collider="mesh")

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

# Run the app
app.run()
