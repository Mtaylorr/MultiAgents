import math
import random
import uuid
import numpy as np
from collections import defaultdict

import mesa
import tornado, tornado.ioloop
from mesa import space 
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from mesa.visualization.modules.ChartVisualization import ChartModule
from mesa.visualization.ModularVisualization import UserSettableParameter

from mesa.batchrunner import BatchRunner


dx=[1,1,0,-1, -1, -1,0,1]
dy=[0,1,1, 1, 0, -1, -1,-1]
angRanges = [22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5,400]
sameDir = 20
changeDir=50


class Barn(mesa.Model):

    def __init__(self, grid_width=50, grid_height=50,n_cows=30, n_team=5, corral_sz=5,n_obstacles=5):
        mesa.Model.__init__(self)
        self.space = mesa.space.MultiGrid(grid_width, grid_height, False)
        self.schedule = RandomActivation(self)

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.weight_empty = random.randint(1,10)
        self.weight_obstacle = -self.weight_empty
        self.obstacles = []
        self.teamCorral1 = []
        self.teamCorral2 = []
        self.score1 = 0
        self.score2 = 0
        self.n_cows= n_cows
        s= set()

        self.center1x = grid_width//2
        self.center1y = grid_height//4
        self.center2x = grid_width//2
        self.center2y = 3*grid_height//4
        self.corral_sz = corral_sz
        for i in range(self.center1x-corral_sz//2,self.center1x+corral_sz//2+1):
            for j in range(self.center1y-corral_sz//2,self.center1y+corral_sz//2+1):
                s.add((i,j))
                self.teamCorral1.append((i,j))
        for i in range(self.center2x-corral_sz//2,self.center2x+corral_sz//2+1):
            for j in range(self.center2y-corral_sz//2,self.center2y+corral_sz//2+1):
                s.add((i,j))
                self.teamCorral2.append((i,j))
        for _ in range(n_obstacles):
            x = int(random.random()* grid_width)
            y= int(random.random() * grid_height)
            while((x,y) in s):
                x = int(random.random()* grid_width)
                y= int(random.random() * grid_height)
            s.add((x,y))
            self.obstacles.append((x,y))
        for _ in range(n_cows):
            x = int(random.random()* grid_width)
            y= int(random.random() * grid_height)
            while((x,y) in s):
                x = int(random.random()* grid_width)
                y= int(random.random() * grid_height)
            s.add((x,y))
            self.schedule.add(Cow(x, y, int(uuid.uuid1()), self))
        for _ in range(n_team):
            for j in range(1,3):
                x = int(random.random()* grid_width)
                y= int(random.random() * grid_height)
                while((x,y) in s):
                    x = int(random.random()* grid_width)
                    y= int(random.random() * grid_height)
                s.add((x,y))
                self.schedule.add(Dog(x, y, int(uuid.uuid1()), self,j))

        self.dc = DataCollector({
            'Score1': lambda m : m.score1,
            'Score2' : lambda m : m.score2,
            'RemainingCows' : lambda m : m.n_cows-m.score1 - m.score2,

        })
        self.dc.collect(self)


    def step(self):
        self.dc.collect(self)
        self.schedule.step()
        if self.schedule.steps >= 1000:
            self.running = False

class Cow(mesa.Agent):
    def __init__(self, x, y, unique_id: int, model:Barn, rc = 9, rcn=3):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.w = random.random()*10
        self.model = model
        self.rc = rc
        self.rcn = rcn
        self.weight = random.randint(1,10)
        self.turn = random.randint(0,2)
        self.steps = 0
    def portrayal_method(self):
        r = 0.5
        color = "black"
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        self.steps+=1
        self.steps%=3
        if(self.steps!=self.turn):
            return 
        g = [[1 for i in range(self.rc)] for i in range(self.rc)]
        rx = self.rc//2
        ry = self.rc//2
        for obj in self.model.schedule.agent_buffer():
            x ,y = obj.pos
            if(abs(x-self.pos[0])<=self.rc//2 and abs(y-self.pos[1])<=self.rc//2):
                diffx = x-self.pos[0]
                diffy = y-self.pos[1]
                g[ry+diffy][rx+diffx]=obj
        for (x,y)  in self.model.obstacles : 
            if(abs(x-self.pos[0])<=self.rc//2 and abs(y-self.pos[1])<=self.rc//2):
                diffx = x-self.pos[0]
                diffy = y-self.pos[1]
                g[ry+diffy][rx+diffx]=-1
        middle = np.array((rx,ry))
        v = np.zeros(2)
        for i in range(self.rc):
            for j in range(self.rc):
                x = self.pos[0]-(rx-i)
                y = self.pos[1]-(ry-j)
                if(x<0 or x>=self.model.grid_width or y<0 or  y>=self.model.grid_height):
                    continue
                if i==rx and j==ry:
                    continue
                w=self.model.weight_empty
                if(isinstance(g[j][i],Dog)):
                    w=g[j][i].weight
                    
                elif isinstance(g[j][i],Cow) :
                    if(abs(i-rx)<=self.rcn//2  and abs(j-ry)<=self.rcn//2):
                        w  = -g[j][i].weight
                    else : 
                        w = g[j][i].weight
                else :
                    w*=g[j][i]
                dif = (np.array((i,j))-middle)
                
                v+=w*dif/(np.linalg.norm(dif))

        if(np.linalg.norm(v)<=1e-5):
            return
        
        v = v/np.linalg.norm(v)
        ang = np.angle(complex(v[0],v[1]))
        ang=ang*180/math.pi
        if(ang<0):
            ang=360+ang
        d = 0
        for i in range(len(angRanges)):
            if ang<=angRanges[i]:
                d=i%8
                break
        ni = rx+dx[d]
        nj = ry+dy[d]
        nx = self.pos[0]+dx[d]
        ny = self.pos[1]+dy[d]
        if nx>=0 and nx<self.model.grid_width and ny>=0 and  ny<self.model.grid_height:
            if(isinstance(g[nj][ni],int) and g[nj][ni]==1):
                if((nx,ny) in self.model.teamCorral1):
                    self.model.score1+=1
                    self.model.schedule.remove(self)
                elif ((nx,ny) in self.model.teamCorral2): 
                    self.model.score2+=1
                    self.model.schedule.remove(self)
                else : 
                    self.pos=(nx,ny)





            

class Dog(mesa.Agent):
    def __init__(self, x, y, unique_id: int, model:Barn, type: int, visibility = 17):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.w = random.random()*20
        self.type = type
        self.model = model
        self.visibility = visibility
        self.weight = random.randint(-300,-100)

    def portrayal_method(self):
        r = 0.8
        if(self.type==1):
            color = "red"
        else :
            color="blue"
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        cow = None 
        mnang = 500
        if(self.type==1):
            to_Cor = np.array((self.model.center1x, self.model.center1y), dtype=float)-np.array(self.pos, dtype=float)
        else :
            to_Cor = np.array((self.model.center2x, self.model.center2y), dtype=float)-np.array(self.pos, dtype=float)
        if(np.linalg.norm(to_Cor)>self.model.corral_sz//2):

            to_Cor =to_Cor/np.linalg.norm(to_Cor)
            v = np.zeros(2)
            for obj in self.model.schedule.agent_buffer():
                if(isinstance(obj, Cow)):
                    x ,y = obj.pos
                    if(abs(x-self.pos[0])<=self.visibility//2 and abs(y-self.pos[1])<=self.visibility//2):
                        to_Cow = (np.array((x, y))-np.array(self.pos)).astype(float)
                    else :
                        continue
                    to_Cow /=np.linalg.norm(to_Cow)
                    dot = np.sum(to_Cor*to_Cow)
                    ang = np.arccos(dot)
                    ang=ang*180/math.pi
                    if(ang<mnang):
                        mnang=ang
                        cow = obj
        if(cow is not None):
            x = cow.pos[0]
            y =  cow.pos[1]
            if(mnang<=sameDir):
                v = np.array((x,y)-np.array(self.pos))
                v = v/np.linalg.norm(v)
                ang = np.angle(complex(v[0],v[1]))
                ang=ang*180/math.pi
                if(ang<0):
                    ang=360+ang
                d = 0
                for i in range(len(angRanges)):
                    if ang<=angRanges[i]:
                        d=i%8
                        break
                nx = self.pos[0]+dx[d]
                ny = self.pos[1]+dy[d]
                if nx>=0 and nx<self.model.grid_width and ny>=0 and  ny<self.model.grid_height:
                    npos = (nx,ny)
                    if(npos in self.model.obstacles):
                        cow=None
                    cond=True
                    for obj in self.model.schedule.agent_buffer():
                        if(obj.pos[0]==nx and obj.pos[1]==ny):
                            cond=False
                            break
                    if(cond):
                        self.pos=(nx,ny)
            elif(mnang<=changeDir):
                v = np.array((-to_Cor[1], to_Cor[0]))
                to_Cow = np.array((cow.pos))-np.array(self.pos)
                det = to_Cor[0]*to_Cow[1] - to_Cor[1]*to_Cow[0]
                if(det<0):
                    v*=-1
                v = v/np.linalg.norm(v)
                ang = np.angle(complex(v[0],v[1]))
                ang=ang*180/math.pi
                if(ang<0):
                    ang=360+ang
                d = 0
                for i in range(len(angRanges)):
                    if ang<=angRanges[i]:
                        d=i%8
                        break
                nx = self.pos[0]+dx[d]
                ny = self.pos[1]+dy[d]
                if nx>=0 and nx<self.model.grid_width and ny>=0 and  ny<self.model.grid_height:
                    npos = (nx,ny)
                    if(npos in self.model.obstacles):
                        cow=None
                    cond=True
                    for obj in self.model.schedule.agent_buffer():
                        if(obj.pos[0]==nx and obj.pos[1]==ny):
                            cond=False
                            break
                    if(cond):
                        self.pos=(nx,ny)

            else : 
                cow=None

        if( cow is None):
            d = random.randint(0,7)
            nx = self.pos[0]+dx[d]
            ny = self.pos[1]+dy[d]
            if nx>=0 and nx<self.model.grid_width and ny>=0 and  ny<self.model.grid_height:
                npos = (nx,ny)
                if(npos in self.model.obstacles):
                    return
                cond=True
                for obj in self.model.schedule.agent_buffer():
                    if(obj.pos[0]==nx and obj.pos[1]==ny):
                        cond=False
                        break
                if(cond):
                    self.pos=(nx,ny)
        






class CanvasGrid(VisualizationElement):
    package_includes = ["GridDraw.js", "CanvasModule.js", "InteractionHandler.js"]

    def __init__(
        self,  
        grid_width=50,
        grid_height=50,
        canvas_width=800,
        canvas_height=800, instantiate=True,
    ):

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.identifier = "space-canvas"

        new_element = "new CanvasModule({}, {}, {}, {})".format(
            self.canvas_width, self.canvas_height, self.grid_width, self.grid_height
        )

        self.js_code = "elements.push(" + new_element + ");"
    
    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        grid_state = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = obj.pos[0]
                portrayal["y"] = obj.pos[1]
                grid_state[portrayal["Layer"]].append(portrayal)
        for (x,y)  in model.obstacles : 
            portrayal = { 
                "Filled": "true",
                "Color": "green",
                "Layer":1,
                "Shape":"rect",
                "w":0.9,
                "h":0.9,
                }
            if portrayal:
                portrayal["x"] = x
                portrayal["y"] = y
                grid_state[portrayal["Layer"]].append(portrayal)
        for (x,y)  in model.teamCorral1 : 
            portrayal = { 
                "Filled": "true",
                "Color": "#FEB2A2",
                "Layer":1,
                "Shape":"rect",
                "w":0.9,
                "h":0.9,
                }
            if portrayal:
                portrayal["x"] = x
                portrayal["y"] = y
                grid_state[portrayal["Layer"]].append(portrayal)

        for (x,y)  in model.teamCorral2 : 
            portrayal = { 
                "Filled": "true",
                "Color": "#9AFDFF",
                "Layer":1,
                "Shape":"rect",
                "w":0.9,
                "h":0.9,
                }
            
            if portrayal:
                portrayal["x"] = x
                portrayal["y"] = y
                grid_state[portrayal["Layer"]].append(portrayal)

        return grid_state

def run_single_server():
    server = ModularServer(Barn,
                           [CanvasGrid(),
                           ChartModule(series =[{'Label':"Score1","Color":"blue"},
                                                {"Label":"Score2","Color":"red"},
                                                {"Label":"RemainingCows","Color":"black"}]
                                                 ,data_collector_name="dc")],
                           "Barn",)
    server.port = 8521
    server.launch()
    tornado.ioloop.IOLoop.current().stop()


if __name__ == "__main__":
    run_single_server()
