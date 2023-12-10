from inky.auto import auto
from inky import InkyMockWHAT
from PIL import Image, ImageDraw
import pygame


def SurfaceToInky(surface):
    try:
        inky_display = auto(ask_user=False, verbose=True)
        inky_display.set_border(inky_display.WHITE)
    except Exception:
        print("No Inky found - falling back to PC support")
        inky_display = InkyMockWHAT("red")

    inky_display.set_border(inky_display.WHITE)

    WIDTH = inky_display.width
    HEIGHT = inky_display.height

    # Draw our surface onto a PIL image and convert the colours accordingly
    img = Image.new("P", (WIDTH, HEIGHT))
    ImageDraw.Draw(img)
    pil_string_image = pygame.image.tostring(surface, "RGBA", False)
    im = Image.frombytes("RGBA", (400, 300), pil_string_image)
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)
    img = im.convert("RGB").quantize(palette=pal_img)

    # And finally update the inky display
    inky_display.set_image(img)
    inky_display.show()
