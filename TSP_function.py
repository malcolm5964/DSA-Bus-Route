import itertools
import sys
from itertools import permutations

def tsp_dp(graph, start):
    n = len(graph)
    all_sets = 2**n
    memo = [[-1] * all_sets for _ in range(n)]

    def tsp_dp_util(curr, visited):
        if visited == all_sets - 1:
            return graph[curr][start]

        if memo[curr][visited] != -1:
            return memo[curr][visited]

        min_cost = sys.maxsize
        next_node_idx = -1

        for next_node in range(n):
            if (visited >> next_node) & 1 == 0:
                cost = graph[curr][next_node] + tsp_dp_util(next_node, visited | (1 << next_node))
                if cost < min_cost:
                    min_cost = cost
                    next_node_idx = next_node

        memo[curr][visited] = min_cost
        route[curr][visited] = next_node_idx  # Store the next node in the optimal route
        return min_cost

    route = [[-1] * all_sets for _ in range(n)]
    min_cost = tsp_dp_util(start, 1 << start)

    # Reconstruct the optimal route
    path = [start]
    visited = 1 << start
    curr = start
    while True:
        next_node = route[curr][visited]
        if next_node == -1:
            break
        path.append(next_node)
        curr = next_node
        visited |= (1 << next_node)

    if path[-1] != 0:
        path.append(0)
    return min_cost, path




'''
#Algorithm to get route
def tsp(graph, start_node):
    # Generate all possible permutations of the nodes
    nodes = list(graph.keys())
    permutations = list(itertools.permutations(nodes))

    min_distance = float('inf')  # Initialize with infinity
    optimal_path = []

    # Iterate through each permutation and calculate the total distance
    for path in permutations:
        current_distance = 0
        prev_node = start_node

        for node in path:
            current_distance += graph[prev_node][node]
            prev_node = node

        current_distance += graph[prev_node][start_node]

        # Update the minimum distance and optimal path if a shorter path is found
        if current_distance < min_distance:
            min_distance = current_distance
            optimal_path = path

    return optimal_path, min_distance
    '''



