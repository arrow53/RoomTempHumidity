"""Deterministic z-buffer renderer of the tessellated CAD assembly. Requires numpy/Pillow.
Run after enclosure.py. No generative image model or hand-drawn enclosure geometry.
"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
SCENE=json.loads((ROOT/'render_scene.json').read_text())
FONT='C:/Windows/Fonts/segoeui.ttf'
def render(name,camera,title,subtitle):
    width,height=2000,1550
    pixels=np.full((height,width,3),(242,245,247),dtype=np.uint8)
    zbuf=np.full((height,width),-np.inf,dtype=np.float32)
    c=np.array(camera,dtype=float);c/=np.linalg.norm(c)
    u=np.cross([0,0,1],c);u/=np.linalg.norm(u);v=np.cross(c,u)
    allv=np.concatenate([np.array(o['vertices']) for o in SCENE]);p=np.stack([allv@u,-allv@v],axis=-1)
    mn=p.min(0);mx=p.max(0);scale=min(1740/(mx[0]-mn[0]),1140/(mx[1]-mn[1]))
    offset=np.array([width/2,820])-scale*(mn+mx)/2
    light=np.array([-.45,-.7,.9]);light/=np.linalg.norm(light)
    def draw_triangle(P,world,color,flat=False):
        A,B,C=P
        x0=max(0,int(np.floor(P[:,0].min())));x1=min(width-1,int(np.ceil(P[:,0].max())))
        y0=max(0,int(np.floor(P[:,1].min())));y1=min(height-1,int(np.ceil(P[:,1].max())))
        den=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
        if abs(den)<1e-9 or x0>x1 or y0>y1:return
        X,Y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        a=((B[1]-C[1])*(X-C[0])+(C[0]-B[0])*(Y-C[1]))/den
        b=((C[1]-A[1])*(X-C[0])+(A[0]-C[0])*(Y-C[1]))/den
        cc=1-a-b;zz=a*A[2]+b*B[2]+cc*C[2]
        zb=zbuf[y0:y1+1,x0:x1+1];mask=(a>=-1e-7)&(b>=-1e-7)&(cc>=-1e-7)&(zz>zb)
        if not mask.any():return
        normal=np.cross(world[1]-world[0],world[2]-world[0]);norm=np.linalg.norm(normal)
        normal=normal/(norm if norm else 1)
        # Two-sided Lambert shading keeps the true CAD tessellation visible.
        shading=1 if flat else .62+.34*max(0,np.dot(normal,light))+.10*max(0,np.dot(normal,c))
        zb[mask]=zz[mask];pixels[y0:y1+1,x0:x1+1][mask]=np.clip(np.array(color)*shading,0,255).astype(np.uint8)
    # Desk contact shadow, projected from real assembly footprint.
    shadow=np.array([[-14,-37,-.15],[221,-37,-.15],[221,208,-.15],[-14,208,-.15]])
    sv=np.column_stack([np.stack([shadow@u,-shadow@v],axis=-1)*scale+offset,shadow@c])
    draw_triangle(sv[[0,1,2]],shadow[[0,1,2]],[221,227,230],True)
    draw_triangle(sv[[0,2,3]],shadow[[0,2,3]],[221,227,230],True)
    for obj in SCENE:
        vs=np.array(obj['vertices']);ps=np.column_stack([np.stack([vs@u,-vs@v],axis=-1)*scale+offset,vs@c])
        for f in obj['faces']:draw_triangle(ps[f],vs[f],obj['color'])
    im=Image.fromarray(pixels);d=ImageDraw.Draw(im)
    def font(size):
        try:return ImageFont.truetype(FONT,size)
        except OSError:return ImageFont.load_default(size=size)
    d.text((85,58),'ROOM TEMPERATURE + HUMIDITY  /  BASE UNIT CASE',fill=(74,91,103),font=font(24))
    d.text((85,105),title,fill=(26,42,53),font=font(48))
    d.text((85,174),subtitle,fill=(74,91,103),font=font(27))
    d.line((85,1430,1915,1430),fill=(196,207,214),width=2)
    d.text((85,1452),'Revision C  |  15° back from vertical  |  75° above desk',fill=(44,62,73),font=font(25))
    d.text((85,1491),'Actual CAD assembly. Screen inactive. Digital prototype; physical fit, cooling and RF untested.',fill=(88,102,110),font=font(22))
    im.save(ROOT/name)
    print('Rendered',name,flush=True)
render('assembled-front-three-quarter.png',(.7,-1,.52),'Front three-quarter','7-inch landscape display  ·  padded bezel  ·  bolted desktop supports')
render('assembled-rear-three-quarter.png',(-.75,1,.52),'Rear three-quarter','Removable radio cover  ·  upper and lower vents  ·  single Pi power exit')
render('assembled-side.png',(1,0,.025),'Side elevation','Screen angle and desk support geometry shown directly from the assembly')
