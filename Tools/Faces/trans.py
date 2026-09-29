from PIL import Image, ImageDraw, ImageFont
import math
SRC="C:/Users/Docente/Desktop/UnityProyects/RunRunSimulator/Assets/RunRunSimulator/Resources/Textures/MoriMochi/Faces/"
M=[('Neutral','07'),('Feliz','03'),('Triste','11'),('Triste b','10'),('Dolor','06'),('Enojado','15'),('Enojado b','05'),('Dormido','08'),('Enfermo','13'),('Mareado','14'),('Asustado','24'),('Amoroso','19'),('Emocionado','23'),('KO','18')]
S=4
def lashes(k):
    im=Image.open(SRC+f'MonchiFace_{k}.png').convert('RGBA'); al=im.getchannel('A').point(lambda v:255 if v>200 else 0)
    big=Image.new('RGBA',(512*S,512*S),(0,0,0,0)); d=ImageDraw.Draw(big)
    for (x0,x1,side) in ((40,215,1),(297,472,-1)):
        bb=al.crop((x0,200 if k not in('10','05') else 226,x1,296)).getbbox()
        if not bb: continue
        y0=200 if k not in('10','05') else 226
        cx=(bb[0]+bb[2])/2+x0; cy=(bb[1]+bb[3])/2+y0; rx=(bb[2]-bb[0])/2; ry=(bb[3]-bb[1])/2
        angs=(-155,-130,-105) if side>0 else (-25,-50,-75)
        for a in angs:
            t=math.radians(a); p=(cx+math.cos(t)*rx,cy+math.sin(t)*ry); q=(p[0]+math.cos(t)*14,p[1]+math.sin(t)*14)
            d.line([(p[0]*S,p[1]*S),(q[0]*S,q[1]*S)],fill=(0,0,0,255),width=5*S)
            for c in (p,q): d.ellipse([(c[0]-2.5)*S,(c[1]-2.5)*S,(c[0]+2.5)*S,(c[1]+2.5)*S],fill=(0,0,0,255))
    im.alpha_composite(big.resize((512,512),Image.LANCZOS)); return im
FEM={k:lashes(k) for _,k in M}
for k,v in FEM.items(): v.save(f'fem_{k}.png')
# static sheet
cw,ch=300,190;cols=5
sh=Image.new('RGB',(cw*cols,ch*3),(236,196,150)); d=ImageDraw.Draw(sh); f=ImageFont.truetype('arial.ttf',16)
for i,(n,k) in enumerate(M):
    c=FEM[k].crop((40,150,472,330)).resize((288,120)); bg=Image.new('RGBA',c.size,(236,196,150,255)); bg.alpha_composite(c)
    x,y=(i%cols)*cw,(i//cols)*ch; sh.paste(bg.convert('RGB'),(x+6,y+30)); d.text((x+8,y+6),n,fill=(40,20,10),font=f)
sh.save('lamina_hembra.png')
# transitions
SEQ=['07','03','23','15','10','19','08','07']
BAND=(0,150,512,292)
def split(im):
    top=im.crop(BAND); low=im.copy(); ImageDraw.Draw(low).rectangle(BAND[:2]+(512,BAND[3]-1),fill=(0,0,0,0)); return top,low
def compose(top,low):
    out=low.copy(); out.alpha_composite(top,(0,BAND[1])); return out
def squash(im,s):
    top,low=split(im); h=top.height; nh=max(1,int(h*s))
    t=top.resize((512,nh),Image.LANCZOS); canvas=Image.new('RGBA',top.size,(0,0,0,0)); canvas.alpha_composite(t,(0,int(256-150-(256-150)*s)))
    return compose(canvas,low)
def pop(im,s):
    top,low=split(im); canvas=Image.new('RGBA',top.size,(0,0,0,0))
    for (x0,x1,cx) in ((0,256,121),(256,512,391)):
        part=top.crop((x0,0,x1,top.height)); w=max(1,int(part.width*s)); h=max(1,int(part.height*s))
        p=part.resize((w,h),Image.LANCZOS); ox=int(cx-(cx-x0)*s); oy=int(106-106*s)
        canvas.alpha_composite(p,(ox,oy)) if 0<=ox and ox+w<=512 and oy>=0 and oy+h<=top.height else canvas.paste(p,(ox,oy),p)
    return compose(canvas,low)
def fade(a,b,t): return Image.blend(a,b,t)
HOLD=14; TR=8
for typ in ('blink','fade','pop'):
    fr=[]
    for i in range(len(SEQ)-1):
        a,b=FEM[SEQ[i]],FEM[SEQ[i+1]]
        fr+= [a]*HOLD
        for j in range(TR):
            t=(j+1)/TR
            if typ=='fade': fr.append(fade(a,b,t))
            elif typ=='blink':
                fr.append(squash(a,max(0.06,1-t*2)) if t<=0.5 else squash(b,min(1,0.06+(t-0.5)*2)))
            else:
                if t<=0.5: fr.append(pop(a,max(0.02,1-t*2)))
                else:
                    u=(t-0.5)*2; s=1+0.18*math.sin(u*math.pi) if u>0.5 else u*2*1.0
                    fr.append(pop(b,max(0.02,min(1.18,u*1.18 if u<0.85 else 1.18-(u-0.85)/0.15*0.18))))
    for n,im in enumerate(fr): im.save(f'frames/{typ}_{n:03d}.png')
    print(typ,len(fr))
