import copy

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from helpers import get_map, convert_to_2d_array, get_moves, Dispatch

app = FastAPI()

# Allow CORS for all origins (you might want to restrict this in a production environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Define models
class Coordinates(BaseModel):
    x: int
    y: int


class Mine(BaseModel):
    id: int
    coordinates: Coordinates


class RoverStatus(str, Enum):
    NOT_STARTED = "Not Started"
    FINISHED = "Finished"
    MOVING = "Moving"
    ELIMINATED = "Eliminated"


class Rover(BaseModel):
    id: int
    status: RoverStatus
    latest_position: Coordinates
    commands: List[str]


class RoverCreate(BaseModel):
    commands: str


# Define your data storage
mines = []
mines_db = {}
rovers_db = {}

# Initialize
array, rows, cols = get_map('map.txt')
map_array = convert_to_2d_array(array, int(cols), int(rows))


def create_mines():
    for y, row in enumerate(map_array):
        for x, cell in enumerate(row):
            if cell == 1:
                serial_number = hash((x * 13) * 31 + (y * 23) * 37)
                mines.append(Mine(id=serial_number, coordinates=Coordinates(x=x, y=y)))
                # Add mine to mines_db
                mines_db[serial_number] = {"x": x, "y": y}


create_mines()


def init_rovers():
    for i in range(10):
        moves = get_moves(f'https://coe892.reev.dev/lab1/rover/{i + 1}')
        rover = Rover(id=i + 1, status="Not Started", latest_position=Coordinates(x=0, y=0), commands=list(moves))
        rovers_db[i + 1] = rover


init_rovers()


# Define endpoints
@app.get("/map")
def get_map():
    print("returned: " + str(map_array))
    return map_array


@app.put("/map")
def update_map(height: int, width: int):
    global mines, mines_db
    global map_array
    map_array = convert_to_2d_array([str(cell) for row in map_array for cell in row], width, height)
    mines.clear()
    mines_db.clear()
    create_mines()

    return {"message": "Map updated successfully"}


@app.get("/mines")
def get_mines():
    return mines


@app.get("/mines/{id}")
def get_mine_by_id(id: int):
    for mine in mines:
        if mine.id == id:
            return mine
    return {"message": "Mine not found"}


@app.delete("/mines/{id}")
def delete_mine(id: int):
    global map_array
    for mine in mines:
        if mine.id == id:
            mines.remove(mine)
            map_array[mine.coordinates.x][mine.coordinates.y] = 0
            return {"message": "success"}
    return {"message": "Mine not found"}


@app.post("/mines")
def create_mine(mine: Mine):
    x = mine.coordinates.x
    y = mine.coordinates.y
    serial_number = hash((x * 13) * 31 + (y * 23) * 37)
    mine.id = serial_number
    map_array[x][y] = 1
    mines.append(mine)
    return mine


@app.put("/mines/{id}", response_model=Mine)
def update_mine(id: int, mine: Mine):
    serial_number = hash((mine.coordinates.x * 13) * 31 + (mine.coordinates.y * 23) * 37)
    for old_mine in mines:
        if old_mine.id == id:
            map_array[old_mine.coordinates.x][old_mine.coordinates.y] = 0
            old_mine.coordinates = mine.coordinates
            map_array[mine.coordinates.x][mine.coordinates.y] = 1
            mine.id = serial_number
    return mine


@app.get("/rovers", response_model=List[Rover])
def get_rovers():
    return list(rovers_db.values())


@app.get("/rovers/{id}", response_model=Rover)
def get_rover_by_id(id: int):
    rover = rovers_db.get(id)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")
    return rover


@app.post("/rovers", response_model=Rover)
def create_rover(rover: RoverCreate):
    new_id = max(rovers_db.keys(), default=0) + 1
    new_rover = Rover(id=new_id, status="Not Started", latest_position=Coordinates(x=0, y=0),
                      commands=list(rover.commands))
    rovers_db[new_id] = new_rover
    return new_rover


@app.delete("/rovers/{id}", response_model=Rover)
def delete_rover(id: int):
    rover = rovers_db.pop(id, None)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")
    return rover


@app.put("/rovers/{id}", response_model=Rover)
def send_commands_to_rover(id: int, commands: str):
    rover = rovers_db.get(id)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")
    # Update the commands for the rover
    rover.commands = list(commands)

    return rover


@app.post("/rovers/{id}/dispatch")
def dispatch_rover(id: int):
    global map_array
    rover = rovers_db.get(id)
    if not rover:
        raise HTTPException(status_code=404, detail="Rover not found")

    # Get the array and commands from the rover
    array = copy.deepcopy(map_array)
    commands = rover.commands

    # Create an instance of the Dispatch class
    dispatch = Dispatch(array, commands)

    # Start traversing the map
    dispatch.startTraverse()

    # Update rover status to "Finished" after dispatch
    rover.status = dispatch.roverState
    rover.latest_position = Coordinates(x=dispatch.roverPosition[0], y=dispatch.roverPosition[1])
    rovers_db[id] = rover
    print(rover)

    return rover
