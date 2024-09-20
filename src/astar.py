#!/usr/env/bin python3
import heapq
import numpy as np
import time

class AStar:
    #default timeout is 5 seconds (ensure AStar finds route in 5 seconds max)
    def __init__(self, grid, timeout=5):
        self.grid = grid
        self.height, self.width = grid.shape
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.timeout = timeout

    def heuristic(self, a, b):
        return np.hypot(b[0] - a[0], b[1] - a[1])

    def astar(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        start_time = time.time()
    
        while frontier:
            _, current = heapq.heappop(frontier)
    
            if current == goal:
                break
    
            for dx, dy in self.directions:
                next_cell = (current[0] + dx, current[1] + dy)
                if (0 <= next_cell[0] < self.width and
                        0 <= next_cell[1] < self.height and
                        self.grid[next_cell[1], next_cell[0]] == 0):
                    new_cost = cost_so_far[current] + 1
                    if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                        cost_so_far[next_cell] = new_cost
                        priority = new_cost + self.heuristic(goal, next_cell)
                        heapq.heappush(frontier, (priority, next_cell))
                        came_from[next_cell] = current
                        print(f"Exploring {next_cell} from {current} with cost {new_cost}")

            if time.time() - start_time > self.timeout:
                print(f"Timeout reached after {self.timeout} seconds")
                return {}, {}
    
        return came_from, cost_so_far
    

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            if current not in came_from:
                print(f"No path found from {start} to {goal}")
                return []
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
