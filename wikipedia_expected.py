import collections, random, sys, time

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # A set of reverse page links.
        # For example, self.links[1234] returns an array of page IDs that have
        # links to the page whose ID is 1234.
        # This is initialized in build_reverse_graph().
        self.reverse_links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()


    # Find the longest titles. This is not related to a graph algorithm at all
    # though :)
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()


    # Homework #1:
    # Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_shortest_path(self, start, goal):
        start_id = self.title_to_id(start)
        goal_id = self.title_to_id(goal)
        if start_id == -1:
            print("The page %s was not found\n" % start)
            return
        if goal_id == -1:
            print("The page %s was not found\n" % goal)
            return

        # BFS
        queue = collections.deque([start_id])
        previous = {}
        previous[start_id] = None
        while queue:
            current = queue.popleft()
            if current == goal_id:
                routes = []
                while current:
                    routes.append(self.titles[current])
                    current = previous[current]
                routes.reverse()
                print("The shortest path from %s to %s is:" % (start, goal))
                print(" -> ".join(routes), "\n")
                return

            for child in self.links[current]:
                if not child in previous:
                    previous[child] = current
                    queue.append(child)
        print("The path from %s to %s was not found." % (start, goal))


    # Helper function:
    # Convert a title to a page ID. Returns -1 if the title was not found.
    def title_to_id(self, title):
        for k, v in self.titles.items():
            if v == title:
                return k
        return -1

    # Homework #2:
    # Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        # The damping factor of the pagerank algorithm.
        DAMPING_FACTOR = 0.85

        pageranks = {}
        updated_pageranks = {}

        # Initialize the pageranks to 1.0.
        for id in self.titles.keys():
            pageranks[id] = 1.0

        for iteration in range(10000):
            # This is the core part of the pagerank algorithm.
            # The pageranks are updated with the following formula:
            #
            #   updated_pageranks(i) =
            #       (1 - DAMPING_FACTOR) +
            #       DAMPING_FACTOR * \sum (pagerank(j) / outdegree(j)).
            #
            # The summation is taken for all j's that have links to the page i.
            # outdegree(j) is the number of outgoing links from the page j.
            for id in self.titles.keys():
                updated_pageranks[id] = 1 - DAMPING_FACTOR

            orphaned_pagerank = 0
            for src in self.links.keys():
                link_count = len(self.links[src])
                if link_count == 0:
                    orphaned_pagerank += pageranks[src]
                else:
                    for dst in self.links[src]:
                        updated_pageranks[dst] += (
                            DAMPING_FACTOR * pageranks[src] / link_count)

            # This is a subtle part to fix up the pageranks calculated in the
            # above. The problem is that there are pages that don't have any
            # outgoing links (let's call these pages "orphaned pages"). Since
            # the above loop only distributes pageranks of pages that have
            # outgoing links, the pageranks of the orphaned pages are lost.
            # To fix the problem, we distribute the pageranks of the orphaned
            # pages evenly to all pages.
            page_count = len(self.titles.keys())
            for id in self.titles.keys():
                updated_pageranks[id] += (
                    DAMPING_FACTOR * orphaned_pagerank / page_count)

            # total = \sum updated_pageranks(i)
            # This total value should stay the same across iterations.
            total = 0

            # norm = \sum (updated_pageranks(i) - pageranks(i)) ^ 2
            # We finish the iteration when the norm becomes small enough.
            norm = 0
            for id in self.titles.keys():
                delta = updated_pageranks[id] - pageranks[id]
                norm += delta * delta
                total += updated_pageranks[id]
                pageranks[id] = updated_pageranks[id]
            print("iteration %d: total = %d, norm = %.5lf" % (
                iteration, total, norm))
            if norm < 0.01:
                break

        # Print the pageranks of the most popular pages.
        sorted_pageranks = sorted(pageranks.items(),
                                  key=lambda x:x[1], reverse=True)
        print("The most popular pages are:")
        for i in range(min(20, len(sorted_pageranks))):
            print("%s (pagerank = %.2lf)" % (
                self.titles[sorted_pageranks[i][0]], sorted_pageranks[i][1]))
        print()


    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        start_id = self.title_to_id(start)
        goal_id = self.title_to_id(goal)
        if start_id == -1:
            print("The page %s was not found\n" % start)
            return
        if goal_id == -1:
            print("The page %s was not found\n" % goal)
            return

        # Run DFS from the start page to the goal page and find an initial
        # path.
        path = self.dfs_with_heuristics(start_id, goal_id, {})
        self.assert_path(path, start, goal)
        print("Initial path: %d" % (len(path) - 1))

        # Repeat until interrupted.
        while True:
            # We try to extend the path incrementally with the following
            # algorithm.
            #
            # 1. Randomly select one node in the current path. Imagine that
            # an 'index'-th node in the path is selected.
            #
            # The current path is:
            #   start == path[0] -> path[1] -> ... ->
            #   path[index] -> path[index+1] -> ... -> path[-1] == goal
            #
            # 2. We set visited flags on all nodes in the path except
            # path[index] and path[index+1], and run DFS from path[index] to
            # path[index+1]. If we find a longer path from path[index] to
            # path[index+1], replace path[index] -> path[index+1] with the
            # found one.

            assert(len(path) >= 2)
            # Randomly select one node in the path.
            index = random.randint(0, len(path) - 2)

            # Before running DFS, we need to set visited flags on all nodes
            # in the path except path[index] and path[index+1].
            visited = {}
            for i, node in enumerate(path):
                if i != index and i != index + 1:
                    visited[node] = True

            # Run DFS from path[index] to path[index+1].
            new_path = self.dfs_with_heuristics(
                path[index], path[index + 1], visited)

            if len(new_path) >= 3:
                # If a longer path is found, update the path.
                path = (path[:index] + new_path + path[index + 2:])
                self.assert_path(path, start, goal)
                print("Updated path: %d" % (len(path) - 1))
            else:
                print("No update")


    # Helper function for Homework #3:
    # Please use this function to check if the found path is well formed.
    # 'path': An array of page IDs that stores the found path.
    #     path[0] is the start page. path[-1] is the goal page.
    #     path[0] -> path[1] -> ... -> path[-1] is the path from the start
    #     page to the goal page.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])


    # DFS with heuristics.
    # 'start_id': An ID of the start page.
    # 'goal_id': An ID of the goal page.
    # 'visited': Visited flags.
    #
    # This function returns a found path.
    def dfs_with_heuristics(self, start_id, goal_id, visited):
        current = start_id
        previous = {}
        previous[current] = None
        stack = collections.deque([current])
        while stack:
            current = stack.pop()
            # For DFS to find a longer path, it is important to set a visited
            # flag when the node is popped from the stack, not when the node is
            # pushed to the stack.
            #
            # For example, imagine that A has links to B and C. When DFS
            # visits A, it pushes B and C to the stack. DFS pops C from the
            # stack and visits C. If a visited flag is set when the node is
            # pushed to the stack, DFS will never find A -> C -> ... -> B
            # because B's visited flag is already set. DFS only finds A -> B.
            visited[current] = True

            if current == goal_id:
                path = []
                while current:
                    path.append(current)
                    current = previous[current]
                path.reverse()
                return path

            # Randomize the order to visit child nodes. Otherwise, DFS always
            # finds the same path and we cannot extend the initial path at all.
            children = self.links[current].copy()
            random.shuffle(children)

            for child in children:
                if not child in visited:
                    # Do not set a visited flag here. See above comment.
                    previous[child] = current
                    stack.append(child)
        return []


    # DFS with advanced heuristics. This finds a longer path more efficiently.
    # 'start_id': An ID of the start page.
    # 'goal_id': An ID of the goal page.
    # 'visited': Visited flags.
    #
    # This function returns a found path.
    def dfs_with_advanced_heuristics(self, start_id, goal_id, visited):
        # Build a reverse graph.
        reverse_links = self.build_reverse_graph()

        # Calculate distance(X -> goal page) on the original graph for all
        # node X's and store it to distances[X]. We can do this by running
        # BFS from the goal page to all nodes using the reverse graph.
        current = goal_id
        distances = {}
        distances[current] = 0
        queue = collections.deque([(current, distances[current])])
        while queue:
            (current, distance) = queue.popleft()
            for child in self.reverse_links[current]:
                if not child in distances:
                    distances[child] = distance + 1
                    queue.append((child, distances[child]))

        # Run DFS from the start page. To find a longer path to the goal
        # page, twist the order to visit child nodes. Instead of visiting
        # the child nodes in the order stored in self.links, visit child
        # nodes that are more distant to the goal page first. By doing this,
        # DFS is more likely to find a longer path to the goal page.
        current = start_id
        previous = {}
        previous[current] = None
        stack = collections.deque([current])
        while stack:
            current = stack.pop()
            # For DFS to find a longer path, the visited flag needs to be set
            # when the node is popped from the stack, not when the node is
            # pushed to the stack.
            visited[current] = True

            if current == goal_id:
                path = []
                while current:
                    path.append(current)
                    current = previous[current]
                path.reverse()
                return path

            # Twist the order to visit child nodes so that DFS visits child
            # nodes that are more distant to the goal page first. For this
            # purpose, we sort the child nodes in the order of the distances
            # to the goal page.
            children = []
            for node in self.links[current]:
                # If 'node' is not included in 'distances', there is no path
                # from the 'node' to the goal page. We do not need to visit
                # the 'node'.
                if node in distances:
                    children.append(node)
            # Sort the child nodes by distances to the goal page.
            children = sorted(children, key=lambda x:distances[x])

            for child in children:
                if not child in visited:
                    previous[child] = current
                    stack.append(child)
        return []


    # Helper function:
    # Build a graph with reverse links.
    # If the original graph has a link from a page X to a page Y,
    # the reverse graph has a link from a page Y to a page X.
    # The reverse links are stored in self.reverse_links.
    def build_reverse_graph(self):
        if self.reverse_links:
            return
        for id in self.titles.keys():
            self.reverse_links[id] = []
        for src in self.links.keys():
            for dst in self.links[src]:
                # If the original graph has a link from 'src' to 'dst',
                # the reverse graph has a link from 'dst' to 'src'.
                self.reverse_links[dst].append(src)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Example
    wikipedia.find_longest_titles()
    # Example
    wikipedia.find_most_linked_pages()
    # Homework #1
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # Homework #2
    wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")
