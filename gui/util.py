import numpy as np


def lighten_hex_color(hex_color, factor=0.2):
    # Convert hex color to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Lighten each RGB value
    lighter_rgb = tuple(min(int(value * (1 + factor)), 255) for value in rgb)
    
    # Convert back to hex
    lighter_hex = '#{:02x}{:02x}{:02x}'.format(*lighter_rgb)
    
    return lighter_hex


def generate_alternating_gradient(color1,color2,n=100):
    # Calculate the stops for the gradient
    stops = []
    for i in np.arange(0, n, .8):
        stops.append(f"stop: {i / n} {color1}")
        if ((i + 1) / n) <= 1:
            stops.append(f"stop: {(i + 1) / n} {color2}")

    # Join the stops into a gradient string
    gradient_str = "qlineargradient(x1:0, y1:0, x2:1, y2:1, " + " ".join(stops) + ")"
    return gradient_str