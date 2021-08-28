from os import write
import struct
import random
from obj import Obj
from collections import namedtuple

V2 = namedtuple('Point2D', ['x', 'y'])
V3 = namedtuple('Point3D', ['x', 'y', 'z'])

def bbox(A, B, C):
    xs = [A.x, B.x, C.x]
    xs.sort()
    ys = [A.y, B.y, C.y]
    ys.sort()
    return xs[0], xs[-1], ys[0], ys[-1]

#escribir en bytes
def char(c):
    return struct.pack('=c',c.encode('ascii'))

#escribir en bytes
def word(w):
    #short
    return struct.pack('=h',w)

#escribir en bytes
def dword(w):
    #long
    return struct.pack('=l',w)

def color(r,g,b):
    return bytes([b,g,r])

def cross(v0, v1):
    cx = v0.y * v1.z - v0.z * v1.y
    cy = v0.z * v1.x - v0.x * v1.z
    cz = v0.x * v1.y - v0.y * v1.x
    return V3(cx, cy, cz)

def barycentric(A, B, C, P):    
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )
    
    if cz == 0:
        return -1, -1, -1
    
    u = cx/cz
    v = cy/cz
    w = 1 - (u + v)
    
    return w, v, u

def sub(v0, v1):
    return V3(
        v0.x - v1.x,
        v0.y - v1.y,
        v0.z - v1.z
    )

def length(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2) ** 0.5

def norm(v0):
    l = length(v0)
    
    if l == 0:
        return V3(0, 0, 0)
    
    return V3(
        v0.x / l,
        v0.y / l,
        v0.z / l
    )

def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def glClearColor(r,g,b):
    return bytes([b,g,r])

BLACK = color(0,0,0)
space_color =  color(0, 0, 10)
WHITE = color(255,255,255)
clear_color = glClearColor(12, 50, 229)

def glInit(width, height):
    glCreateWindow(width, height)
    
def glCreateWindow(width, height):
    global framebuffer, zbuffer
    framebuffer = [
            [space_color for x in range(width)]
            for y in range(height)
        ]
    
    zbuffer = [
            [-999999 for x in range(width)]
            for y in range(height)
        ]    

def glViewport(xV, yV, widthV, heightV):
    global viewPortX, viewPortY, viewWidth, viewHeight
    viewPortX = xV
    viewPortY = yV
    viewWidth = widthV
    viewHeight = heightV
    
def glVertex(x_v, y_v, color=None):
    framebuffer[y_v][x_v]=color or current_color

def glLine(x0, y0, x1, y1):
    #x0 = int((x0 + 1) * (viewWidth / 2) + viewPortX)
    #y0 = int((y0 + 1) * (viewWidth / 2) + viewPortX)
    #x1 = int((x1 + 1) * (viewWidth / 2) + viewPortX)
    #y1 = int((y1 + 1) * (viewWidth / 2) + viewPortX)
    
    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    steep = dy > dx

    if steep:      
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    offset = 0 * 2 * dx
    threshold = 0.5
    y = y0

    # y = mx + b
    points = []
    for x in range(x0, x1+1):
        if steep:
            points.append((y, x))
        else:
            points.append((x, y))

        offset += 2 * dy
        if offset >= threshold:
            y += 1 if y0 < y1 else -1
            threshold += 1 * 2 * dx
        
    for point in points:        
        glVertex(*point)

def glLineT(A, B):
    '''
    x0 = round(((A.x + 1) * (viewWidth / 2) + viewPortX)/100)
    y0 = round(((A.y + 1) * (viewHeight / 2) + viewPortY)/100)
    x1 = round(((B.x + 1) * (viewWidth / 2) + viewPortX)/100)
    y1 = round(((B.y + 1) * (viewHeight / 2) + viewPortY)/100)
    '''
    x0 = A.x
    y0 = A.y
    x1 = B.x
    y1 = B.y    
    
    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    steep = dy > dx

    if steep:      
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dy = abs(y1 - y0)
    dx = abs(x1 - x0)

    offset = 0 * 2 * dx
    threshold = 0.5
    y = y0

    # y = mx + b
    points = []
    for x in range(x0, x1+1):
        if steep:
            points.append((y, x))
        else:
            points.append((x, y))

        offset += 2 * dy
        if offset >= threshold:
            y += 1 if y0 < y1 else -1
            threshold += 1 * 2 * dx
        
    for point in points:        
        glVertex(*point)

