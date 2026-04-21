import os

# Stop pygame from printing unnecessary welcome message to terminal
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from PIL import Image
from pathlib import Path
import tkinter
from tkinter import filedialog

# Constants
GRID_WIDTH = 64     # Grid elements (per column)
GRID_HEIGHT = 64    # Grid elements (per row)
PIXEL_SIZE = 8      # Pixels per grid element

SIDEBAR_WIDTH = 120                 # Width of sidebar
CANVAS_OFFSET_X = SIDEBAR_WIDTH     # Canvas starts after sidebar
CANVAS_OFFSET_Y = 0

WINDOW_WIDTH = SIDEBAR_WIDTH + GRID_WIDTH * PIXEL_SIZE      # Actual window width
WINDOW_HEIGHT = GRID_HEIGHT * PIXEL_SIZE                    # Actual window height

BACKGROUND_COLOR = (0, 0, 0)                                # Black
GRID_LINE_COLOR = (40, 40, 40)                              # Grey
DEFAULT_DRAW_COLOR = (255, 255, 255)                        # White

BUTTON_HEIGHT = 40                                          # Size of button
BUTTON_PADDING = 10                                         # Padding between buttons

# Number of frames created
frame_count = 0

# Save directory
chosen_directory = None

def draw_canvas(surface: pygame.Surface, canvas: list[list[tuple[int, int, int]]]):
    """
    Draw every pixel from the canvas onto the screen

    :param surface: Pygame surface that will be drawn on
    :param canvas: Canvas with color info
    :return: Nothing
    """

    for row in range(GRID_HEIGHT):

        for col in range(GRID_WIDTH):

            pixel_color = canvas[row][col]

            screen_x = CANVAS_OFFSET_X + col * PIXEL_SIZE
            screen_y = CANVAS_OFFSET_Y + row * PIXEL_SIZE

            rect = pygame.Rect(
                screen_x, screen_y, PIXEL_SIZE, PIXEL_SIZE
            )

            pygame.draw.rect(surface, pixel_color, rect)

def draw_grid_lines(surface: pygame.Surface):
    """
    Draw grid lines onto surface

    :param surface: Pygame surface that will be drawn on
    :return: Nothing
    """

    # Vertical lines
    for col in range(GRID_WIDTH + 1):
        screen_x = CANVAS_OFFSET_X + col * PIXEL_SIZE
        pygame.draw.line(surface, GRID_LINE_COLOR, (screen_x, 0), (screen_x, WINDOW_HEIGHT))

    # Horizontal lines
    for row in range(GRID_HEIGHT + 1):
        screen_y = CANVAS_OFFSET_Y + row * PIXEL_SIZE
        pygame.draw.line(surface, GRID_LINE_COLOR, (CANVAS_OFFSET_X, screen_y), (WINDOW_WIDTH, screen_y))

def handle_mouse_drawing(canvas: list[list[tuple[int, int, int]]], drawing_color: tuple[int, int, int]):
    """
    If mouse is pressed, draw on canvas

    :return:Nothing
    """

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Convert screen coordinates to grid coordinates
    grid_x = (mouse_x - CANVAS_OFFSET_X) // PIXEL_SIZE
    grid_y = (mouse_y - CANVAS_OFFSET_Y) // PIXEL_SIZE

    # If we are within canvas, draw
    if (0 <= grid_x < GRID_WIDTH) and (0 <= grid_y < GRID_HEIGHT):
        canvas[grid_y][grid_x] = drawing_color

def draw_sidebar(surface: pygame.Surface):
    rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(surface, (30, 30, 30), rect)

def handle_sidebar_click(mouse_pos: tuple[int, int], buttons:  dict[str, pygame.Rect | str],
                         canvas: list[list[tuple[int, int, int]]]):
    x, y = mouse_pos
    global frame_count, chosen_directory

    for name, rect in buttons.items():
        if rect.collidepoint(x, y):
            if name == "clear":
                clear_canvas(canvas)
            elif name == "save":

                # Ask for directory, if none available
                if chosen_directory is None:
                    selected = choose_directory()

                    if not selected: # User cancelled
                        return

                    chosen_directory = Path(selected) / "frame_data"

                    chosen_directory.mkdir(parents=True, exist_ok=True)

                filename = chosen_directory / f"frame_{frame_count}.png"
                save_drawing(canvas, str(filename))
                frame_count += 1

