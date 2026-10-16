from PIL import Image, ImageDraw, ImageFont
import numpy as np, math

FD = '/usr/share/fonts/truetype/'
FONTS = {
    'n': FD + 'liberation/LiberationSans-Regular.ttf',
    'b': FD + 'liberation/LiberationSans-Bold.ttf',
    'i': FD + 'liberation/LiberationSans-Italic.ttf',
    'bi': FD + 'liberation/LiberationSans-BoldItalic.ttf',
    'dj': FD + 'dejavu/DejaVuSans.ttf',
    'djb': FD + 'dejavu/DejaVuSans-Bold.ttf',
}
_cache = {}
def font(style, size):
    k = (style, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FONTS[style], size)
    return _cache[k]

def load(p):
    return Image.open(p).convert('RGB')

def sample(img, x, y, r=3):
    a = np.asarray(img)[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1].reshape(-1, 3)
    return tuple(int(v) for v in np.median(a, axis=0))

def fill(img, box, color=None, from_pt=None):
    d = ImageDraw.Draw(img)
    if color is None:
        color = sample(img, *from_pt)
    d.rectangle(box, fill=color)
    return color

def parse(spec):
    """spec: list of (text, style) where style like 'n','b','i','bi' optionally +'_sub' or '_sup'."""
    return spec

def rich_size(spec, size):
    w = 0; asc = 0
    for text, st in spec:
        st = st.rstrip('^')
        base, pos = (st.split('_') + [''])[:2]
        sz = int(size * 0.68) if pos in ('sub', 'sup') else size
        f = font(base, sz)
        w += f.getlength(text)
    return w

def draw_rich(img, xy, spec, size, color=(0, 0, 0), anchor='l'):
    """Draw rich text; xy = baseline-left (anchor 'l'), centre ('c') or right ('r')."""
    d = ImageDraw.Draw(img)
    w = rich_size(spec, size)
    x, y = xy
    if anchor == 'c':
        x -= w / 2
    elif anchor == 'r':
        x -= w
    for text, st in spec:
        hat = st.endswith('^'); st = st.rstrip('^')
        base, pos = (st.split('_') + [''])[:2]
        if pos == 'sub':
            sz = int(size * 0.68); dy = size * 0.22
        elif pos == 'sup':
            sz = int(size * 0.68); dy = -size * 0.38
        else:
            sz = size; dy = 0
        f = font(base, sz)
        d.text((x, y + dy), text, font=f, fill=color, anchor='ls')
        if hat:
            tw = f.getlength(text); top = y + dy - sz * 0.80
            d.line([(x + tw*0.2, top), (x + tw*0.5, top - sz*0.16), (x + tw*0.8, top)], fill=color, width=max(2, sz//14))
        x += f.getlength(text)
    return w

def T(s, st='n'):
    return [(s, st)]

def arrow(img, p0, p1, color, width=10, head=40, headw=34):
    d = ImageDraw.Draw(img)
    x0, y0 = p0; x1, y1 = p1
    ang = math.atan2(y1 - y0, x1 - x0)
    bx = x1 - head * math.cos(ang); by = y1 - head * math.sin(ang)
    d.line([(x0, y0), (bx, by)], fill=color, width=width)
    px = -math.sin(ang); py = math.cos(ang)
    d.polygon([(x1, y1), (bx + px * headw / 2, by + py * headw / 2), (bx - px * headw / 2, by - py * headw / 2)], fill=color)

def dashed(img, p0, p1, color, width=3, dash=10, gap=7):
    d = ImageDraw.Draw(img)
    x0,y0=p0; x1,y1=p1; L=math.hypot(x1-x0,y1-y0); ux=(x1-x0)/L; uy=(y1-y0)/L
    t=0
    while t < L:
        e=min(L,t+dash); d.line([(x0+ux*t,y0+uy*t),(x0+ux*e,y0+uy*e)],fill=color,width=width); t=e+gap

def tbar(img, p0, p1, color, width=3, half=10, dash=True):
    d = ImageDraw.Draw(img)
    if dash: dashed(img,p0,p1,color,width)
    else: d.line([p0,p1],fill=color,width=width)
    x0,y0=p0; x1,y1=p1; L=math.hypot(x1-x0,y1-y0); ux=(x1-x0)/L; uy=(y1-y0)/L
    d.line([(x1-uy*half,y1+ux*half),(x1+uy*half,y1-ux*half)],fill=color,width=width+1)

def draw_rot(img, center, spec, size, color=(0,0,0), bg=(255,255,255), angle=90):
    w = int(rich_size(spec, size)) + 20; h = int(size * 1.8)
    tile = Image.new('RGB', (w, h), bg)
    draw_rich(tile, (10, int(h * 0.68)), spec, size, color)
    tile = tile.rotate(angle, expand=True)
    img.paste(tile, (int(center[0] - tile.width / 2), int(center[1] - tile.height / 2)))

def rep(img, box, lines, size, color, align='l', sp=None, lh=1.2, pad=2, bg=None):
    """Replace box contents with lines (list of spec lists)."""
    if bg is None:
        sp = sp or (box[0] + 1, box[1] + 1)
        bg = sample(img, *sp, 1)
    ImageDraw.Draw(img).rectangle(box, fill=bg)
    n = len(lines); H = box[3] - box[1]
    total = size * lh * n
    y = box[1] + (H - total) / 2 + size * 0.95
    for spec in lines:
        if align == 'c':
            draw_rich(img, ((box[0] + box[2]) / 2, y), spec, size, color, anchor='c')
        else:
            draw_rich(img, (box[0] + pad, y), spec, size, color)
        y += size * lh
    return bg