def glFinish(filename, width, height):
    with open(filename, "bw") as f:
    #file header 14 bytes
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + 3 *(width * height)))
        f.write(dword(0))
        f.write(dword(14 + 40))

        #info header 40 bytes
        f.write(dword(40))
        f.write(dword(width))
        f.write(dword(height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword( 3 *(width * height)))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        #bitmap
        for y in range(height):
            for x in range(width):
                f.write(framebuffer[y][x])

def Transform(v, translate, scale):
    return V3(
        round((v[0] + translate[0]) * scale[0]),
        round((v[1] + translate[1]) * scale[1]),
        round((v[2] + translate[2]) * scale[2])
    )

def shader(A, B, C, grey, kind):
    c1 = 0
    c2 = 0
    c3 = 0
    if kind == 'P':
        if (A.y > 380 and A.y < 400) or (B.y > 380 and B.y < 400) or (C.y > 380 and C.y < 400):
            c1 = 1
            c2 = 1
            c3 = 1 - 0.22
        elif (A.y > 360 and A.y <= 380) or (B.y > 360 and B.y <= 380) or (C.y > 360 and C.y <= 380):
            c1 = 1
            c2 = 1 
            c3 = 1
        elif (A.y > 330 and A.y <= 360) or (B.y > 330 and B.y <= 360) or (C.y > 330 and C.y <= 360):
            c1 = 1 - 0.63
            c2 = 1 - 0.92
            c3 = 1 - 0.95
        elif (A.y > 240 and A.y <= 330) or (B.y > 240 and B.y <= 330) or (C.y > 240 and C.y <= 330):
            c1 = 1
            c2 = 1
            c3 = 1
        else:
            c1 = (1 - 0.07) * 0.95
            c2 = (1 - 0.11) * 0.95
            c3 = (1 - 0.40) * 0.95
        return color(round(grey*c1), round(grey*c2), round(grey*c3))
    elif kind == 'R':
        if A.x < 290 and B.x < 280 and C.x < 280:
            return space_color
        else:
            return color(grey, grey, grey)
    else:
        return color(grey, grey, grey)

def load(filename, translate, scale, kind):
    model = Obj(filename)
    
    light1 = V3(0.35, 0, 0.45)
    light2 = V3(0, 0.6, 0)
    
    for face in model.faces:
        vcount = len(face)
        
        if vcount == 3:
            f1 = face[0][0] - 1
            f2 = face[1][0] - 1
            f3 = face[2][0] - 1
            
            A = Transform(model.vertices[f1], translate, scale)
            B = Transform(model.vertices[f2], translate, scale)
            C = Transform(model.vertices[f3], translate, scale)
            
            normal = norm(cross(
                sub(B, A),
                sub(C, A)
            ))
            
            if kind == 'P' or kind == 'A':
                intensity =  dot(normal, light1)
                # 1 si esta en frente
                # 0 si esta de lado
                                
                grey = round(255 * intensity)
                
                if intensity < 0:
                    continue
                                
                triangle(A, B, C, kind, shader(A, B, C, grey, kind))
            else:
                intensity =  dot(normal, light2)
                # 1 si esta en frente
                # 0 si esta de lado
                                
                grey = round(255 * intensity)
                
                if intensity < 0:
                    continue
                                
                triangle(A, B, C, kind, shader(A, B, C, grey, kind))
                
        
        elif vcount == 4:
            f1 = face[0][0] - 1
            f2 = face[1][0] - 1
            f3 = face[2][0] - 1 
            f4 = face[3][0] - 1
            
            A = Transform(model.vertices[f1], translate, scale)
            B = Transform(model.vertices[f2], translate, scale)
            C = Transform(model.vertices[f3], translate, scale)
            D = Transform(model.vertices[f4], translate, scale)
            
            normal = norm(cross(
                sub(A, B),
                sub(B, C)
            ))
            
            intensity =  dot(normal, light)
            # 1 si esta en frente
            # 0 si esta de lado
                            
            grey = round(255 * intensity)
            
            if intensity < 0:
                continue
                            
            triangle(A, B, C,
                color(
                    grey,
                    grey,
                    grey
                )
            )
            
            triangle(A, C, D,
                color(
                    grey,
                    grey,
                    grey
                )
            )
            
def triangle_wireframe(A, B, C):
    glLine(A, B)
    glLine(B, C)
    glLine(C, A)

def fragment_shader(x, y, colorc, kind):
    b, g, r = colorc
    if kind == 'P':
        center_x, center_y = 530, 385
        center_x1, center_y1 = 470, 240 
        #-----------------------------Parte de arriba--------------------
        if y > (460 + random.randint(0, 10)):
            return color(int(r*0.75),
                         int(g*0.75),
                         int(b*0.75)
                    )
        elif y > 420 and y <= 460:
            if random.randint(0, 5) == 2:
                return color(int(r*0.75),
                             int(g*0.75),
                             int(b*0.75)
                        )
            else:
                return color(r, g, b)
        #-----------------------------Primera Franja--------------------
        elif y > (380 + random.randint(0, 1)) and y < (385 + random.randint(0, 1)) and x > (350 + random.randint(0, 1)) and x < (400 + random.randint(0, 30)):
            return color(int(r*(1 - round(random.uniform(0.60, 0.70), 2)*0.44)),
                         int(g*(1 - round(random.uniform(0.57, 0.60), 2))),
                         int(b*(1 - 0.57))
                    )
        elif ((x + random.randint(0, 5)) - center_x)**2/160 + ((y + random.randint(0, 3)) - center_y)**2/15 <= 1 :
            return color(int(r*(1 - round(random.uniform(0.60, 0.70), 2)*0.44)),
                         int(g*(1 - round(random.uniform(0.57, 0.60), 2))),
                         int(b*(1 - 0.57))
                    )
        elif y > (395 - random.randint(0, 2)) and y < (408 - random.randint(0, 2)):
            return color(int(r*(1 - round(random.uniform(0.60, 0.70), 2)*0.44)),
                         int(g*(1 - round(random.uniform(0.57, 0.60), 2))),
                         int(b*(1 - 0.57))
                    )
        elif y > 370 and y < 400:
            if random.randint(0, 10) == 2:
                return color(int(r*(1 - round(random.uniform(0.08, 0.09), 2))),
                             int(g*(1 - round(random.uniform(0.34, 0.35), 2))),
                             int(b*(1 - 0.57))
                        )
            else:
                return color(r, g, b)
        #------------------------------Segunda Franja------------------------
        elif y > 335 and y < 365:
            if random.randint(0, 10) == 2:
                return color(int(r * 0.8),
                             int(g * 0.8),
                             int(b * 0.8)
                        )
            elif random.randint(0, 6) == 3:
                return color(int((r - 0.23) * 0.9),
                             int((g - 0.20) * 0.9),
                             int(b)
                        )
            else:
                return color(r, g, b)
        #-------------------------Tercera Franja-----------------------------
        elif y > 310 and y < 335 and x > 500:
            if random.randint(0, 20) == 2:
                return color(int(r + 73),
                             int(g + 50),
                             int(b + 37)
                        )
            else:
                return color(r, g, b)
        #-------------------------Cuarta Franja------------------------------
        elif (x - random.randint(0, 2) - center_x1)**2/50 + (y - random.randint(0, 2) - center_y1)**2/15 <= 1:
            return color(int(r),
                         int(g*(1 - 0.67)*0.77),
                         int(b*0)
                        )
        elif (x - center_x1)**2/250 + (y - center_y1)**2/150 <= 1:
            return color(int(r),
                         int(g*(1 - 0.60)),
                         int(b*0)
                        )
        elif (x - center_x1)**2/500 + (y - (center_y1+3))**2/250 <= 1:
            return color(int(r*(1 - 0.10) * 0.89),
                         int(g*(1 - 0.20) * 0.89),
                         int(b*(1 - 0.41) * 0.89)
                        )
        elif (y > 240 - random.randint(0, 3) and y < 260  - random.randint(0, 3) and x > 470):
            return color(int(r * 0.6),
                         int(g*(1 - 0.24) * 0.6),
                         int(b*(1 - 0.31) * 0.6)
                        )
        elif (y > 240 - random.randint(0, 3) and y < 270 - random.randint(0, 3)) or (y > 229 and y < 270 - random.randint(0, 3) and x > 470):
            return color(int(r*(1 - 0.10) * 0.89),
                         int(g*(1 - 0.20) * 0.89),
                         int(b*(1 - 0.41) * 0.89)
                        )
        #-------------------------Parte de abajo--------------------------------
        elif y < 205 - random.randint(0, 7):
            return color(int(r * 0.5),
                         int(g * 0.5),
                         int(b * 0.5)
                        )
        else:
            return colorc
    else:
        return colorc
            
def triangle(A, B, C, kind, color=None):
    
    xmin, xmax, ymin, ymax = bbox(A, B, C)
    
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            P = V2(x, y)
            w, v, u = barycentric(A, B, C, P)
            if w < 0 or v < 0 or u < 0:
                continue
            
            z = A.z * w + B.z * v + C.z * u
            
            if z > zbuffer[x][y]:
                color2 = fragment_shader(x, y, color, kind)
                glVertex(x, y, color2)
                zbuffer[x][y] = z

width = 800
height = 600
i = 0
j = 0
slide_x = 0

glInit(width, height)
while i < 800:
    glVertex(random.randint(1, 790), random.randint(1, 590), WHITE)
    i += 1


load('./models/sphere.obj', (1.4, 1.1, 0), (300, 300, 150), 'P')
load('./models/sphere.obj', (1.06, 16, 0.05), (380, 20, 200), 'R')
while j < 15:
    load('./models/sphere.obj', (17.5+slide_x, 29 + round(random.uniform(0.00, 0.8), 2), 8), (15+random.randint(0, 1), 10, 10), 'A')
    slide_x += 1.3
    j += 1

glFinish("Jupiter.bmp", width, height)
