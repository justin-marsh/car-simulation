from ursina import *

app = Ursina()

class Car(Entity):
    def __init__(self, position=(22, 90, 0), scale=(0.1, 0.1, 0.1), rotation=(0, 0, 0), topspeed=30, acceleration=0.15, braking_strength=30, friction=0.6, camera_speed=8, drift_speed=35):
        super().__init__(
            model="cube",
            scale=scale,
            color=color.red,
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
            self.topspeed = 30  # Reset topspeed when accelerating
        else:
            # Slow down gradually when 'w' is released
            self.speed -= self.speed * self.friction * time.dt

        rotation_direction = (held_keys['d'] or held_keys['right arrow']) - (held_keys['a'] or held_keys['left arrow'])

        # Update rotation speed regardless of drifting
        self.rotation_speed += rotation_direction * self.drift_speed * time.dt

        # Check if the car is drifting
        if abs(rotation_direction) > 0 and self.speed.length() > self.topspeed * 0.9:
            self.is_drifting = True
        else:
            self.is_drifting = False

        if self.is_drifting:
            self.rotation_speed += rotation_direction * self.drift_speed * time.dt

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
racetrack = Entity(model="testtrack.obj", scale=(12, 12, 12), position=(0, -50, 0), texture="white_cube", collider="mesh")

# Initialize car
car = Car()

# Initialize camera position and rotation
camera.position = (22, 100, 0)
camera.rotation = (0, 0, 0)

# Create dot to represent camera position
camera_dot = Entity(model='quad', scale=0.1, color=color.green)

# Function to update camera position and move the camera with WASD keys
def update_camera():
    global camera_dot
    camera_dot.position = camera.position
    camera_movement = Vec3(0, 0, 0)
    if held_keys['w'] or held_keys['up arrow']:
        camera_movement.z += 1
    if held_keys['s'] or held_keys['down arrow']:
        camera_movement.z -= 1
    if held_keys['a'] or held_keys['left arrow']:
        camera_movement.x -= 1
    if held_keys['d'] or held_keys['right arrow']:
        camera_movement.x += 1
    camera.position += camera_movement.normalized() * car.camera_speed * time.dt

# Update function
def update():
    # Update car movement
    car.update()

    # Update camera position
    update_camera()

# Run the app
app.run()
