import pygame
import random
import heapq

# Inisialisasi Pygame
pygame.init()

# Screen Settings
WIDTH = 640
HEIGHT = 480
GRID_SIZE = 20
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Autonomous Snake AI')

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Font
FONT = pygame.font.SysFont('Arial', 18)

class SnakeAI:
    def __init__(self):
        """
        Initialize the SnakeAI object with default starting values.

        Attributes:
            position (list): A list containing the initial position of the snake's head as a Vector2 object.
            direction (Vector2): The initial direction of the snake's movement.
            length (int): The initial length of the snake.
            food (tuple or None): The position of the food on the grid, initialized to None.
            score (int): The initial score of the game.
        """
        self.position = [
            pygame.math.Vector2(5 * GRID_SIZE, 5 * GRID_SIZE)
        ]
        self.direction = pygame.math.Vector2(1, 0)
        self.length = 1
        self.food = None
        self.generate_food()
        self.score = 0

    def generate_food(self):
        """
        Generate a new food position on the grid.

        This method generates a new random position for the food on the grid, 
        ensuring that the new position is not occupied by the snake.
        """
        while True:
            x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
            new_food = (x, y)
            
            if new_food not in [(pos.x, pos.y) for pos in self.position]:
                self.food = new_food
                break

    def heuristic(self, a, b):
        """
        Calculate the Manhattan distance between two points.

        This heuristic function is used to estimate the cost from the current 
        point 'a' to the target point 'b'. It is primarily used in pathfinding 
        algorithms like A* to provide a quick estimate of the remaining 
        distance to the goal.

        Args:
            a (tuple): The current point as a tuple (x, y).
            b (tuple): The target point as a tuple (x, y).

        Returns:
            int: The Manhattan distance between points 'a' and 'b'.
        """

        return abs(b[0] - a[0]) + abs(b[1] - a[1])

    def astar(self, start, end):
        """
        Finds the shortest path from start to end using the A* algorithm.

        This algorithm is used to find the shortest path from the current position of the snake's head to the position of the food. The A* algorithm is a pathfinding algorithm that uses a heuristic to guide the search. The heuristic used in this implementation is the Manhattan distance.

        Args:
            start (tuple): The starting point as a tuple (x, y).
            end (tuple): The target point as a tuple (x, y).

        Returns:
            list or None: A list of tuples representing the shortest path from start to end, or None if no path is found.
        """
        open_list = []
        heapq.heappush(open_list, (self.heuristic(start, end), start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while open_list:
            _, current = heapq.heappop(open_list)
            if current == end:
                break

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                next = (current[0] + dx * GRID_SIZE, current[1] + dy * GRID_SIZE)
                if (next[0] < 0 or next[0] >= WIDTH or 
                    next[1] < 0 or next[1] >= HEIGHT or 
                    next in [(pos.x, pos.y) for pos in self.position]):
                    continue

                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, end)
                    heapq.heappush(open_list, (priority, next))
                    came_from[next] = current

        if end not in came_from:
            return None

        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    def move(self):
        """
        Move the snake to the next position in the path.

        This method uses the A* algorithm to find the shortest path from the current position of the snake's head to the position of the food. The path is then followed by moving the snake one step in the direction of the next position in the path.

        If the snake eats the food, the length of the snake is increased by one and the score is incremented by one. A new piece of food is then generated at a random position on the grid.
        """
        start = (self.position[0].x, self.position[0].y)
        path = self.astar(start, self.food)
        if path is None or len(path) < 2:
            return

        next_pos = path[1]
        self.direction = pygame.math.Vector2(next_pos[0] - start[0], next_pos[1] - start[1]).normalize()
        self.position.insert(0, pygame.math.Vector2(next_pos))

        if next_pos == self.food:
            self.length += 1
            self.score += 1
            self.generate_food()
        else:
            self.position.pop()

    def draw(self, screen):
        """
        Draw the snake and the food on the screen.

        This method draws each segment of the snake as a green rectangle and the food as a red rectangle.

        Args:
            screen (Surface): The surface to draw on.
        """

        for segment in self.position:
            pygame.draw.rect(screen, GREEN, 
                             (segment.x, segment.y, GRID_SIZE, GRID_SIZE))
        
        # Draw food
        pygame.draw.rect(screen, RED, 
                         (self.food[0], self.food[1], GRID_SIZE, GRID_SIZE))

    def check_collision(self):
        """
        Check for collision with the wall or itself.

        This method checks if the head of the snake is colliding with the wall or with any other segment of the snake.

        Returns:
            bool: True if a collision is detected, False otherwise.
        """
        head = self.position[0]
        
        # Collision with wall
        if (head.x < 0 or head.x >= WIDTH or 
            head.y < 0 or head.y >= HEIGHT):
            return True
        
        # Collision with itself
        if head in self.position[1:]:
            return True
        
        return False


def main():
    """
    Main game loop for the SnakeAI game.

    This function initializes the game and runs the main game loop. 
    It handles events, moves the snake, checks for collisions, updates 
    the display, and controls the game speed. The loop continues until 
    a quit event is detected or a collision occurs. The score is displayed 
    on the screen.

    The game is terminated when the game_over condition is met.
    """

    clock = pygame.time.Clock()
    snake = SnakeAI()
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # Move snake
        snake.move()

        # Check collision
        if snake.check_collision():
            game_over = True

        # Clean screen
        SCREEN.fill(BLACK)

        # Draw snake and food
        snake.draw(SCREEN)

        # Draw score
        text = FONT.render("Score: " + str(snake.score), True, WHITE)
        SCREEN.blit(text, (10, 10))

        # Update screen
        pygame.display.flip()

        # Control speed
        clock.tick(10)  # 10 frames per second

    pygame.quit()

if __name__ == "__main__":
    main()

