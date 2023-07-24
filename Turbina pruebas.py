import pygame
import math
import colorsys

# Dimensiones de la ventana y constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAVITY = 0.1
WATER_SPEED = 2
WATER_RADIUS = 1
TURBINE_RADIUS = 80
TURBINE_BLADES = 10
BLADE_DENSITY = 2.5
WATER_SOURCE_RATE = 1  # Velocidad de creación de partículas de agua por iteración

# Colores
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class WaterParticle:
    def __init__(self, x, y, density):
        self.x = x
        self.y = y
        self.vx = WATER_SPEED
        self.vy = 0
        self.density = density
        self.radius = WATER_RADIUS


def draw_turbine(screen, x, y, angle):
    blade_length = TURBINE_RADIUS
    for i in range(TURBINE_BLADES):
        blade_angle = math.radians(angle + i * 360 / TURBINE_BLADES)
        blade_end_x = x + blade_length * math.cos(blade_angle)
        blade_end_y = y - blade_length * math.sin(blade_angle)
        pygame.draw.line(screen, GREEN, (x, y), (blade_end_x, blade_end_y), 8)

class Barra:
    def __init__(self, x1, y1, x2, y2, width):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width

    def draw(self, screen):
        pygame.draw.line(screen, GRAY, (self.x1, self.y1), (self.x2, self.y2), self.width)

    def collision_check(self, particle):
        # Verificar si la partícula colisiona con la línea de la barra y obtener el grosor de la barra
        thickness = 10  # Ancho de la barra (grosor)
        x_diff = self.x2 - self.x1
        y_diff = self.y2 - self.y1

        if x_diff != 0:
            slope = y_diff / x_diff
            intercept = self.y1 - slope * self.x1
            closest_y = slope * particle.x + intercept
            distance = abs(particle.y - closest_y)

            if distance <= thickness / 2 and self.x1 <= particle.x <= self.x2:
                # La partícula colisiona con la barra, ajustar el movimiento
                particle.y = closest_y + (thickness / 2) * (-1 if y_diff > 0 else 1)
                particle.vx += particle.vx * 0.1  # Añadir velocidad horizontal al resbalar
                particle.vy = 0
                
        # Verificar colisión horizontal
        thickness = 10  # Ancho de la barra (grosor)
        x_diff = self.x2 - self.x1
        y_diff = self.y2 - self.y1

        if y_diff != 0:
            slope_inv = x_diff / y_diff
            intercept_inv = self.x1 - slope_inv * self.y1
            closest_x = slope_inv * particle.y + intercept_inv
            distance_inv = abs(particle.x - closest_x)

            if distance_inv <= thickness / 2 and self.y1 <= particle.y <= self.y2:
                # La partícula colisiona horizontalmente con la barra, ajustar el movimiento
                particle.x = closest_x + (thickness / 2) * (-1 if x_diff > 0 else 1)
                particle.vx = 0


def calculate_collision_force(particle, blade_end_x, blade_end_y, blade_density):
    dx = particle.x - blade_end_x
    dy = particle.y - blade_end_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Verificar si la partícula está dentro del área ocupada por el aspa
    blade_length = TURBINE_RADIUS * 2
    if distance < blade_length:
        normal_x = dx / distance
        normal_y = dy / distance

        relative_velocity_x = particle.vx
        relative_velocity_y = particle.vy

        relative_speed = relative_velocity_x * normal_x + relative_velocity_y * normal_y

        if relative_speed > 0:
            return 0, 0  # Las partículas solo colisionarán cuando se acercan a las aspas

        e = 0  # Coeficiente de restitución (0 para colisiones perfectamente elásticas, 1 para colisiones perfectamente inelásticas)
        j = -(1 + e) * relative_speed
        j /= (1 / (particle.density + blade_density))

        impulse_x = j * normal_x
        impulse_y = j * normal_y

        return impulse_x, impulse_y

    return 0, 0  # No hay colisión

def particle_collision_check(particles):
    for i, particle1 in enumerate(particles):
        for j, particle2 in enumerate(particles):
            if i != j:
                dx = particle2.x - particle1.x
                dy = particle2.y - particle1.y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if dx == 0 or dy == 0:
                    break

                if distance < particle1.radius + particle2.radius:
                    # Las partículas colisionan
                    if dy < 0:  # Verifica si la colisión ocurre en el eje y (hacia arriba)
                        normal_y = -1
                    elif dy > 0:  # Verifica si la colisión ocurre en el eje y (hacia abajo)
                        normal_y = 1
                    else:
                        normal_y = 0

                    relative_velocity_y = particle2.vy - particle1.vy

                    if relative_velocity_y > 0:
                        # Coeficiente de restitución para simular una colisión suave
                        restitution = 0
                        impulse = (1 + restitution) * relative_velocity_y / (particle1.density + particle2.density)

                        impulse_y = impulse * normal_y

                        particle1.vy -= impulse_y / particle1.density
                        particle2.vy += impulse_y / particle2.density


