from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from signal import pause
from time import sleep
import json

# --- Initialize display ---
serial = i2c(port=1, address=0x3C)
device = sh1106(serial, width=128, height=64)

# --- Canvas size ---
CANVAS_WIDTH = 125
CANVAS_HEIGHT = 64

# --- Font ---
font = ImageFont.load_default()

# --- Button setup ---
BUTTON_PIN = 26  # BCM numbering
button = Button(BUTTON_PIN, pull_up=True)

# --- Example static transit data ---
subway_line = "1"
subway_times = "--"
bus_line = "M104"
bus_times = "--"

# --- Spacing constants ---
TOP_PADDING = 4
ARRIVAL_PADDING = 10
BUS_RECT_W = 30
BUS_RECT_H = 12
BUS_LEFT_PADDING = 2
BUS_RIGHT_PADDING = 1
CIRCLE_RADIUS = 6

# --- State variable for direction ---
direction_state = ["UPTOWN", "DOWNTOWN"]
current_index = 1

def draw_transit(direction):
    """Draw the full display for the given direction ('UPTOWN' or 'DOWNTOWN')"""
    image = Image.new("1", (CANVAS_WIDTH, CANVAS_HEIGHT), "black")
    draw = ImageDraw.Draw(image)

    # --- Top line: direction ---
    bbox_dir = draw.textbbox((0,0), direction, font=font)
    dir_width = bbox_dir[2] - bbox_dir[0]
    draw.text(((CANVAS_WIDTH - dir_width)//2, TOP_PADDING), direction, font=font, fill=255)

    # --- Subway line ---
    subway_y = TOP_PADDING + 16
    circle_x = 10 + CIRCLE_RADIUS
    circle_y = subway_y + CIRCLE_RADIUS
    draw.ellipse((circle_x - CIRCLE_RADIUS, circle_y - CIRCLE_RADIUS,
                  circle_x + CIRCLE_RADIUS, circle_y + CIRCLE_RADIUS), outline=255, fill=255)
    sub_text_bbox = draw.textbbox((0,0), subway_line, font=font)
    sub_text_w = sub_text_bbox[2] - sub_text_bbox[0]
    sub_text_h = sub_text_bbox[3] - sub_text_bbox[1]
    draw.text((circle_x - sub_text_w//2, circle_y - sub_text_h//2), subway_line, font=font, fill=0)
    # draw.text((circle_x + CIRCLE_RADIUS + ARRIVAL_PADDING, subway_y), subway_times, font=font, fill=255)

    # --- Bus line ---
    bus_y = TOP_PADDING + 34
    rect_x0, rect_y0 = 5, bus_y
    rect_x1, rect_y1 = rect_x0 + BUS_RECT_W, rect_y0 + BUS_RECT_H
    draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), outline=255, fill=255)

    bus_bbox = draw.textbbox((0,0), bus_line, font=font)
    bus_w = bus_bbox[2] - bus_bbox[0]
    bus_h = bus_bbox[3] - bus_bbox[1]
    text_x_bus = rect_x0 + BUS_LEFT_PADDING + ((BUS_RECT_W - BUS_LEFT_PADDING - BUS_RIGHT_PADDING - bus_w)//2)
    text_y_bus = rect_y0 + (BUS_RECT_H - bus_h)//2
    draw.text((text_x_bus, text_y_bus), bus_line, font=font, fill=0)

    # --- Fetch new data and display ---
    subway_times, bus_times = get_arrival_strings(direction=direction)

    draw.text((rect_x1 + ARRIVAL_PADDING, bus_y), bus_times, font=font, fill=255)
    draw.text((rect_x1 + ARRIVAL_PADDING, subway_y), subway_times, font=font, fill=255)

    # --- Border ---
    draw.rectangle((0,0,CANVAS_WIDTH-1,CANVAS_HEIGHT-1), outline=255)

    # --- Paste into full 128-wide buffer ---
    full_buffer = Image.new("1", (128, CANVAS_HEIGHT), "black")
    x_offset = (128 - CANVAS_WIDTH)//2
    full_buffer.paste(image, (x_offset, 0))
    device.display(full_buffer)


# --- Button press handler ---
def toggle_direction():
    global current_index
    current_index = 1 - current_index  # toggle between 0 and 1
    draw_transit(direction_state[current_index])

def format_times(times):
    """Return up to two times joined with & and a single 'min' at the end."""
    times = times[:2]  # take at most 2
    if not times:
        return "--"
    return " & ".join(str(t) for t in times) + " min"

def get_arrival_strings(subway_file="subway_data.json", bus_file="bus_data.json", direction="UPTOWN"):
    """Return formatted arrival strings for subway and bus for a given direction."""
    subway_times = "--"
    bus_times = "--"

    # Load subway times
    try:
        with open(subway_file) as f:
            data = json.load(f)
            times = data.get("subway", {}).get(direction, [])
            subway_times = format_times(times)
    except FileNotFoundError:
        pass

    # Load bus times
    try:
        with open(bus_file) as f:
            data = json.load(f)
            times = data.get("bus", {}).get(direction, [])
            bus_times = format_times(times)
    except FileNotFoundError:
        pass

    return subway_times, bus_times

if __name__ == "__main__":
    # Attach button
    button.when_pressed = toggle_direction

    while True:
        draw_transit(direction_state[current_index])
        sleep(30)

