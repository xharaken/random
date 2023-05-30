#! /usr/bin/python3
import collections


# An example graph structure
links = {"A": ["B","E","G"],
         "B": ["C"],
         "C": ["D"],
         "D": ["E"],
         "E": ["B","F"],
         "F": [],
         "G": ["F"]}


# dfs_with_recursion finds A -> B -> C -> D -> E -> F first.
def dfs_with_recursion(start, goal):
    print("dfs_with_recursion:")
    visited = {}
    path = []

    visited[start] = True
    if recursion(start, goal, visited, path):
        print(" -> ".join(path))
        return
    print("Not found")

def recursion(node, goal, visited, path):
    path.append(node)
    if node == goal:
        return True
    for child in links[node]:
        if not child in visited:
            visited[child] = True
            if recursion(child, goal, visited, path):
                return True
    path.pop()
    return False


# dfs_with_stack finds A -> G -> F first.
def dfs_with_stack(start, goal):
    print("dfs_with_stack:")
    stack = collections.deque()
    visited = {}
    previous = {}

    stack.append(start)
    visited[start] = True
    previous[start] = None
    while len(stack):
        node = stack.pop()
        if node == goal:
            break
        for child in reversed(links[node]):
            if not child in visited:
                stack.append(child)
                visited[child] = True
                previous[child] = node

    # Print the path from |start| to |goal|.
    if goal in previous:
        path = []
        node = goal
        path.append(node)
        while previous[node]:
            node = previous[node]
            path.append(node)
        path.reverse()
        print(" -> ".join(path))
        return
    print("Not found")


# Challenge quiz: Implement DFS using a stack that visits nodes and edges
# in the same order as dfs_with_recursion. In other words, implement DFS that
# finds A -> B -> C -> D -> E -> F first using a stack.

# Solution 1
def dfs_with_stack_in_the_recursion_order_1(start, goal):
    print("dfs_with_stack_in_the_recursion_order_1:")
    stack = collections.deque()
    visited = {}
    previous = {}

    stack.append(start)
    previous[start] = None
    while len(stack):
        node = stack.pop()
        visited[node] = True
        if node == goal:
            break
        for child in reversed(links[node]):
            if not child in visited:
                stack.append(child)
                previous[child] = node

    # Print the path from |start| to |goal|.
    if goal in previous:
        path = []
        node = goal
        path.append(node)
        while previous[node]:
            node = previous[node]
            path.append(node)
        path.reverse()
        print(" -> ".join(path))
        return
    print("Not found")


# Solution 2
def dfs_with_stack_in_the_recursion_order_2(start, goal):
    print("dfs_with_stack_in_the_recursion_order_2:")
    stack = collections.deque()
    visited = {}
    previous = {}

    stack.append((start, 0))
    visited[start] = True
    previous[start] = None
    while len(stack):
        (node, index) = stack.pop()
        if node == goal:
            break
        if index < len(links[node]):
            stack.append((node, index + 1))
            child = links[node][index]
            if not child in visited:
                stack.append((child, 0))
                visited[child] = True
                previous[child] = node

    # Print the path from |start| to |goal|.
    if goal in previous:
        path = []
        node = goal
        path.append(node)
        while previous[node]:
            node = previous[node]
            path.append(node)
        path.reverse()
        print(" -> ".join(path))
        return
    print("Not found")


# Solution 3
def dfs_with_stack_in_the_recursion_order_3(start, goal):
    print("dfs_with_stack_in_the_recursion_order_3:")
    stack = collections.deque()
    visited = {}
    previous = {}

    current = None
    child = start
    while True:
        if not child in visited:
            visited[child] = True
            previous[child] = current
            for i in reversed(range(len(links[child]))):
                stack.append((child, i))
        if len(stack) == 0:
            break
        (current, index) = stack.pop()
        if current == goal:
            break
        child = links[current][index]

    # Print the path from |start| to |goal|.
    if goal in previous:
        path = []
        node = goal
        path.append(node)
        while previous[node]:
            node = previous[node]
            path.append(node)
        path.reverse()
        print(" -> ".join(path))
        return
    print("Not found")


dfs_with_recursion("A", "F")
dfs_with_stack("A", "F")
dfs_with_stack_in_the_recursion_order_1("A", "F")
dfs_with_stack_in_the_recursion_order_2("A", "F")
dfs_with_stack_in_the_recursion_order_3("A", "F")
