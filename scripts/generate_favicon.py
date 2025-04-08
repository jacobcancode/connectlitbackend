from PIL import Image, ImageDraw
import os

# Create a 32x32 image with a transparent background
img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a simple book icon
# Book cover
draw.rectangle([4, 4, 28, 28], outline=(0, 0, 0), fill=(255, 255, 255))
# Book spine
draw.rectangle([4, 4, 8, 28], fill=(200, 200, 200))
# Book pages
for i in range(6, 28, 4):
    draw.line([8, i, 28, i], fill=(200, 200, 200))

# Save the image
os.makedirs('static', exist_ok=True)
img.save('static/favicon.ico', format='ICO', sizes=[(32, 32)]) 