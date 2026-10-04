import sys, os
from PIL import Image, ImageDraw, ImageFont
src, out, step = sys.argv[1], sys.argv[2], int(sys.argv[3])
files = sorted(f for f in os.listdir(src) if f.endswith('.jpg'))
pick = files[::step]
cols = 5
tw, th = 384, 216
rows = (len(pick) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * th))
f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 30)
for i, name in enumerate(pick):
    im = Image.open(os.path.join(src, name)).resize((tw, th))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 90, 34], fill=(0, 0, 0))
    d.text((4, 0), name[2:6], font=f, fill=(255, 255, 0))
    sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
sheet.save(out, quality=85)
