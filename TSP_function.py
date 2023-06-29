import itertools

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