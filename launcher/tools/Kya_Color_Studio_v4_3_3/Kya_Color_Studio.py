# -*- coding: utf-8 -*-
"""Kya Color Studio 4.3.4 — verified UV presets, freehand painting, lipstick, nail polish and coordinated randomize.
The 14 proven regions retain their exact masks; cosmetic masks for lips and nail polish are user-validated add-ons.
"""
from pathlib import Path
import colorsys, math, json, subprocess, threading, queue, traceback, os, random, io
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps, ImageChops, ImageDraw, ImageStat

HERE=Path(__file__).resolve().parent
ASSETS=HERE/'assets'
NAME='5417b68a93e1b617-435f677b690903da-00002213.png'
DEFAULT_DEST=Path.home()/'Documents'/'PCSX2'/'textures'/'SLES-51473'/'replacements'
BG='#100D18';NAV='#1A1527';PANEL='#251C34';CARD='#2B203A';BORDER='#483459'
TXT='#F9F2FF';SUB='#C3B0D5';DIM='#9B89B2';ACC='#C48CFF';ACC2='#6C419A';GOOD='#9FF1BA';ERR='#FF9AB8'
FONT='Segoe UI'
VIEWS=['0_Face.png','1_Profil_gauche.png','2_Profil_droit.png','3_Dos.png']
VIEWS_NAMES=['FRONT','LEFT','RIGHT','BACK']
PRESETS=['#8D32C8','#BB52E6','#FF3855','#EA577D','#171923','#44414B','#F4D5F5','#04B4AE']

def is_hex(v):return isinstance(v,str) and len(v)==7 and v[0]=='#' and all(c in '0123456789ABCDEFabcdef' for c in v[1:])
def hex_rgb(v):return tuple(int(v[i:i+2],16) for i in (1,3,5))
def rgb_hex(rgb):return '#%02X%02X%02X'%tuple(int(max(0,min(255,c))) for c in rgb)

class Button(tk.Frame):
 def __init__(self,parent,text,command,kind='normal',height=36,**kw):
  self.kind=kind;self.command=command;self.enabled=True
  schemes={'normal':(CARD,'#433051',TXT),'subtle':('#2B2237','#3A2B49',SUB),
      'primary':(ACC,'#DBAFFF','#1D1028'),'danger':('#3B2638','#503047','#FFDFEA')}
  self.normal,self.hover,self.fore=schemes[kind]
  super().__init__(parent,bg=self.normal,height=height,**kw);self.pack_propagate(False)
  self.lbl=tk.Label(self,text=text,bg=self.normal,fg=self.fore,font=(FONT,10,'bold'),cursor='hand2')
  self.lbl.pack(fill='both',expand=True)
  for el in (self,self.lbl):
   el.bind('<Enter>',lambda e:self._set_bg(self.hover if self.enabled else self.normal))
   el.bind('<Leave>',lambda e:self._set_bg(self.normal))
   el.bind('<Button-1>',lambda e:self.command() if self.enabled else None)
 def _set_bg(self,b):self.configure(bg=b);self.lbl.configure(bg=b)
 def set_active(self,on):
  self.normal=ACC2 if on else CARD;self.hover='#7D50AD' if on else '#433051';self._set_bg(self.normal)
 def set_enabled(self,on):
  self.enabled=on;self.lbl.configure(fg=self.fore if on else DIM,cursor='hand2' if on else 'arrow')

