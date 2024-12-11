#!/usr/bin/env python3
import heapq
import numpy as np
import time

class AStar:
    # Default timeout is 600 seconds (ensure AStar finds route in 600 seconds max)
    def __init__(self, grid, timeout=600):
        self.grid = grid
        self.height, self.width = grid.shape
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.timeout = timeout

    def heuristic0(self, a, b):
        return np.hypot(b[0] - a[0], b[1] - a[1])

    def astar0(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        start_time = time.time()

        while frontier:
            if time.time() - start_time > self.timeout:
                print(f"Timeout reached after {self.timeout} seconds")
                return {}, {}

            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for dx, dy in self.directions:
                next_cell = (current[0] + dx, current[1] + dy)
                if (0 <= next_cell[0] < self.height and
                    0 <= next_cell[1] < self.width and
                    self.grid[next_cell[0], next_cell[1]] == 0):
                    new_cost = cost_so_far[current] + 1
                    if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                        cost_so_far[next_cell] = new_cost
                        priority = new_cost + self.heuristic(goal, next_cell)
                        heapq.heappush(frontier, (priority, next_cell))
                        came_from[next_cell] = current

        return came_from, cost_so_far

    def heuristic(self, a, b):
        scaling_factor = 1.2  # Increase for more relaxed exploration
        return scaling_factor * np.hypot(b[0] - a[0], b[1] - a[1])


    def astar(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        start_time = time.time()

        while frontier:
            if time.time() - start_time > self.timeout:
                print(f"Timeout reached after {self.timeout} seconds")
                return {}, {}

            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for dx, dy in self.directions:
                next_cell = (current[0] + dx, current[1] + dy)
                if (0 <= next_cell[0] < self.height and
                    0 <= next_cell[1] < self.width):
                    # Add weight for semi-passable cells (e.g., value 0.5)
                    weight = self.grid[next_cell[0], next_cell[1]]
                    if weight < 1:  # Only passable areas
                        new_cost = cost_so_far[current] + weight
                        if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                            cost_so_far[next_cell] = new_cost
                            priority = new_cost + self.heuristic(goal, next_cell)
                            heapq.heappush(frontier, (priority, next_cell))
                            came_from[next_cell] = current
 

        return came_from, cost_so_far



    def reconstruct_path(self, came_from, start, goal):
        if goal not in came_from:
            print(f"No path found from {start} to {goal}")
            return []

        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

# Example usage
if __name__ == "__main__":
    grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ])
    start = (0, 0)
    goal = (4, 4)

    astar = AStar(grid)
    came_from, cost_so_far = astar.astar(start, goal)
    path = astar.reconstruct_path(came_from, start, goal)
    print("Path:", path)
""
