from pathlib import Path
import struct,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]/'outputs'/'revision-B'
faces=[];s=math.sqrt(.5)
def stand(p):x,y,z=p;return(x,30+s*(y+z),100+s*(y-z))
def load(name,xf,color):
 b=(root/(name+'.stl')).read_bytes();n=struct.unpack_from('<I',b,80)[0]
 for i in range(n):
  a=struct.unpack_from('<12fH',b,84+50*i)
  faces.append(([xf(a[j:j+3]) for j in (3,6,9)],color))
load('front_bezel',stand,(48,67,79))
load('enclosed_body',lambda p:stand((p[0],p[1],p[2]+4)),(135,150,158))
load('rear_cover_radio_mount',lambda p:stand((p[0],p[1],113-p[2])),(69,88,100))
load('rear_cable_strip',lambda p:stand((p[0],p[1],113-p[2])),(225,147,65))
for off in (0,194.32):load('feet_45_print_two',lambda p,o=off:(o+p[2],p[0],p[1]),(64,82,94))
glass=[stand((x,y,2.3)) for x,y in [(8.5,8.5),(197.82,8.5),(197.82,128.74),(8.5,128.74)]]
faces.append((glass,(24,133,155)))
im=Image.new('RGB',(1800,1120),(246,248,250));d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/segoeui.ttf'
title=ImageFont.truetype(font,36);body=ImageFont.truetype(font,24);small=ImageFont.truetype(font,21)
d.text((55,30),'Revision B - fully enclosed desktop case',font=title,fill=(25,45,60))
d.text((55,85),'7-inch front bezel | Pi behind display | radio inside rear cover | 45 degree stand',font=body,fill=(70,85,100))
def render(camera,region):
 # Orthogonal view bases: camera is toward viewer, world z is vertical.
 c=camera;L=math.sqrt(sum(q*q for q in c));c=[q/L for q in c]
 u=[-c[1],c[0],0];L=math.hypot(*u[:2]);u=[q/L for q in u]
 v=[c[(i+1)%3]*u[(i+2)%3]-c[(i+2)%3]*u[(i+1)%3] for i in range(3)]
 def pnt(p):return(sum(p[i]*u[i] for i in range(3)),-sum(p[i]*v[i] for i in range(3)))
 pts=[pnt(p) for poly,_ in faces for p in poly]
 mins=[min(p[i] for p in pts) for i in range(2)];maxs=[max(p[i] for p in pts) for i in range(2)]
 x,y,w,h=region;scale=min(w/(maxs[0]-mins[0]),h/(maxs[1]-mins[1]))
 def project(p):a,b=pnt(p);return(x+(a-mins[0])*scale,y+(b-mins[1])*scale)
 def depth(poly):return sum(sum(p[i]*c[i] for i in range(3)) for p in poly)/len(poly)
 pixels=np.full((int(h)+1,int(w)+1,3),(246,248,250),dtype=np.uint8)
 zbuf=np.full((int(h)+1,int(w)+1),-np.inf)
 for poly,color in faces:
  a,b,cp=poly[:3];U=[b[i]-a[i] for i in range(3)];V=[cp[i]-a[i] for i in range(3)]
  n=[U[(i+1)%3]*V[(i+2)%3]-U[(i+2)%3]*V[(i+1)%3] for i in range(3)];L=math.sqrt(sum(q*q for q in n)) or 1
  light=.70+.28*abs(sum(n[i]*[.3,-.4,.86][i] for i in range(3))/L)
  points=[(project(p)[0]-x,project(p)[1]-y,sum(p[i]*c[i] for i in range(3))) for p in poly]
  for j in range(1,len(points)-1):
   A,B,C=points[0],points[j],points[j+1]
   x0=max(0,int(math.floor(min(A[0],B[0],C[0]))));x1=min(int(w),int(math.ceil(max(A[0],B[0],C[0]))))
   y0=max(0,int(math.floor(min(A[1],B[1],C[1]))));y1=min(int(h),int(math.ceil(max(A[1],B[1],C[1]))))
   den=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
   if abs(den)<1e-9 or x1<x0 or y1<y0:continue
   X,Y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
   aa=((B[1]-C[1])*(X-C[0])+(C[0]-B[0])*(Y-C[1]))/den
   bb=((C[1]-A[1])*(X-C[0])+(A[0]-C[0])*(Y-C[1]))/den
   cc=1-aa-bb;zz=aa*A[2]+bb*B[2]+cc*C[2]
   tile=zbuf[y0:y1+1,x0:x1+1];mask=(aa>=-1e-7)&(bb>=-1e-7)&(cc>=-1e-7)&(zz>tile)
   tile[mask]=zz[mask];pixels[y0:y1+1,x0:x1+1][mask]=tuple(int(q*light) for q in color)
 im.paste(Image.fromarray(pixels),(int(x),int(y)))
render((.45,-1,.7),(50,180,820,700))
render((-.55,1,.65),(935,180,820,700))
d.text((55,900),'Front: padded bezel, continuous side walls',font=body,fill=(25,45,60))
d.text((935,900),'Rear: vented cover and split cable exits',font=body,fill=(25,45,60))
d.text((55,980),'Case envelope: 206 x 137 x 113 mm. Feet lift the deep shell clear of the desk.',font=small,fill=(70,85,100))
d.text((55,1025),'Prototype meshes shown. Cooler, radio revision, cable fit, RF and thermal performance await verification.',font=small,fill=(95,105,115))
im.save(root/'enclosed-preview.png')
