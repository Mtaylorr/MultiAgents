import math
import random
import uuid
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

class Village(mesa.Model):

    def __init__(self, n_villagers, n_loupGrou, n_cleric, n_hunter):
        mesa.Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        for _ in range(n_villagers):
            self.schedule.add(Villager(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self))
        for _ in range(n_loupGrou):
            self.schedule.add(Villager(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self, True))
        for _ in range(n_cleric):
            self.schedule.add(Cleric(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self))
        for _ in range(n_hunter):
            self.schedule.add(Hunter(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self))
        self.dc = DataCollector({
            'Population': lambda m : m.getPopulationSize(),
            'Humans' : lambda m : m.getHumansSize(),
            'Werewolves' : lambda m : m.getWerewolvesSize(),
            'TransformedWerewolves' : lambda m : m.getTransformedWerewolvesSize(),

        })
        self.dc.collect(self)


    def getPopulationSize(self):
        return len([u for u in self.schedule.agent_buffer() if isinstance(u,Villager) ])

    def getHumansSize(self):
        return len([u for u in self.schedule.agent_buffer() if isinstance(u,Villager)and u.isLoupGarou==False ])

    def getWerewolvesSize(self):
        return len([u for u in self.schedule.agent_buffer() if isinstance(u,Villager)and u.isLoupGarou==True and u.isTransformed==False ])
    
    def getTransformedWerewolvesSize(self):
        return len([u for u in self.schedule.agent_buffer() if isinstance(u,Villager)and u.isTransformed==True ])


    def step(self):
        self.dc.collect(self)
        self.schedule.step()
        if self.schedule.steps >= 1000:
            self.running = False


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
                portrayal["x"] = ((obj.pos[0] - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.pos[1] - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation


def wander(x, y, speed, model):
    r = random.random() * math.pi * 2
    new_x = max(min(x + math.cos(r) * speed, model.space.x_max), model.space.x_min)
    new_y = max(min(y + math.sin(r) * speed, model.space.y_max), model.space.y_min)

    return new_x, new_y


class Villager(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village, isLoupGarou: bool = False):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
        self.isLoupGarou = isLoupGarou
        self.isTransformed=False

    def portrayal_method(self):
        if self.isLoupGarou : 
            color = "red"
        else:
            color = "blue"
        r = 3
        if self.isTransformed :
            r=6
        
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def cure(self):
        self.isLoupGarou=False

    def kill(self):
        self.model.schedule.remove(self)

    def makeLoupGarou(self):
        self.isLoupGarou=True

    def transform(self):
        self.makeLoupGarou()
        self.isTransformed=True

    def step(self):
        if self.isLoupGarou :
            if self.isTransformed==False  and random.random()<=0.1:
                self.transform()
        if self.isTransformed :
            attacked = [u for u in self.model.schedule.agent_buffer() if ((self.pos[0]-u.pos[0])**2 + (self.pos[1]-u.pos[1])**2 <=40.0**2)]
            for u in attacked :
                if isinstance(u, Villager):
                    u.makeLoupGarou()
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)
        
class Cleric(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model

    def portrayal_method(self):
        color = "green"
        r = 3
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        toCure = [u for u in self.model.schedule.agent_buffer() if ((self.pos[0]-u.pos[0])**2 + (self.pos[1]-u.pos[1])**2 <=30.0**2)]
        for u in toCure :
            if isinstance(u, Villager) and u.isTransformed==False:
                u.cure()
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)

class Hunter(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model

    def portrayal_method(self):
        color = "black"
        r = 3
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        toKill = [u for u in self.model.schedule.agent_buffer() if ((self.pos[0]-u.pos[0])**2 + (self.pos[1]-u.pos[1])**2 <=40.0**2)]
        for u in toKill :
            if isinstance(u, Villager) and u.isTransformed==True:   
                u.kill()
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)

def run_single_server():
    server = ModularServer(Village,
                           [ContinuousCanvas(),
                           ChartModule(series =[{'Label':"Population","Color":"orange"},
                                                {"Label":"Humans","Color":"blue"},
                                                {"Label":"Werewolves","Color":"red"},
                                                {"Label":"TransformedWerewolves","Color":"green"}]
                                                 ,data_collector_name="dc")],
                           "Village",
                           {"n_villagers": UserSettableParameter("slider","n_villagers",15, 0,20),
                            "n_loupGrou":UserSettableParameter("slider","n_loupGrou",5, 0,20),
                            "n_cleric":UserSettableParameter("slider","n_cleric",1, 0,20),
                            "n_hunter":UserSettableParameter("slider","n_hunter",2, 0,20)})
    server.port = 8521
    server.launch()
    tornado.ioloop.IOLoop.current().stop()

def run_batch():
    params = {
        "n_villagers":[50],
        "n_loupGrou":[5],
        "n_cleric": list(range(0,6,1)),
        "n_hunter": [1],
    }  
    model_reporter  = {
        'Population': lambda m : m.getPopulationSize(),
        'Humans' : lambda m : m.getHumansSize(),
        'Werewolves' : lambda m : m.getWerewolvesSize(),
        'TransformedWerewolves' : lambda m : m.getTransformedWerewolvesSize(),
    }
    br = BatchRunner(Village, variable_parameters = params, model_reporters=model_reporter)
    br.run_all()
    df = br.get_model_vars_dataframe()
    df.to_csv("Experiment.csv", index=False)


if __name__ == "__main__":
    run_batch()
    #run_single_server()
