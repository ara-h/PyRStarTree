from tkinter import *
from tkinter import ttk

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from pyrstar import rtree
from pyrstar import rectangle as rct

import pandas as pd

#------------------R*-tree example data----------------------------------------#

# data1 = {
# 1 : [2.0,9.0],
# 2 : [3.0, 4.0],
# 3 : [-1.0, -3.2],
# 4 : [-12.0, 8.0],
# 5 : [14.0, -5.8]
# }
#
# rt_1 = rtree.RStarTree(children=[],is_leaf=True,point_data=data1)


df = pd.read_csv('visual/generated_data.csv',index_col=0)

data2 = [x for x in enumerate(df.values.tolist())]

rt2cursor = rtree.create_tree_from_pts(data2)

rt_2 = rt2cursor.root





#------------------Displaying the R*-tree--------------------------------------#

root = Tk()
root.title("An R*-Tree")

canvas_width = 512
canvas_height = 512

canvas = Canvas(root, width=canvas_width, height=canvas_height, background='gray75')
canvas.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


# In tk's canvas, origin (0,0) is top-left corner. Coordinates express pixels
# away from origin in each axis.

# Define parameters to map object space to pixel space

# x bounds
L_x = -128.0
U_x = 128.0

# y bounds
L_y = -128.0
U_y = 128.0

# Map object space to pixel space

def to_tk_coord(x,y):
    u = round( canvas_width *  (x - L_x) / (U_x - L_x) )
    v = round( canvas_height *  (U_y - y) / (U_y - L_y) )
    return u, v


def draw_rect(rect, color):
    """ rect should be 2D """
    mx, my = rect.minima[0], rect.minima[1]
    Mx, My = rect.maxima[0], rect.maxima[1]
    mu, mv = to_tk_coord(mx, my)
    Mu, Mv = to_tk_coord(Mx, My)

    canvas.create_rectangle(mu, Mv, Mu, mv, outline=color)


def draw_pts(pts):
    """
    pts: list of 2d pts
    """
    for pt in pts:
        u,v = to_tk_coord(pt[0],pt[1])
        canvas.create_oval(u-1,v-1,u+1,v+1,fill="black")


def draw_leaf(rt_leaf):
    draw_rect(rt_leaf.key, "SpringGreen4")
    draw_pts(rt_leaf.get_points())


def draw_r_tree(rt, lvl = 0):
    """
    draw the rtree
    """
    # alternate colors between levels
    a = lvl % 3

    if a == 0:
        c = "blue4"
    elif a == 1:
        c = "gold"
    else:
        c = "red3"

    if rt.is_leaf:
        draw_leaf(rt)
    else:
        draw_rect(rt.key, c)

    for ch in rt.children:
        draw_r_tree(ch, lvl + 1)

draw_r_tree(rt_2)


#------------------Test rectangle overlap--------------------------------------#

# R1 = rct.Rectangle([-32,-32],[0,0])
# R2 = rct.Rectangle([-16,-16],[16,16])
#
# draw_rect(R1)
# draw_rect(R2)

#------------------Tkinter's main loop-----------------------------------------#

root.mainloop()
