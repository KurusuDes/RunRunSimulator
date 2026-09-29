from PIL import Image, ImageDraw, ImageFont
import math
SRC="C:/Users/Docente/Desktop/UnityProyects/RunRunSimulator/Assets/RunRunSimulator/Resources/Textures/MoriMochi/Faces/"
M=[('Neutral','07'),('Feliz','03'),('Triste','11'),('Triste b','10'),('Dolor','06'),('Enojado','15'),('Enojado b','05'),('Dormido','08'),('Enfermo','13'),('Mareado','14'),('Asustado','24'),('Amoroso','19'),('Emocionado','23'),('KO','18')]
S=4
def lashes(k,mode='top'):
    im=Image.open(SRC+f'MonchiFace_{k}.png').convert('RGBA'); al=im.getchannel('A').point(lambda v:255 if v>200 else 0)
    big=Image.new('RGBA',(512*S,512*S),(0,0,0,0)); d=ImageDraw.Draw(big)
    for (x0,x1,side) in ((40,215,1),(297,472,-1)):
        bb=al.crop((x0,200 if k not in('10','05') else 226,x1,296)).getbbox()
        if not bb: continue
        y0=200 if k not in('10','05') else 226
        cx=(bb[0]+bb[2])/2+x0; cy=(bb[1]+bb[3])/2+y0; rx=(bb[2]-bb[0])/2; ry=(bb[3]-bb[1])/2
        if mode=='top':
            L=[(math.radians(a),)*2 for a in ((-155,-130,-105) if side>0 else (-25,-50,-75))]
        elif mode=='down':
            L=[(math.radians(a),)*2 for a in ((150,120,95) if side>0 else (30,60,85))]
        else:
            b=math.radians(180 if side>0 else 0); L=[(b, math.radians(d)) for d in (((200,180) if side>0 else (-20,0)))]
        for t,dirr in L:
            p=(cx+math.cos(t)*rx,cy+math.sin(t)*ry) if mode!='corner' else (cx+math.cos(t)*rx, bb[3]+y0-4)
            q=(p[0]+math.cos(dirr)*13,p[1]+math.sin(dirr)*13)
            d.line([(p[0]*S,p[1]*S),(q[0]*S,q[1]*S)],fill=(0,0,0,255),width=5*S)
            for c in (p,q): d.ellipse([(c[0]-2.5)*S,(c[1]-2.5)*S,(c[0]+2.5)*S,(c[1]+2.5)*S],fill=(0,0,0,255))
    im.alpha_composite(big.resize((512,512),Image.LANCZOS)); return im
MODE={'07':'top','11':'top','10':'top','15':'top','05':'top','24':'top','03':'corner','08':'down'}
FEM={k:(lashes(k,MODE[k]) if k in MODE else Image.open(SRC+f'MonchiFace_{k}.png').convert('RGBA')) for _,k in M}
for k,v in FEM.items(): v.save(f'fem_{k}.png')
# static sheet
cw,ch=300,190;cols=5
sh=Image.new('RGB',(cw*cols,ch*3),(236,196,150)); d=ImageDraw.Draw(sh); f=ImageFont.truetype('arial.ttf',16)
for i,(n,k) in enumerate(M):
    c=FEM[k].crop((40,150,472,330)).resize((288,120)); bg=Image.new('RGBA',c.size,(236,196,150,255)); bg.alpha_composite(c)
    x,y=(i%cols)*cw,(i//cols)*ch; sh.paste(bg.convert('RGB'),(x+6,y+30)); d.text((x+8,y+6),n,fill=(40,20,10),font=f)
sh.save('lamina_hembra.png')
