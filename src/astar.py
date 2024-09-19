#!/usr/env/bin python3
import heapq
import numpy as np

class AStar:
    def __init__(self, grid):
        self.grid = grid
        self.height, self.width = grid.shape
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def heuristic(self, a, b):
        return np.hypot(b[0] - a[0], b[1] - a[1])

    def astar(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

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

        return came_from, cost_so_far

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
