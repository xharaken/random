import sys
import collections

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


    # Find the shortest path.
    # |start|: The title of the start page.
    # |goal|: The title of the goal page.
    def find_shortest_path(self, start, goal):
        start_id = -1
        goal_id = -1
        for id in self.titles.keys():
            if self.titles[id] == start:
                start_id = id
            if self.titles[id] == goal:
                goal_id = id
        if start_id == -1:
            print("The page %s was not found\n" % start)
            return
        if goal_id == -1:
            print("The page %s was not found\n" % goal)
            return

        # BFS.
        queue = collections.deque([start_id])
        visited = {}
        visited[start_id] = True
        previous = {}
        previous[start_id] = None
        while queue:
            current = queue.popleft()
            if current == goal_id:
                print("The shortest path from %s to %s is:" %
                      (start, goal))
                routes = []
                current = goal_id
                while current:
                    routes.append(current)
                    current = previous[current]
                for id in reversed(routes):
                    print(self.titles[id],
                          end="\n" if id == goal_id else " -> ")
                print()
                return

            for child in self.links[current]:
                if not child in visited:
                    visited[child] = True
                    previous[child] = current
                    queue.append(child)
        print("The path from %s to %s was not found." % (start, goal))


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


    # Do something more interesting!!
    def find_something_more_interesting(self):
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