def draw_text(screen, text, x, y, font, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Agregar una función para obtener el color en función del tiempo o iteración
def get_title_color(counter):
    hue = (counter % 360) / 360.0  # Obtener el valor del matiz entre 0 y 1
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulación de Turbina de Agua")

    # Crear la fuente para el texto
    font = pygame.font.Font(None, 30)  # Puedes cambiar el tamaño y el tipo de letra aquí

    # Variables para controlar el cambio de color del título
    color_change_speed = 50  # Velocidad de cambio de color (ajusta según lo desees)
    color_counter = 0


    particles = []  # Lista de partículas de agua
    
    # Variables para controlar la fuente de partículas
    generating_particles = False
    particle_sources = []  # Lista para almacenar las posiciones de las fuentes de partículas
    particles_inside_screen = []  # Lista para almacenar las partículas dentro de la pantalla


    # Posición y ángulo inicial de la turbina
    turbine_x, turbine_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    turbine_angle = 0
    turbine_v = 0  # Velocidad angular inicial
    turbine_max_v = 10.0  # Velocidad angular máxima de la turbina
    turbine_acceleration = 0.1  # Ajusta la aceleración de la turbina aquí
    turbine_deceleration = 0.05  # Ajusta la desaceleración de la turbina aquí


    clock = pygame.time.Clock()

    # Crea las barras en pantalla
    barra1 = Barra(100, 100, 300, 200, 5)
    barra2 = Barra(0, 0, 0, 600, 20)
    barra3 = Barra(0, 0, 800, 0, 20)
    barra4 = Barra(800, 0, 800, 600, 20)
    barra5 = Barra(0, 600, 800, 600, 20)
    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:  # Botón izquierdo del mouse oprimido
                # Generar partícula de agua en las coordenadas del mouse
                water_density = 1.0  # Ajusta la densidad de las partículas de agua aquí
                particles.append(WaterParticle(*event.pos, water_density))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Agregar la posición actual del mouse a las fuentes de partículas
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    particle_sources.append((mouse_x, mouse_y))
                    generating_particles = True
                elif event.key == pygame.K_r:
                    # Eliminar todas las partículas de agua al presionar "R"
                    particles.clear()
                    particle_sources.clear()
        if generating_particles:
            # Generar partículas en todas las fuentes registradas
            for source_x, source_y in particle_sources:
                water_density = 1.0  # Ajusta la densidad de las partículas de agua aquí
                particles.append(WaterParticle(source_x, source_y, water_density))

        # Variables para controlar si hay colisión entre las partículas y la turbina
        is_colliding = False
        
        # Lista para almacenar las partículas que siguen dentro de la pantalla
        particles_inside_screen = []

        particle_collision_check(particles)  # Verifica colisiones entre las partículas


        for particle in particles:
            # Movimiento del agua
            particle.vy += GRAVITY
            particle.x += particle.vx
            particle.y += particle.vy

            # Restringe la posición dentro de la pantalla
            particle.x = max(particle.x, 1)
            particle.x = min(particle.x, SCREEN_WIDTH)
            particle.y = max(particle.y, 1)
            particle.y = min(particle.y, SCREEN_HEIGHT)

            # Verificar colisión con las aspas de la turbina
            for i in range(TURBINE_BLADES):
                blade_angle = math.radians(turbine_angle + i * 360 / TURBINE_BLADES)
                blade_end_x = turbine_x + TURBINE_RADIUS * math.cos(blade_angle)
                blade_end_y = turbine_y - TURBINE_RADIUS * math.sin(blade_angle)

            blade_length = TURBINE_RADIUS * 2
            if math.dist((particle.x, particle.y), (blade_end_x, blade_end_y)) < blade_length:
                impulse_x, impulse_y = calculate_collision_force(particle, blade_end_x, blade_end_y, BLADE_DENSITY)
                particle.vx += impulse_x
                particle.vy += impulse_y

                # Actualizar la variable is_colliding
                if impulse_x != 0 or impulse_y != 0:
                    is_colliding = True

            # Verificar colisión con las barras
            barra1.collision_check(particle)
            barra2.collision_check(particle)
            barra3.collision_check(particle)
            barra4.collision_check(particle)
            barra5.collision_check(particle)
            
            # Verificar si la partícula sigue dentro de la pantalla
            if 0 <= particle.x <= SCREEN_WIDTH and 0 <= particle.y <= SCREEN_HEIGHT:
                particles_inside_screen.append(particle)
        
        # Reemplazar la lista original por la lista filtrada de partículas dentro de la pantalla
        particles = particles_inside_screen

        # Aceleración y desaceleración de la turbina
        if is_colliding:
            if turbine_v < turbine_max_v:
                turbine_v += turbine_acceleration
        else:
            if turbine_v > 0:
                turbine_v -= turbine_deceleration

        # Actualiza el ángulo de la turbina
        turbine_angle += turbine_v

        # Límite superior de la turbina
        if turbine_angle >= 360:
            turbine_angle = 0

        screen.fill(WHITE)

        # Dibuja las partículas de agua
        for particle in particles:
            pygame.draw.circle(screen, BLUE, (int(particle.x), int(particle.y)), 5)

        # Dibuja la turbina
        draw_turbine(screen, turbine_x, turbine_y, turbine_angle)
        
        # Dibuja las barras en pantalla
        barra1.draw(screen)
        barra2.draw(screen)
        barra3.draw(screen)
        barra4.draw(screen)
        barra5.draw(screen)
        
        # Obtén el color del título en función del contador
        title_color = get_title_color(color_counter)

        # Agregar leyenda en la parte superior izquierda de la pantalla
        draw_text(screen, "Click para generar agua.", 20, 20, font, BLACK)
        draw_text(screen, "F para colocar una fuente de agua.", 20, 42, font, BLACK)
        draw_text(screen, "Presiona R para borrar todas las partículas y fuentes.", 20, 64, font, BLACK)
        draw_text(screen, "Simulación de Turbina de Agua", 20, SCREEN_HEIGHT - 40, font, title_color)
        
        # Actualizar el contador de cambio de color
        color_counter = (color_counter + 1) % (360 * color_change_speed)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