def handle_mouse_click(mouse_pos: tuple[int, int], buttons: dict[str, pygame.Rect | str],
                       canvas: list[list[tuple[int, int, int]]], current_color: tuple[int, int, int]):

    x, y = mouse_pos

    # Clicked on sidebar
    if x < SIDEBAR_WIDTH:
        return handle_sidebar_click(mouse_pos, buttons, canvas)

    # Clicked on canvas
    else:
        handle_mouse_drawing(canvas, current_color)

def draw_buttons(surface: pygame.Surface, buttons:  dict[str, pygame.Rect | str]):
    font = pygame.font.SysFont(None, 24)

    for name, rect in buttons.items():
        pygame.draw.rect(surface, (80, 80, 80), rect)
        pygame.draw.rect(surface, (200, 200, 200), rect, 2)

        text = font.render(name.upper(), True, (255, 255, 255))
        text_rec = text.get_rect(center=rect.center)
        surface.blit(text, text_rec)


def clear_canvas(canvas: list[list[tuple[int, int, int]]]):
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            canvas[row][col] = BACKGROUND_COLOR

def handle_keyboard_press(event: pygame.event.Event, current_drawing_color: tuple[int, int, int], canvas: list[list[tuple[int, int, int]]]) -> tuple[int, int, int]:
    """
    Handle keyboard shortcut for colors

    :param event: Keyboard shortcut event
    :param current_drawing_color: Color currently being used in drawing
    :return: New color, if a new one is chosen. Otherwise, old color
    """

    if event.key == pygame.K_0:
        return DEFAULT_DRAW_COLOR

    elif event.key == pygame.K_1:
        return (255, 0, 0)

    elif event.key == pygame.K_2:
        return (0, 255, 0)

    elif event.key == pygame.K_3:
        return (0, 0, 255)

    elif event.key == pygame.K_e:
        return BACKGROUND_COLOR

    elif event.key == pygame.K_c:
        clear_canvas(canvas)
        return current_drawing_color

    else:
        return current_drawing_color


def save_drawing(canvas: list[list[tuple[int, int, int]]], filename: str):

    # Create image
    img = Image.new("RGB", (GRID_WIDTH, GRID_HEIGHT))

    # Flatten 2D canvas to 1D set of pixels
    pixels = []

    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):

            pixels.append(canvas[row][col])

    # Put pixels in image
    img.putdata(pixels)

    # Save image
    img.save(filename)

def choose_directory():
    root = tkinter.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    root.destroy()
    return directory

def main():

    # Initialize variables and game module
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Drawing Window")
    clock = pygame.time.Clock()  # Helps track time

    # Canvas is a 2D list
    # Canvas[row][col] gives color of pixel
    canvas = []

    # Fill out canvas with background color
    for row_index in range(GRID_HEIGHT):
        row = []
        for col_index in range(GRID_WIDTH):
            row.append(BACKGROUND_COLOR)
        canvas.append(row)

    buttons = {
        "clear": pygame.Rect(10, 20, SIDEBAR_WIDTH - 20, BUTTON_HEIGHT),
        "save": pygame.Rect(10, 80, SIDEBAR_WIDTH - 20, BUTTON_HEIGHT)
    }


    running = True

    current_drawing_color = DEFAULT_DRAW_COLOR

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                current_drawing_color = handle_keyboard_press(event, current_drawing_color, canvas)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                handle_mouse_click(mouse_pos, buttons, canvas, current_drawing_color)

        # Handle dragging
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pressed and (mouse_pos[0] >= SIDEBAR_WIDTH):
            handle_mouse_drawing(canvas, current_drawing_color)

        # Refresh screen
        screen.fill(BACKGROUND_COLOR)

        # Draw sidebar and buttons
        draw_sidebar(screen)
        draw_buttons(screen, buttons)

        # Redraw canvas value and grid lines
        draw_canvas(screen, canvas)
        draw_grid_lines(screen)

        # Update display
        pygame.display.flip()

        # Limit to 60 fps
        clock.tick(60)

    pygame.quit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

