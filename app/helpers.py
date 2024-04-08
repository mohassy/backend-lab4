import requests


def get_moves(url):
    try:
        response = requests.get(url)
        data = response.json()
        moves = data['data']['moves']
        return moves
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_map(map_path):
    with open("map.txt", "r") as f:
        rowsAndColumns = f.readline().split()
        rows = rowsAndColumns[0]
        columns = rowsAndColumns[1]
        array = []
        for line in f:
            array = array + line.split()
    return array, rows, columns


def convert_to_2d_array(numbers, cols, rows):
    if len(numbers) != cols * rows:
        raise ValueError("Number of elements does not match the provided dimensions")
    # Reshape the flat list into a 2D array
    array_2d = [list(map(int, numbers[i:i+cols])) for i in range(0, len(numbers), cols)]

    return array_2d


import random
from hashlib import sha256

class Dispatch:
    def __init__(self, array, commands):
        self.roverState = "Moving"
        self.roverDirectionState = 'South'
        self.roverPosition = [0, 0]  # x, y
        self.commands = commands
        self.array = array
        self.rows = len(array)
        self.columns = len(array[0])

    def moveForward(self):
        if self.array[self.roverPosition[1]][self.roverPosition[0]] == 1:
            self.roverState = "Eliminated"
            return
        try:
            switch = {
                'North': (-1, 0),
                'South': (1, 0),
                'East': (0, 1),
                'West': (0, -1)
            }
            dx, dy = switch.get(self.roverDirectionState)
            new_x, new_y = self.roverPosition[0] + dx, self.roverPosition[1] + dy
            if new_x < 0 or new_y < 0 or new_x >= self.columns or new_y >= self.rows:
                print("Command Ignored: At the edge")
                return
            self.roverPosition = [new_x, new_y]
        except IndexError:
            print("index out of range")

    def turnLeft(self):
        switch = {
            'North': 'West',
            'East': 'North',
            'South': 'East',
            'West': 'South'
        }
        self.roverDirectionState = switch.get(self.roverDirectionState)

    def turnRight(self):
        switch = {
            'North': 'East',
            'East': 'South',
            'South': 'West',
            'West': 'North'
        }
        self.roverDirectionState = switch.get(self.roverDirectionState)

    def startTraverse(self):
        for move in self.commands:
            if move == 'M':
                self.moveForward()
                if self.roverState == "Eliminated":
                    break
            elif move == 'L':
                self.turnLeft()
            elif move == 'R':
                self.turnRight()
            elif move == 'D':
                try:
                    print(self.array)
                    print(self.roverPosition)
                    print("digging procedure: ", self.array[self.roverPosition[1]][self.roverPosition[0]])
                    if self.array[self.roverPosition[1]][self.roverPosition[0]] == 1:
                        print("mine is here")
                        self.array[self.roverPosition[1]][self.roverPosition[0]] = 0
                    else:
                        print("mine is not here")
                except IndexError:
                    print("IndexError")
            print("Direction: " + self.roverDirectionState)
            print("Position: ", self.roverPosition)
            print("---------")
        if self.roverState != "Eliminated":
            self.roverState = "Finished"
