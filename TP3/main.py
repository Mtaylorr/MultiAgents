import enum
import math
import random
import uuid
from enum import Enum
import matplotlib.pyplot as plt

import mesa
import numpy as np
from collections import defaultdict

import mesa.space
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import VisualizationElement, ModularServer
from mesa.visualization.modules import ChartModule

MAX_ITERATION = 100
PROBA_CHGT_ANGLE = 0.01


def move(x, y, speed, angle):
    return x + speed * math.cos(angle), y + speed * math.sin(angle)


def go_to(x, y, speed, dest_x, dest_y):
    if np.linalg.norm((x - dest_x, y - dest_y)) < speed:
        return (dest_x, dest_y), 2 * math.pi * random.random()
    else:
        angle = math.acos((dest_x - x)/np.linalg.norm((x - dest_x, y - dest_y)))
        if dest_y < y:
            angle = - angle
        return move(x, y, speed, angle), angle


class MarkerPurpose(Enum):
    DANGER = enum.auto(),
    INDICATION = enum.auto()


class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500,
                 canvas_width=500, instantiate=True):
        VisualizationElement.__init__(self)
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if (instantiate):
            new_element = ("new Simple_Continuous_Module({}, {},'{}')".
                           format(self.canvas_width, self.canvas_height, self.identifier))
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        representation = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.mines:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.markers:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.obstacles:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.quicksands:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation


class Obstacle:  # Environnement: obstacle infranchissable
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "black",
                     "r": self.r}
        return portrayal


class Quicksand:  # Environnement: ralentissement
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "olive",
                     "r": self.r}
        return portrayal


class Mine:  # Environnement: élément à ramasser
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "black",
                     "r": 2}
        return portrayal


class Marker:  # La classe pour les balises
    def __init__(self, x, y, purpose, direction=None):
        self.x = x
        self.y = y
        self.purpose = purpose
        if purpose == MarkerPurpose.INDICATION:
            if direction is not None:
                self.direction = direction
            else:
                raise ValueError("Direction should not be none for indication marker")

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "red" if self.purpose == MarkerPurpose.DANGER else "green",
                     "r": 2}
        return portrayal


class Robot(Agent):  # La classe des agents
    def __init__(self, unique_id: int, model: Model, x, y, speed, sight_distance, angle=0.0):
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.speed = speed
        self.lastspeed  = speed
        self.sight_distance = sight_distance
        self.angle = angle
        self.counter = 0

    def ChangeRandomAngle(self):
        self.angle = random.random() * 2 * math.pi

    def intersect(self, other, newx, newy):
        return np.linalg.norm((newx - other.x,newy-other.y))<=other.speed or np.linalg.norm((self.x - other.x,self.y-other.y))<=other.speed


    def PossibleNextPosition(self, newx, newy):
        if(newx<0 or newy<0 or newx>=500 or newy>=500):
            return False
        cond=True
        for robot in self.model.schedule.agent_buffer() : 
            if robot ==self : 
                continue
            if(np.linalg.norm((self.x - robot.x,self.y-robot.y))<=self.sight_distance and self.intersect(robot, newx, newy)):
                cond=False
                break
        for obs in self.model.obstacles : 
            if(np.linalg.norm((newx - obs.x,newy-obs.y))<=obs.r) : 
                cond=False
                break
        return cond
    def  putDangerMarker(self):
        self.model.markers.append(Marker(self.x, self.y,MarkerPurpose.DANGER))
        

    def putIndicationMarkers(self, positions):
        for (x,y) in positions : 
            self.model.markers.append(Marker(x, y,MarkerPurpose.INDICATION,self.angle))

    def updCounter(self):
        self.counter=self.speed//2

    def step(self):
        self.counter = max((self.counter-1,0))
        # Détruire les mines
        idxToRmv = []
        indicationMarkers = []
        for (i,mine) in enumerate(self.model.mines) : 
            if(abs(self.x-mine.x)<1e-3 and abs(self.y-mine.y)<1e-3):
                idxToRmv.append(i)
                indicationMarkers.append((mine.x,mine.y))
                self.updCounter()
                

        self.model.mines= [self.model.mines[i] for i in range(len(self.model.mines)) if i not in idxToRmv]
        
        idxToRmv = []
        for (i,marker) in enumerate(self.model.markers) : 
            if(abs(self.x-marker.x)<1e-3 and abs(self.y-marker.y)<1e-3):
                idxToRmv.append(i)
        self.model.markers= [self.model.markers[i] for i in range(len(self.model.markers)) if i not in idxToRmv]
                

        self.model.mines= [self.model.mines[i] for i in range(len(self.model.mines)) if i not in idxToRmv]
        
        # Diminuer la vitesse s'il trouve dans un environnement ralentissant
        speed  = self.speed
        for ralent in self.model.quicksands : 
            
            if np.linalg.norm((self.x - ralent.x,self.y-ralent.y)) <=ralent.r :
                speed = speed / 2 
                self.model.quicksandsCounter += 1
                
        

        if(speed == self.speed and self.lastspeed !=self.speed ) : 
            self.putDangerMarker()
            self.updCounter()
        self.lastspeed = speed
        # changement de l'angle aléatoirement
        if random.random() <= PROBA_CHGT_ANGLE : 
            self.ChangeRandomAngle()
        
        # Détecter les mines
        for mine in  self.model.mines : 
            if np.linalg.norm((self.x - mine.x,self.y-mine.y)) <=self.sight_distance  : 
                (newx , newy) , angle = go_to(self.x, self.y, speed, mine.x, mine.y)
                if self.PossibleNextPosition(newx,newy)  : 
                    self.x = newx
                    self.y = newy
                    self.angle = angle 
                    self.putIndicationMarkers(indicationMarkers)
                    return
        if(self.counter>0):
            print(self.counter)
        if(self.counter==0):
            idxToRmv = []
            for marker in  self.model.markers : 
                if np.linalg.norm((self.x - marker.x,self.y-marker.y)) <=self.sight_distance  : 
                    (newx , newy) , angle = go_to(self.x, self.y, speed, marker.x, marker.y)
                    if self.PossibleNextPosition(newx,newy)  : 
                        if(marker.purpose==MarkerPurpose.INDICATION):
                            self.x = newx
                            self.y = newy
                            r = random.random()
                            r = int (r>0.5)
                            if r==0:
                                r=-1
                            self.angle = angle + r*math.pi/2 
                            self.angle%=math.pi
                            self.putIndicationMarkers(indicationMarkers)
                            return
                        else : 
                            self.x = newx
                            self.y = newy
                            self.angle = -angle
                            while self.angle<0: 
                                self.angle+=2*math.pi
                            self.putIndicationMarkers(indicationMarkers)
                            return
        newx , newy = move(self.x, self.y, self.speed, self.angle)
        while not self.PossibleNextPosition(newx,newy):
            self.ChangeRandomAngle()
            newx , newy = move(self.x, self.y, speed, self.angle)

        self.x , self.y = move(self.x, self.y, speed, self.angle)
        self.putIndicationMarkers(indicationMarkers)
         
    def portrayal_method(self):
        portrayal = {"Shape": "arrowHead", "s": 1, "Filled": "true", "Color": "Red", "Layer": 3, 'x': self.x,
                     'y': self.y, "angle": self.angle}
        return portrayal


