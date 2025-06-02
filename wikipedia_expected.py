import collections, random, sys

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
    # 'start': The title of the start page.
    # 'goal': The title of the goal page.
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


    # Optional homework:
    # Search a pair of the most distant pages with heuristics.
    #
    # This method uses a Double Sweep algorithm.
    # See https://qiita.com/knewknowl/items/bb49242db38b99c82c06.
    def search_most_distant_pages(self):
        # Build a reverse graph.
        reverse_links = self.build_reverse_links()

        visited_goal_ids = {}
        max_distance = 0
        # Repeat until interrupted.
        while True:
            # Step 1: Choose a random page P.
            random_id = random.choice(list(self.titles.keys()))

            # Step 2: Find one of the most distant pages from P in the
            # original graph. We call it a goal page.
            (goal_id, _) = self.find_most_distant_page(random_id, self.links)

            # Avoid searching the same goal page again.
            if goal_id in visited_goal_ids:
                continue
            visited_goal_ids[goal_id] = True

            # Step 3: Find one of the most distant pages from the goal page
            # using the reverse graph. We call it a start page. For any page X,
            # distance(X -> goal page) <= distance(start page -> goal page)
            # holds in the original graph.
            (start_id, distance) = self.find_most_distant_page(
                goal_id, reverse_links)
            print("random = %s, start = %s, goal = %s, distance = %d" % (
                self.titles[random_id], self.titles[goal_id],
                self.titles[start_id], distance))

            # Update the max distance to distance(start page, goal page).
            if max_distance < distance:
                print("Distance: %d" % distance)
                # Print a route from the start page to the goal page.
                self.find_shortest_path(
                    self.titles[start_id], self.titles[goal_id])
                max_distance = distance


    # Helper function:
    # Bulid a graph with reverse links.
    # self.links is a set of all page links of the original graph.
    # If the original graph has a link from a page X to a page Y,
    # the reverse graph has a link from a page Y to a page X.
    # This method returns a set of all page links of the reverse graph.
    def build_reverse_links(self):
        reverse_links = {}
        for id in self.titles.keys():
            reverse_links[id] = []
        for src in self.links.keys():
            for dst in self.links[src]:
                # If the original graph has a link from 'src' to 'dst',
                # the reverse graph has a link from 'dst' to 'src'.
                reverse_links[dst].append(src)
        return reverse_links


    # Helper function:
    # Finds one of the most distant pages reachable from a starting page.
    # 'start_id': An ID of the starting page.
    # 'links': All page links.
    #
    # This method returns a tuple of (one of the most distant pages, the
    # distance from the starting page).
    def find_most_distant_page(self, start_id, links):
        # BFS
        current = start_id
        distance = 0
        queue = collections.deque([(current, distance)])
        visited = {}
        visited[current] = True
        while queue:
            (current, distance) = queue.popleft()
            # To avoid returning the same most distant page every time,
            # randomize the order to visit children.
            randomized = random.sample(links[current], len(links[current]))
            for child in randomized:
                if not child in visited:
                    visited[child] = True
                    queue.append((child, distance + 1))
        return (current, distance)


    # Optional homework:
    # Search the longest path with heuristics.
    # 'start': The title of the start page.
    # 'goal': The title of the goal page.
    def search_longest_path(self, start, goal):
        start_id = self.title_to_id(start)
        goal_id = self.title_to_id(goal)
        if start_id == -1:
            print("The page %s was not found\n" % start)
            return
        if goal_id == -1:
            print("The page %s was not found\n" % goal)
            return

        # Build a reverse graph.
        reverse_links = self.build_reverse_links()

        # Run BFS from the goal page using the reverse graph.
        # As a result, distance(X -> goal page) on the original graph is stored
        # in distances[X].
        current = goal_id
        distances = {}
        distances[current] = 0
        queue = collections.deque([(current, distances[current])])
        while queue:
            (current, distance) = queue.popleft()
            for child in reverse_links[current]:
                if not child in distances:
                    distances[child] = distance + 1
                    queue.append((child, distances[child]))
        print("BFS from the goal page finished.")

        max_path = 0
        # Repeat until interrupted.
        while True:
            # Run DFS from the start page. To find a longer path to the goal
            # page, twist the order to visit child nodes. Instead of visiting
            # the child nodes in the order stored in self.links, visit child
            # nodes that are more distant to the goal page first. That way,
            # DFS is more likely to find a longer path to the goal page.
            current = start_id
            previous = {}
            previous[current] = None
            stack = collections.deque([current])
            while stack:
                current = stack.pop()
                # The path from the start page to the goal page is found.
                if current == goal_id:
                    path = 0
                    node = current
                    while node:
                        path += 1
                        node = previous[node]
                    print("Path found: %d" % path)
                    # Update the max path.
                    if max_path < path:
                        max_path = path
                        print("Max path found: %d" % path)
                    break

                # Twist the order to visit child nodes so that DFS visits
                # child nodes that are more distant to the goal page first.
                children = self.shuffle_nodes(self.links[current], distances)
                for child in children:
                    if not child in previous:
                        previous[child] = current
                        stack.append(child)


    # Helper function:
    # Twist the order of visiting child nodes.
    # 'nodes': A list of child nodes.
    # 'distances': distances[X] stores distance(X -> goal page).
    #
    # This method sorts 'nodes' in the order of the distances to the goal page.
    # nodes[0] is the most distant node to the goal page, and nodes[-1] is the
    # least distant node to the goal page.
    # To add some randomness, swap a few items in the sorted nodes.
    def shuffle_nodes(self, nodes, distances):
        result = []
        for node in nodes:
            if node in distances:
                result.append((node, distances[node]))
        # Sort the child nodes in the order of the distances to the goal page.
        result = sorted(result, key=lambda x:x[1])

        # To add randomness, swap a few items.
        for _ in range(len(result) // 40):
            index1 = random.randint(0, len(result) - 1)
            index2 = random.randint(0, len(result) - 1)
            result[index1], result[index2] = result[index2], result[index1]
        return [item[0] for item in result]


    # Optional homework:
    # Do something more interesting!!
    def do_something_more_interesting(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    wikipedia.find_longest_titles()
    wikipedia.find_most_linked_pages()
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    wikipedia.find_most_popular_pages()
    wikipedia.search_most_distant_pages()
    wikipedia.search_longest_path("渋谷", "池袋")
    wikipedia.do_something_more_interesting()