class Studio:
 def __init__(self,root):
  self.root=root;root.configure(bg=BG);root.overrideredirect(True);root.geometry('1400x850+70+65')
  self.maxed=False;self.old_geo='1400x850+70+65';self._closing=False;self.draginfo=None
  self.base=Image.open(ASSETS/'vanilla.png').convert('RGBA')
  assert self.base.size==(1024,1024)
  meta=json.loads((ASSETS/'zones.json').read_text(encoding='utf-8'))
  self.names={k:v['name'] for k,v in meta.items()}
  self.masks={k:Image.open(ASSETS/'masks'/f'{k}.png').convert('L') for k in meta}
  self.bounds={k:tuple(v['bounds']) for k,v in meta.items()}
  self.ids=list(self.names)
  self.colors={k:None for k in self.ids};self.display=self.base.copy()
  self.paint_layer=Image.new('RGBA',self.base.size,(0,0,0,0))
  self.tool='select';self.brush_size=16;self.stroke_last=None;self.brush_stroke_active=False
  self.paint_path=HERE/'studio_brush_layer.png'
  self.active=self.ids[0];self.undo_stack=[];self.redo_stack=[]
  self.hex_color='#8D32C8';self.hsv=colorsys.rgb_to_hsv(*[v/255 for v in hex_rgb(self.hex_color)])
  self.jobs=queue.Queue();self.busy=False
  self.after_atlas=None;self.after_save=None;self.after_color=None;self.after_previews=None
  self.zoom=1.;self.panx=0;self.pany=0;self.status='Choose a body part, then pick a color.'
  self.cfg=HERE/'studio_settings.json';self.destination=str(DEFAULT_DEST)
  if self.cfg.exists():
   try:
    s=json.loads(self.cfg.read_text(encoding='utf-8'))
    self.destination=str(s.get('destination',self.destination))
    for k,v in s.get('colors',{}).items():
     if k in self.colors and is_hex(v):self.colors[k]=v.upper()
    saved=s.get('color')
    if is_hex(saved):self.hex_color=saved.upper()
    self.brush_size=max(2,min(72,int(s.get('brush_size',16))))
   except Exception:pass
  self.hsv=colorsys.rgb_to_hsv(*[v/255 for v in hex_rgb(self.hex_color)])
  if self.paint_path.exists():
   try:
    saved_layer=Image.open(self.paint_path).convert('RGBA')
    if saved_layer.size==self.base.size:self.paint_layer=saved_layer.copy()
   except Exception:pass
  self._rebuild()
  self._build()
  root.bind('<Escape>',lambda e:self.close())
  root.bind('<Control-z>',lambda e:self.undo())
  root.bind('<Control-y>',lambda e:self.redo())
  root.bind('<Configure>',self._resize)
  root.bind('<Control-Return>',lambda e:self.apply())
  # Windows sends wheel events to the label under the pointer, not the
  # enclosing scrolling Canvas. Bind at app level and route ONLY events
  # occurring over the parts list; the UV canvas keeps its own zoom wheel.
  root.bind_all('<MouseWheel>',self._parts_wheel,add='+')
  root.bind_all('<Button-4>',self._parts_wheel,add='+')
  root.bind_all('<Button-5>',self._parts_wheel,add='+')
  root.after(200,self._refresh)

 def label(self,p,text,size=10,color=TXT,bold=False,**opts):
  return tk.Label(p,text=text,bg=p.cget('bg'),fg=color,font=(FONT,size,'bold' if bold else 'normal'),**opts)

 def _build(self):
  r=self.root
  head=tk.Frame(r,bg=NAV,height=62);head.pack(fill='x');head.pack_propagate(False)
  logo=tk.Label(head,text='K',font=(FONT,22,'bold'),bg=ACC,fg=BG,width=3);logo.pack(side='left',padx=(15,12),pady=8)
  heading=tk.Frame(head,bg=NAV);heading.pack(side='left',pady=8)
  self.label(heading,'KYA   /   COLOR STUDIO',14,TXT,True).pack(anchor='w')
  self.label(heading,'RECOLOR  •  PAINT  •  PERSONALIZE',8,DIM).pack(anchor='w')
  topbuttons=tk.Frame(head,bg=NAV);topbuttons.pack(side='right',padx=8)
  for t,fn in [('—',self.minimize),('□',self.maximize),('×',self.close)]:
   b=Button(topbuttons,t,fn,'subtle',height=33,width=40);b.pack(side='left',padx=2,pady=14)
  for el in (head,logo,heading):
   el.bind('<ButtonPress-1>',self.drag_start);el.bind('<B1-Motion>',self.drag_move)
   el.bind('<Double-Button-1>',lambda e:self.maximize())
  tk.Frame(r,bg=BORDER,height=1).pack(fill='x')
  foot=tk.Frame(r,bg=NAV,height=37);foot.pack(side='bottom',fill='x');foot.pack_propagate(False)
  self.status_label=self.label(foot,self.status,9,SUB,anchor='w');self.status_label.pack(side='left',fill='both',expand=True,padx=18,pady=9)
  resize=self.label(foot,'◢',12,DIM,cursor='arrow');resize.pack(side='right',padx=7)
  resize.bind('<ButtonPress-1>',self.resize_start);resize.bind('<B1-Motion>',self.resize_move)
  body=tk.Frame(r,bg=BG);body.pack(fill='both',expand=True,padx=10,pady=10)
  left=tk.Frame(body,bg=NAV,width=260);left.pack(side='left',fill='y');left.pack_propagate(False)
  right=tk.Frame(body,bg=NAV,width=275);right.pack(side='right',fill='y');right.pack_propagate(False)
  middle=tk.Frame(body,bg=BG);middle.pack(side='left',fill='both',expand=True,padx=10)
  self._left(left);self._middle(middle);self._right(right)

 def _left(self,p):
  self.label(p,'BODY PARTS',11,ACC,True).pack(anchor='w',padx=14,pady=(17,4))
  self.label(p,'Choose a part to recolor',9,SUB).pack(anchor='w',padx=14,pady=(0,8))
  listbox=tk.Frame(p,bg=NAV);listbox.pack(fill='both',expand=True,padx=10)
  self.part_canvas=tk.Canvas(listbox,bg=NAV,highlightthickness=0,width=238)
  scrollbar=tk.Scrollbar(listbox,orient='vertical',command=self.part_canvas.yview)
  self.part_canvas.configure(yscrollcommand=scrollbar.set)
  self.part_canvas.pack(side='left',fill='both',expand=True)
  scrollbar.pack(side='right',fill='y')
  self.part_inner=tk.Frame(self.part_canvas,bg=NAV)
  self.part_win=self.part_canvas.create_window((0,0),window=self.part_inner,anchor='nw')
  self.part_inner.bind('<Configure>',lambda e:self.part_canvas.configure(scrollregion=self.part_canvas.bbox('all')))
  self.part_canvas.bind('<Configure>',lambda e:self.part_canvas.itemconfigure(self.part_win,width=e.width))
  self.part_buttons={}
  for k,name in self.names.items():
   b=Button(self.part_inner,name,lambda key=k:self.select(key),height=33)
   b.pack(fill='x',padx=4,pady=3)
   self.part_buttons[k]=b
  self.part_buttons[self.active].set_active(True)
  self.label(p,'COLOR WHEEL',11,ACC,True).pack(anchor='w',padx=14,pady=(13,8))
  img=Image.open(ASSETS/'wheel.png').convert('RGBA').resize((180,180),Image.Resampling.LANCZOS)
  self.wheel_img=ImageTk.PhotoImage(img)
  self.wheel=tk.Canvas(p,bg=NAV,width=180,height=180,highlightthickness=0,cursor='crosshair')
  self.wheel.pack();self.wheel.create_image(90,90,image=self.wheel_img)
  self.cursor=self.wheel.create_oval(0,0,0,0,outline=BG,fill=TXT,width=2)
  self.wheel.bind('<Button-1>',self.pick_wheel);self.wheel.bind('<B1-Motion>',self.pick_wheel)
  self.valuebar=tk.Canvas(p,bg=NAV,width=180,height=24,highlightthickness=0,cursor='hand2')
  self.valuebar.pack(pady=(5,8));self.valuebar.bind('<Button-1>',self.pick_value);self.valuebar.bind('<B1-Motion>',self.pick_value)
  self.hexvar=tk.StringVar(value=self.hex_color)
  cr=tk.Frame(p,bg=NAV);cr.pack(fill='x',padx=15)
  self.swatch=tk.Frame(cr,bg=self.hex_color,width=31,height=30);self.swatch.pack(side='left',padx=(0,7));self.swatch.pack_propagate(False)
  self.hex_entry=tk.Entry(cr,textvariable=self.hexvar,bg='#362744',fg=TXT,insertbackground=TXT,relief='flat',
              font=(FONT,12,'bold'),justify='center',highlightthickness=1,highlightbackground=BORDER)
  self.hex_entry.pack(fill='x',expand=True,ipady=4)
  self.hex_entry.bind('<Return>',self.hex_commit)
  self.label(p,'PRESETS',8,SUB,True).pack(anchor='w',padx=15,pady=(9,3))
  sw=tk.Frame(p,bg=NAV);sw.pack(padx=12,pady=(0,7))
  for color in PRESETS:
   dot=tk.Canvas(sw,bg=NAV,highlightthickness=0,width=26,height=27,cursor='hand2')
   dot.pack(side='left',padx=1)
   dot.create_oval(4,4,23,23,fill=color,outline=BORDER)
   dot.bind('<Button-1>',lambda e,c=color:self.commit_color(c,history=True))
  self._update_palette()

 def _middle(self,p):
  header=tk.Frame(p,bg=BG);header.pack(fill='x',pady=(5,9))
  self.label(header,'UV TEXTURE  /  LIVE COLORS',18,TXT,True).pack(side='left')
  # The texture resolution is an internal detail, not an interface heading.
  frame=tk.Frame(p,bg=PANEL,highlightthickness=1,highlightbackground=BORDER)
  frame.pack(fill='both',expand=True)
  self.atlas=tk.Canvas(frame,bg=PANEL,highlightthickness=0,cursor='crosshair');self.atlas.pack(fill='both',expand=True,padx=7,pady=7)
  self.atlas.bind('<Button-1>',self.atlas_down)
  self.atlas.bind('<B1-Motion>',self.atlas_drag)
  self.atlas.bind('<ButtonRelease-1>',self.atlas_up)
  self.atlas.bind('<Button-3>',self.pan_start);self.atlas.bind('<B3-Motion>',self.pan_move)
  self.atlas.bind('<MouseWheel>',self.zoom_move)
  self.atlas.bind('<Button-4>',lambda e:self.zoom_move(e,1))
  self.atlas.bind('<Button-5>',lambda e:self.zoom_move(e,-1))
  nav=tk.Frame(p,bg=BG);nav.pack(fill='x',pady=(8,4))
  self.uv_info=self.label(nav,'UV: —',9,SUB);self.uv_info.pack(side='left')
  for text,fn in [('FIT',self.fit),('REDO',self.redo),('UNDO',self.undo)]:
   b=Button(nav,text,fn,'subtle',height=32,width=69);b.pack(side='right',padx=3)
  self.label(p,'Left-click: select / draw   •   Right-drag: pan   •   Wheel: zoom',9,DIM).pack(anchor='w')

 def _right(self,p):
  self.label(p,'DRAW TOOLS',11,ACC,True).pack(anchor='w',padx=12,pady=(17,5))
  self.label(p,'Draw directly on the UV square',9,SUB).pack(anchor='w',padx=12,pady=(0,10))
  bar=tk.Frame(p,bg=NAV);bar.pack(fill='x',padx=10,pady=(0,8))
  self.tool_buttons={}
  for key,caption in [('select','SELECT'),('brush','BRUSH'),('erase','ERASER')]:
   btn=Button(bar,caption,lambda k=key:self.set_tool(k),'subtle',height=36)
   btn.pack(side='left',fill='x',expand=True,padx=2)
   self.tool_buttons[key]=btn
  self.tool_buttons[self.tool].set_active(True)
  self.label(p,'BRUSH SIZE',9,ACC,True).pack(anchor='w',padx=12,pady=(8,2))
  self.brush_info=self.label(p,'16 px',10,TXT,True)
  self.brush_info.pack(anchor='e',padx=16)
  self.brush_var=tk.IntVar(value=self.brush_size)
  slider=tk.Scale(p,from_=2,to=72,orient='horizontal',variable=self.brush_var,command=self.set_brush_size,
      showvalue=False,bg=NAV,fg=TXT,highlightthickness=0,troughcolor=CARD,activebackground=ACC,
      sliderrelief='flat',bd=0,relief='flat',length=230)
  slider.pack(fill='x',padx=14,pady=(0,6))
  self.current_part=self.label(p,self.names[self.active],11,TXT,True)
  self.current_part.pack(anchor='w',padx=12,pady=(8,4))
  self.part_tip=self.label(p,'Choose a region then a wheel color.',9,SUB,wraplength=244,justify='left')
  self.part_tip.pack(anchor='w',padx=12,pady=(0,12))
  Button(p,'RESET SELECTED PART',self.reset_selected,'subtle',height=34).pack(fill='x',padx=12,pady=3)
  actions=tk.Frame(p,bg=NAV);actions.pack(fill='x',padx=12,pady=3)
  Button(actions,'RANDOMIZE',self.randomize,'primary',height=34).pack(side='left',fill='x',expand=True,padx=(0,3))
  Button(actions,'RESET ALL',self.reset_all,'subtle',height=34).pack(side='left',fill='x',expand=True,padx=(3,0))
  self.label(p,'PCSX2 TEXTURE',11,ACC,True).pack(anchor='w',padx=12,pady=(15,5))
  self.dest_label=self.label(p,self.destination,8,SUB,wraplength=246,justify='left')
  self.dest_label.pack(anchor='w',padx=12,pady=(0,7))
  Button(p,'CHANGE PCSX2 FOLDER',self.choose_folder,'subtle',height=30).pack(fill='x',padx=12,pady=(0,10))
  self.apply_btn=Button(p,'APPLY',self.apply,'primary',height=44);self.apply_btn.pack(fill='x',padx=12,pady=(0,6))
  self.restore_btn=Button(p,'RESTORE VANILLA',self.restore,'danger',height=36);self.restore_btn.pack(fill='x',padx=12)
  self.label(p,'Brush uses the true texture pixels. Lipstick and Nail Polish are dedicated cosmetic masks. Apply installs to PCSX2.',
      8,DIM,wraplength=245,justify='left').pack(anchor='w',padx=12,pady=(10,4))
  self.select(self.active)

 def set_tool(self,tool):
  if tool not in ('select','brush','erase') or self.busy:return
  self.tool=tool
  for k,b in self.tool_buttons.items():b.set_active(k==tool)
  self.atlas.configure(cursor='hand2' if tool=='select' else 'crosshair')
  if tool=='select':self.set_status('Select a mapped UV part, then change its color on the wheel.')
  elif tool=='brush':self.set_status('BRUSH: pick a wheel color and paint freely on the UV texture.')
  else:self.set_status('ERASER: clear your freehand strokes without changing the base UV colors.')
  self._schedule_atlas()

 def set_brush_size(self,value):
  self.brush_size=int(float(value))
  if hasattr(self,'brush_info'):self.brush_info.configure(text=f'{self.brush_size} px')

 def set_status(self,text,error=False):
  self.status=text
  if hasattr(self,'status_label'):self.status_label.config(text=text,fg=ERR if error else SUB)
 def select(self,key):
  if key not in self.colors:return
  self.active=key
  self.tool='select'
  if hasattr(self,'tool_buttons'):
   for k,b in self.tool_buttons.items():b.set_active(k=='select')
   self.atlas.configure(cursor='hand2')
  for k,b in self.part_buttons.items():b.set_active(k==key)
  self.current_part.config(text=self.names[key])
  if self.colors[key]:
   self.set_wheel_color(self.colors[key])
  else:
   mask=self.masks[key]
   av=ImageStat.Stat(self.base.convert('RGB'),mask).mean
   avg=rgb_hex(tuple(int(v) for v in av))
   self.set_wheel_color(avg)
  tip = 'Choose a color to recolor this part.'
  if key=='LP': tip='Dedicated lip color mask. Choose a color for lipstick.'
  elif key=='NP': tip='Dedicated nail polish mask. Choose a color for the nails / varnish.'
  self.part_tip.config(text=tip + ('\n(Vanilla: not recolored)' if not self.colors[key] else ''))
  self.root.after_idle(self._ensure_selected_visible)
  self._schedule_atlas();self.set_status(f'{self.names[key]} — change the color on the wheel.')

 def _parts_wheel(self,event):
  """Scroll the list even when hovering a custom Button/Label, not just Canvas.

  The event reaches the root via bind_all; do not consume the wheel on the
  central UV texture (where it zooms) or on the color wheel / side panel.
  """
  c=self.part_canvas
  if not c.winfo_ismapped():return
  x,y=event.x_root,event.y_root
  x0,y0=c.winfo_rootx(),c.winfo_rooty()
  if not (x0<=x<x0+c.winfo_width() and y0<=y<y0+c.winfo_height()):
   return
  if event.num==4:steps=-1
  elif event.num==5:steps=1
  else:
   delta=getattr(event,'delta',0)
   if not delta:return
   # Usually +/-120 on Windows. Some touchpads send smaller increments.
   steps=-max(1,round(abs(delta)/120)) if delta>0 else max(1,round(abs(delta)/120))
  if c.yview()!=(0.0,1.0):c.yview_scroll(steps*2,'units')
  return 'break'

 def _ensure_selected_visible(self):
  """Show buttons selected from the UV texture or by keyboard."""
  if self._closing or not self.part_canvas.winfo_exists():return
  c=self.part_canvas
  b=self.part_buttons.get(self.active)
  if b is None:return
  viewport=c.winfo_height()
  total=self.part_inner.winfo_height()
  if viewport<10 or total<=viewport:return
  start=c.canvasy(0)
  end=start+viewport
  y=b.winfo_y()
  bottom=y+b.winfo_height()
  if y<start+2:c.yview_moveto(max(0,(y-4)/total))
  elif bottom>end-2:c.yview_moveto(min(1,(bottom-viewport+4)/total))

 def set_wheel_color(self,color):
  if not is_hex(color):return
  self.hex_color=color.upper();self.hsv=colorsys.rgb_to_hsv(*[v/255 for v in hex_rgb(self.hex_color)])
  self.hexvar.set(self.hex_color);self.swatch.config(bg=self.hex_color);self._update_palette()
 def pick_wheel(self,e):
  if not hasattr(self,'_wheel_stroke') or not self._wheel_stroke:
   if self.tool=='select':self._push_history()
   self._wheel_stroke=True
  dx=e.x-90;dy=90-e.y
  h=(math.atan2(dy,dx)/(2*math.pi))%1
  s=min(1,math.hypot(dx,dy)/82)
  self.hsv=(h,s,self.hsv[2]);self._hsv_commit()
  self.wheel.bind('<ButtonRelease-1>',lambda ev:setattr(self,'_wheel_stroke',False))
 def pick_value(self,e):
  if not getattr(self,'_value_stroke',False):
   if self.tool=='select':self._push_history()
   self._value_stroke=True
  self.hsv=(self.hsv[0],self.hsv[1],max(0.,min(1.,(e.x-5)/170)))
  self._hsv_commit()
  self.valuebar.bind('<ButtonRelease-1>',lambda ev:setattr(self,'_value_stroke',False))
 def _hsv_commit(self):
  v=colorsys.hsv_to_rgb(*self.hsv)
  c=rgb_hex(tuple(round(x*255) for x in v))
  self.hex_color=c;self.hexvar.set(c);self.swatch.config(bg=c);self._update_palette()
  if self.tool=='select':
   self.colors[self.active]=c;self._schedule_color()
  else:self.set_status('Brush color: '+c+' — draw on the UV atlas.')
 def _update_palette(self):
  if not hasattr(self,'wheel'):return
  h,s,v=self.hsv
  x=90+82*s*math.cos(2*math.pi*h);y=90-82*s*math.sin(2*math.pi*h)
  self.wheel.coords(self.cursor,x-5,y-5,x+5,y+5)
  self.valuebar.delete('all')
  for i in range(171):
   rgb=colorsys.hsv_to_rgb(h,s,i/170)
   self.valuebar.create_line(i+5,6,i+5,19,fill=rgb_hex(tuple(round(k*255) for k in rgb)))
  xx=5+170*v
  self.valuebar.create_oval(xx-6,0,xx+6,24,fill=TXT,outline=BG,width=2)
 def hex_commit(self,e=None):
  v=self.hexvar.get().strip();v='#'+v if len(v)==6 else v
  if is_hex(v):self.commit_color(v,True)
  else:self.hexvar.set(self.hex_color);self.set_status('Enter a valid color such as #A36BDD.',True)
 def commit_color(self,color,history=True):
  if not is_hex(color) or self.busy:return
  if history and self.tool=='select':self._push_history()
  self.set_wheel_color(color)
  if self.tool=='select':
   self.colors[self.active]=self.hex_color
   self._schedule_color()
  else:self.set_status('Brush color selected: '+self.hex_color)
 def _schedule_color(self):
  if self.after_color:self.root.after_cancel(self.after_color)
  self.after_color=self.root.after(50,self._apply_selected_color)
 def _apply_selected_color(self):
  self.after_color=None
  self._rebuild();self._schedule_atlas();self._schedule_save()
  self.part_tip.config(text='Color selected. Press Apply to install in PCSX2.')
  self.set_status(f'{self.names[self.active]}: {self.colors[self.active]} (not yet installed).')
 def _snapshot(self):
  buffer=io.BytesIO()
  self.paint_layer.save(buffer,format='PNG',compress_level=1)
  return (self.colors.copy(),buffer.getvalue())
 def _load_snapshot(self,snap):
  colors,png=snap
  self.colors=colors.copy()
  self.paint_layer=Image.open(io.BytesIO(png)).convert('RGBA')
 def _push_history(self):
  snap=self._snapshot()
  if self.undo_stack and self.undo_stack[-1]==snap:return
  self.undo_stack.append(snap)
  if len(self.undo_stack)>25:self.undo_stack.pop(0)
  self.redo_stack.clear()
 def undo(self):
  if not self.undo_stack or self.busy:return
  self.redo_stack.append(self._snapshot());self._load_snapshot(self.undo_stack.pop())
  self._rebuild();self.select(self.active);self._schedule_atlas();self._schedule_save()
 def redo(self):
  if not self.redo_stack or self.busy:return
  self.undo_stack.append(self._snapshot());self._load_snapshot(self.redo_stack.pop())
  self._rebuild();self.select(self.active);self._schedule_atlas();self._schedule_save()
 def randomize(self):
  """Randomize coherent outfits: members of a single garment share one HEX.

  Confirmed by the user's neon UV map. Lipstick and Nail Polish get
  independent colors. Face, hand skin, zone 16, and strokes stay untouched.
  """
  if self.busy:return
  if self.after_color:
   self.root.after_cancel(self.after_color);self.after_color=None
   self._apply_selected_color()
  self._push_history()
  rng=random.SystemRandom()
  # A group receives ONE color. Individual buttons can still be edited later.
  # 01+10 = trousers and pocket; 03+04+05 = shirt/back/shoulders/chest.
  # 06+07 = all hair; 08+15 = shoes including toe/sole.
  matching=[('01','10'),('03','04','05'),('06','07'),('08','15')]
  valid=list(self.ids)
  claimed={k for g in matching for k in g}
  groups=[tuple(k for k in g if k in valid) for g in matching]
  groups=[g for g in groups if g]
  groups += [(k,) for k in valid if k not in claimed]
  hue0=rng.random()
  hues=[(hue0+(i/len(groups)))%1 for i in range(len(groups))]
  rng.shuffle(hues)
  for group,hue in zip(groups,hues):
   saturation=rng.uniform(.60,.96)
   brightness=rng.uniform(.65,.99)
   rgb=colorsys.hsv_to_rgb(hue,saturation,brightness)
   color=rgb_hex(tuple(round(255*v) for v in rgb))
   for key in group:self.colors[key]=color
  self._rebuild()
  if self.colors[self.active]:self.set_wheel_color(self.colors[self.active])
  self.part_tip.config(text='Matching pieces share a color. Lipstick and Nail Polish get separate colors. Undo reverses everything.')
  self._schedule_atlas();self._schedule_save()
  self.set_status('Randomized body parts, Lipstick and Nail Polish. Linked outfit pieces share a color. Apply to PCSX2.')

 def reset_selected(self):
  if self.busy:return
  self._push_history();self.colors[self.active]=None;self._rebuild();self.select(self.active);self._schedule_atlas();self._schedule_save()
 def reset_all(self):
  if self.busy:return
  self._push_history();self.colors={k:None for k in self.ids}
  self.paint_layer=Image.new('RGBA',self.base.size,(0,0,0,0))
  self._rebuild();self.select(self.active);self._schedule_atlas();self._schedule_save();self.set_status('All parts and brush strokes reset.')
 def _rebuild(self):
  out=self.base.copy()
  # Masks are the exact *observed* neon pixels from the diagnostic. All remaining
  # RGBA bytes remain unchanged; this includes excluded face and skin regions.
  for key,color in self.colors.items():
   if not color:continue
   bbox=self.bounds[key]
   original=self.base.crop(bbox)
   luminance=ImageOps.grayscale(original)
   rgb=hex_rgb(color)
   dark=tuple(round(x*.13) for x in rgb)
   light=tuple(min(255,round(x*.66+82)) for x in rgb)
   tinted=ImageOps.colorize(luminance,dark,light,mid=rgb,blackpoint=8,whitepoint=243,midpoint=112).convert('RGBA')
   tinted.putalpha(original.getchannel('A'))
   out.paste(tinted,bbox[:2],self.masks[key].crop(bbox))
  # Preserve *entire* original alpha channel exactly, independent of tint.
  out=Image.alpha_composite(out,self.paint_layer)
  out.putalpha(self.base.getchannel('A'))
  self.display=out
 def _schedule_save(self):
  if self._closing:return
  if self.after_save:self.root.after_cancel(self.after_save)
  self.after_save=self.root.after(650,self._save)
 def _save(self):
  self.after_save=None
  try:
   self.cfg.write_text(json.dumps({'destination':self.destination,'colors':self.colors,'color':self.hex_color,'brush_size':self.brush_size},indent=2),encoding='utf-8')
   if self.paint_layer.getbbox():
    tmp=self.paint_path.with_suffix('.tmp')
    self.paint_layer.save(tmp,format='PNG');os.replace(tmp,self.paint_path)
   elif self.paint_path.exists():self.paint_path.unlink()
  except OSError:pass
 def _schedule_atlas(self):
  if self._closing or self.after_atlas:return
  self.after_atlas=self.root.after(80,self._render_atlas)
 def _refresh(self):self._render_atlas()
 def _render_atlas(self):
  self.after_atlas=None
  c=self.atlas;w=c.winfo_width();h=c.winfo_height()
  if w<80 or h<80:return
  scale=min((w-16)/1024,(h-16)/1024)*self.zoom
  size=max(32,int(round(1024*scale)))
  left=int((w-size)/2+self.panx);top=int((h-size)/2+self.pany)
  self.scale=scale;self.left=left;self.top=top
  raw=self.display.copy()
  # For viewing only: original texture is semi-transparent. Show RGB opaque;
  # original alpha in the installed PNG is untouched.
  raw.putalpha(raw.getchannel('A').point(lambda a:255 if a>0 else 0))
  img=raw.resize((size,size),Image.Resampling.NEAREST if self.zoom>=1.4 else Image.Resampling.BILINEAR)
  self.atlas_image=ImageTk.PhotoImage(img)
  c.delete('all')
  # Solid background; avoid the distracting transparency checkerboard.
  c.create_image(left,top,anchor='nw',image=self.atlas_image)
  c.create_rectangle(left,top,left+size,top+size,outline=ACC2)
  if self.tool=='select':
   bx0,by0,bx1,by1=self.bounds[self.active]
   x0=left+bx0*scale;y0=top+by0*scale;x1=left+bx1*scale;y1=top+by1*scale
   c.create_rectangle(x0,y0,x1,y1,outline='#C0FFB3',width=2,dash=(5,4))
   # Keep the outline without displaying the internal mask identifier.
  mode_info=self.names[self.active] if self.tool=='select' else f'{self.brush_size} px'
  self.uv_info.config(text=f'{self.tool.upper()}   •   {mode_info}   •   {int(self.zoom*100)}%')
 def _canvas_to_uv(self,x,y):
  if not hasattr(self,'scale') or self.scale<=0:return None
  X=int((x-self.left)/self.scale);Y=int((y-self.top)/self.scale)
  if 0<=X<1024 and 0<=Y<1024:return X,Y
  return None
 def atlas_down(self,e):
  if self.tool=='select':self.atlas_select(e);return
  if self.busy:return
  pos=self._canvas_to_uv(e.x,e.y)
  if not pos:return
  if self.after_color:
   self.root.after_cancel(self.after_color);self._apply_selected_color()
  self._push_history();self.brush_stroke_active=True;self.stroke_last=pos
  self._stroke(pos,pos)
 def atlas_drag(self,e):
  if not self.brush_stroke_active or self.busy:return
  pos=self._canvas_to_uv(e.x,e.y)
  if pos is None:return
  prev=self.stroke_last or pos
  self._stroke(prev,pos);self.stroke_last=pos
 def atlas_up(self,e):
  if self.brush_stroke_active:
   self.brush_stroke_active=False;self.stroke_last=None
   self._rebuild();self._schedule_atlas();self._schedule_save()
 def _stroke(self,p1,p2):
  size=max(1,self.brush_size);radius=size/2
  # Draw directly in texture-pixel coordinates, regardless of canvas zoom.
  if self.tool=='erase':
   ink=(0,0,0,0)
  else:ink=(*hex_rgb(self.hex_color),255)
  d=ImageDraw.Draw(self.paint_layer)
  d.line((p1[0],p1[1],p2[0],p2[1]),fill=ink,width=size)
  for x,y in (p1,p2):d.ellipse((int(x-radius),int(y-radius),int(x+radius),int(y+radius)),fill=ink)
  self._rebuild();self._schedule_atlas()
 def atlas_select(self,e):
  pos=self._canvas_to_uv(e.x,e.y)
  if not pos:return
  for key in self.ids:
   if self.masks[key].getpixel(pos)>100:self.select(key);return
  self.set_status('This pixel is outside the editable body parts.')
 def pan_start(self,e):self.pan_pos=(e.x,e.y,self.panx,self.pany)
 def pan_move(self,e):
  x,y,px,py=self.pan_pos;self.panx=px+e.x-x;self.pany=py+e.y-y;self._schedule_atlas()
 def zoom_move(self,e,force=None):
  z=self.zoom;delta=force if force is not None else (1 if e.delta>0 else -1)
  self.zoom=max(.65,min(6.,z*(1.18 if delta>0 else 1/1.18)))
  mx=e.x-self.atlas.winfo_width()/2;my=e.y-self.atlas.winfo_height()/2;f=self.zoom/z
  self.panx=mx-(mx-self.panx)*f;self.pany=my-(my-self.pany)*f;self._schedule_atlas();return 'break'
 def fit(self):self.zoom=1.;self.panx=self.pany=0;self._schedule_atlas()
 def _resize(self,e=None):
  if not self._closing:self._schedule_atlas()
 def drag_start(self,e):
  if not self.maxed:self.draginfo=(e.x_root,e.y_root,self.root.winfo_x(),self.root.winfo_y())
 def drag_move(self,e):
  if self.draginfo:
   x,y,ox,oy=self.draginfo;self.root.geometry(f'+{ox+e.x_root-x}+{oy+e.y_root-y}')
 def maximize(self):
  if self.maxed:self.root.geometry(self.old_geo);self.maxed=False
  else:
   self.old_geo=self.root.geometry();self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()-42}+0+0');self.maxed=True
  self._resize()
 def minimize(self):
  self.root.overrideredirect(False);self.root.iconify();self.root.bind('<Map>',self._restore_window)
 def _restore_window(self,e):
  self.root.unbind('<Map>');self.root.after(100,lambda:self.root.overrideredirect(True))
 def resize_start(self,e):self.resz=(e.x_root,e.y_root,self.root.winfo_width(),self.root.winfo_height())
 def resize_move(self,e):
  if not self.maxed:
   x,y,w,h=self.resz;self.root.geometry(f'{max(1090,w+e.x_root-x)}x{max(710,h+e.y_root-y)}')
 def close(self):
  self._closing=True
  for v in (self.after_atlas,self.after_save,self.after_color):
   if v:
    try:self.root.after_cancel(v)
    except Exception:pass
  self._save();self.root.destroy()
 def choose_folder(self):
  init=self.destination if Path(self.destination).is_dir() else str(Path.home())
  d=filedialog.askdirectory(parent=self.root,initialdir=init,title='Select PCSX2/SLES-51473/replacements')
  if d:self.destination=d;self.dest_label.config(text=d);self._schedule_save()
 def _busy(self,v):
  self.busy=v;self.apply_btn.set_enabled(not v);self.restore_btn.set_enabled(not v)
  self.apply_btn.lbl.config(text='WORKING…' if v else 'APPLY')
 def apply(self):self._begin_ps('Apply')
 def restore(self):self._begin_ps('RestoreVanilla')
 def _begin_ps(self,action):
  if self.busy:return
  dest=Path(self.destination)
  if dest.name.lower()!='replacements' or dest.parent.name.upper()!='SLES-51473' or not dest.is_dir():
   self.set_status('Please choose an existing SLES-51473/replacements folder.',True);return
  if self.after_color:
   self.root.after_cancel(self.after_color);self._apply_selected_color()
  img=self.display.copy() if action=='Apply' else None
  self._busy(True);self.set_status('Applying texture…' if action=='Apply' else 'Removing texture replacement…')
  threading.Thread(target=self._ps_worker,args=(action,img,dest),daemon=True).start()
  self.root.after(110,self._poll_ps)
 def _ps_worker(self,action,img,dest):
  try:
   args=['powershell.exe','-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass',
         '-File',str(HERE/'Kya_Texture_Manager.ps1'),'-Action',action,'-Destination',str(dest)]
   if img is not None:
    work=HERE/'work';work.mkdir(exist_ok=True)
    out=work/NAME;temp=work/(NAME+'.pending')
    img.save(temp,format='PNG');os.replace(temp,out)
    args.extend(['-SourcePNG',str(out)])
   p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',
      timeout=50,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   if p.returncode:raise RuntimeError((p.stdout or 'PowerShell operation failed.')[-1500:])
   self.jobs.put(('ok',action,(p.stdout or '').strip()))
  except Exception as exc:self.jobs.put(('error',action,str(exc)))
 def _poll_ps(self):
  try:status,action,body=self.jobs.get_nowait()
  except queue.Empty:self.root.after(110,self._poll_ps);return
  self._busy(False)
  if status=='ok':
   self.set_status('Texture applied! Restart the game in PCSX2.' if action=='Apply' else 'Vanilla restored! Restart the game in PCSX2.')
  else:
   work=HERE/'work';work.mkdir(exist_ok=True)
   (work/'last_error.txt').write_text(body,encoding='utf-8')
   self.set_status('Operation failed. See work/last_error.txt.',True)
   self.error_box(body)
 def error_box(self,body):
  win=tk.Toplevel(self.root,bg=PANEL);win.title('Color Studio error');win.geometry('560x210')
  self.label(win,'PCSX2 update failed',13,ERR,True).pack(anchor='w',padx=13,pady=10)
  t=tk.Text(win,bg=NAV,fg=TXT,relief='flat',height=7,wrap='word')
  t.pack(fill='both',expand=True,padx=13);t.insert('1.0',body);t.config(state='disabled')
  Button(win,'CLOSE',win.destroy,'subtle',height=31).pack(fill='x',padx=13,pady=9)

if __name__=='__main__':
 root=tk.Tk()
 try:Studio(root);root.mainloop()
 except Exception:
  traceback.print_exc()
  try:
   from tkinter import messagebox
   messagebox.showerror('Kya Color Studio v4',traceback.format_exc())
  except Exception:pass
  raise