class MinedZone(Model):
    collector = DataCollector(
        model_reporters={"Mines": lambda model: len(model.mines),
                         "Danger markers": lambda model: len([m for m in model.markers if
                                                          m.purpose == MarkerPurpose.DANGER]),
                         "Indication markers": lambda model: len([m for m in model.markers if
                                                          m.purpose == MarkerPurpose.INDICATION]),
                         "Steps in quickSand": lambda model : model.quicksandsCounter,},
        agent_reporters={})

    def __init__(self, n_robots, n_obstacles, n_quicksand, n_mines, speed):
        Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        self.mines = []  # Access list of mines from robot through self.model.mines
        self.markers = []  # Access list of markers from robot through self.model.markers (both read and write)
        self.obstacles = []  # Access list of obstacles from robot through self.model.obstacles
        self.quicksands = []  # Access list of quicksands from robot through self.model.quicksands
        for _ in range(n_obstacles):
            self.obstacles.append(Obstacle(random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_quicksand):
            self.quicksands.append(Quicksand(random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_robots):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.schedule.add(
                Robot(int(uuid.uuid1()), self, x, y, speed,
                      2 * speed, random.random() * 2 * math.pi))
        for _ in range(n_mines):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.mines.append(Mine(x, y))
        self.datacollector = self.collector
        self.cumulativeMines = [0]
        self.initialCountMines = len(self.mines)
        self.quicksandsCounter = 0

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.cumulativeMines.append(self.initialCountMines-len(self.mines))
        if not self.mines:
            plt.plot(list(range(len(self.cumulativeMines))),self.cumulativeMines)
            plt.xlabel("Step")
            plt.ylabel("Cumulative mines count")
            plt.savefig('CumulativeMinesCount.png')
            print("Saved Cumualtive mines count figure ..")
            f = open("StepCountTillEnd.txt",'a')
            f.write(str(len(self.cumulativeMines))+"\n")
            f.close()
            print("Saved Number of steps ..")
            self.running = False


def run_single_server():
    chart = ChartModule([{"Label": "Mines",
                          "Color": "Orange"},
                         {"Label": "Danger markers",
                          "Color": "Red"},
                         {"Label": "Indication markers",
                          "Color": "Green"},
                          {"Label": "Steps in quickSand",
                          "Color": "black"}
                         ],
                        data_collector_name='datacollector')
    server = ModularServer(MinedZone,
                           [ContinuousCanvas(),
                            chart],
                           "Deminer robots",
                           {"n_robots": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of robots", 7, 3,
                                                                       15, 1),
                            "n_obstacles": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of obstacles", 5, 2, 10, 1),
                            "n_quicksand": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of quicksand", 5, 2, 10, 1),
                            "speed": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Robot speed", 15, 5, 40, 5),
                            "n_mines": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of mines", 15, 5, 30, 1)})
    server.port = 8521
    server.launch()


if __name__ == "__main__":
    run_single_server()
