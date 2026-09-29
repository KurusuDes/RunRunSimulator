from PIL import Image, ImageDraw, ImageFont
import sys, os
SRC="C:/Users/Docente/Desktop/UnityProyects/RunRunSimulator/Assets/RunRunSimulator/Resources/Textures/MoriMochi/Faces/"
M=[('Neutral','07'),('Feliz','03'),('Triste','11'),('Triste b','10'),('Dolor','06'),('Enojado','15'),('Enojado b','05'),('Dormido','08'),('Enfermo','13'),('Mareado','14'),('Asustado','24'),('Amoroso','19'),('Emocionado','23'),('KO','18')]
CX,CY=121,256
def draw_x(style):
    S=4; W=512*S
    lay=Image.new('RGBA',(W,W),(0,0,0,0)); d=ImageDraw.Draw(lay)
    ink=(22,14,14,255)
    def line(p,q,w):
        d.line([(p[0]*S,p[1]*S),(q[0]*S,q[1]*S)],fill=ink,width=int(w*S))
        for c in (p,q): d.ellipse([(c[0]-w/2)*S,(c[1]-w/2)*S,(c[0]+w/2)*S,(c[1]+w/2)*S],fill=ink)
    if style=='A':
        r=24; line((CX-r,CY-r),(CX+r,CY+r),13); line((CX-r,CY+r),(CX+r,CY-r),13)
    else:
        r=27; line((CX-r,CY-r+3),(CX+r,CY+r-3),6); line((CX-r+3,CY+r),(CX+r-3,CY-r),6)
        import math
        for sgn in (1,-1):
            for t in (-0.55,0.55):
                px,py=CX+t*r*1, CY+sgn*t*r
                nx,ny=(1/math.sqrt(2),-sgn/math.sqrt(2))
                line((px-nx*8,py-ny*8),(px+nx*8,py+ny*8),4.5)
    return lay.resize((512,512),Image.LANCZOS)
def build(k,style):
    im=Image.open(SRC+f'MonchiFace_{k}.png').convert('RGBA')
    px=im.load()
    brow={'10':216,'05':216}.get(k,0)
    for y in range(165,345):
        for x in range(55,178):
            r,g,b,a=px[x,y]
            if a==0: continue
            blush = y>=290 and r>200 and r-b>60 and g<190
            if blush or y<brow: continue
            px[x,y]=(0,0,0,0)
    im.alpha_composite(draw_x(style))
    return im
def sheet(style,out):
    cw,ch=300,190;cols=5
    sh=Image.new('RGB',(cw*cols,ch*3),(236,196,150)); d=ImageDraw.Draw(sh)
    f=ImageFont.truetype('arial.ttf',16)
    for i,(n,k) in enumerate(M):
        im=build(k,style); im.save(f'tuerto{style}_{k}.png')
        c=im.crop((40,150,472,330)).resize((288,120))
        bg=Image.new('RGBA',c.size,(236,196,150,255)); bg.alpha_composite(c)
        x,y=(i%cols)*cw,(i//cols)*ch
        sh.paste(bg.convert('RGB'),(x+6,y+30)); d.text((x+8,y+6),n,fill=(40,20,10),font=f)
    sh.save(out); return sh
sh=[sheet(s,f'lamina_tuerto{s}.png') for s in sys.argv[1:]]
both=Image.new('RGB',(1500,570*len(sh)+20),(120,90,70))
for i,x in enumerate(sh): both.paste(x,(0,i*590))
both.save('lamina_tuerto_AB.png')
