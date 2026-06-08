#!/usr/bin/env python3

import sys
import math

def read_input(filename):
    with open(filename) as f:
        cities = []
        for line in f.readlines()[1:]:  # Ignore the first line.
            xy = line.split(',')
            cities.append((float(xy[0]), float(xy[1])))
        return cities


def print_tour(tour):
    print('index\n' + '\n'.join(map(str, tour)))


def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


def solve(cities):
    N = len(cities)

    # Calculate distances
    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])

    # Create an initial path using greedy search
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]

    while unvisited_cities:
        # Select the nearest neighbour.
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city

    # 2-opt
    improved = True
    while improved:
        improved = False
        # Select two edges [i, i+1] and [j, j+1]
        for i in range(N - 2):
            for j in range(i + 2, N):
                if i == 0 and j == N - 1:
                    continue

                node1 = tour[i]
                node2 = tour[i + 1]
                node3 = tour[j]
                node4 = tour[(j + 1) % N]

                current_dist = dist[node1][node2] + dist[node3][node4]
                new_dist = dist[node1][node3] + dist[node2][node4]

                if new_dist < current_dist:
                    # Reverse the path from i+1 to j.
                    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
                    improved = True

    return tour


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage %s input_file" % sys.argv[0])
        sys.exit(1)
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)
