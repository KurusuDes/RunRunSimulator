from PIL import Image, ImageDraw
import math
SRC="C:/Users/Docente/Desktop/UnityProyects/RunRunSimulator/Assets/RunRunSimulator/Resources/Textures/MoriMochi/Faces/"
S=4; INK=(0,0,0,255); WH=(255,255,255,255)
EYES=[(121,256,1),(391,256,-1)]
def blush():
    im=Image.open(SRC+'MonchiFace_07.png').convert('RGBA'); px=im.load()
    for y in range(512):
        for x in range(512):
            if y<292: px[x,y]=(0,0,0,0)
    return im
class C:
    def __init__(s): s.im=Image.new('RGBA',(512*S,512*S),(0,0,0,0)); s.d=ImageDraw.Draw(s.im)
    def circ(s,x,y,r,c=INK): s.d.ellipse([(x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S],fill=c)
    def ell(s,x,y,rx,ry,c=INK): s.d.ellipse([(x-rx)*S,(y-ry)*S,(x+rx)*S,(y+ry)*S],fill=c)
    def line(s,p,q,w,c=INK):
        s.d.line([(p[0]*S,p[1]*S),(q[0]*S,q[1]*S)],fill=c,width=int(w*S))
        for a in (p,q): s.circ(a[0],a[1],w/2,c)
    def rect(s,x0,y0,x1,y1,c=(0,0,0,0)): s.d.rectangle([x0*S,y0*S,x1*S,y1*S],fill=c)
    def done(s):
        b=blush(); b.alpha_composite(s.im.resize((512,512),Image.LANCZOS)); return b
def eye(c,x,y,r=32):
    c.circ(x,y,r); c.circ(x+r*0.3,y-r*0.3,r*0.34,WH)
def original(c):
    return Image.open(SRC+'MonchiFace_07.png').convert('RGBA')
def tuerto(c):
    x,y,_=EYES[0]; r=24; c.line((x-r,y-r),(x+r,y+r),13); c.line((x-r,y+r),(x+r,y-r),13)
    eye(c,*EYES[1][:2]); return c.done()
def puntitos(c):
    for x,y,_ in EYES: c.circ(x,y+6,13); c.circ(x+4,y+2,4,WH)
    return c.done()
def pestanas(c):
    for x,y,sd in EYES:
        eye(c,x,y)
        for i,a in enumerate((-150,-125,-100) if sd>0 else (-30,-55,-80)):
            ra=math.radians(a); p=(x+math.cos(ra)*30,y+math.sin(ra)*30); q=(x+math.cos(ra)*46,y+math.sin(ra)*46)
            c.line(p,q,6)
    return c.done()
def brillitos(c):
    for x,y,_ in EYES:
        c.circ(x,y,38); c.circ(x+12,y-12,13,WH); c.circ(x-12,y+14,6,WH); c.circ(x+16,y+14,3,WH)
    return c.done()
def somnoliento(c):
    for x,y,_ in EYES:
        eye(c,x,y+4); c.rect(x-40,y-40,x+40,y-4); c.line((x-36,y-4),(x+36,y-4),8)
    return c.done()
def cejudo(c):
    for x,y,sd in EYES:
        eye(c,x,y)
        c.line((x-26,y-50),(x+26,y-50),13)
    return c.done()
def ovalados(c):
    for x,y,_ in EYES: c.ell(x,y,18,32); c.ell(x+5,y-14,7,9,WH)
    return c.done()
def sonriente(c):
    for x,y,_ in EYES:
        c.d.arc([(x-26)*S,(y-18)*S,(x+26)*S,(y+34)*S],200,340,fill=INK,width=10*S)
    return c.done()
STY=[('Original',original),('Tuerto A',tuerto),('Puntitos',puntitos),('Pestanas',pestanas),('Brillitos',brillitos),('Somnoliento',somnoliento),('Cejudo',cejudo),('Ovalados',ovalados)]
for i,(n,f) in enumerate(STY): f(C()).save(f'style_{i}.png')
print(len(STY))
