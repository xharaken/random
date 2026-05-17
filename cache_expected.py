import sys
import hash_table_expected # Use the hash table you implemented in Homework #2

# Implement a data structure that stores the most recently accessed N pages.
# See the test cases to see how it should work.
#
# Note: Please do not use a library like collections.OrderedDict). The goal is
#       to implement the data structure yourself!

class Node:
    def __init__(self, url, contents):
        # URL
        self.url = url
        # The contents of the URL
        self.contents = contents
        # Previous Node
        self.prev = None
        # Next Node
        self.next = None

        
class Cache:
    # Initialize the cache.
    # 'n': The size of the cache.
    def __init__(self, n):
        assert(n >= 1)
        self.list_head = Node("", "")
        self.list_tail = Node("", "")
        self.list_head.next = self.list_tail
        self.list_tail.prev = self.list_head
        self.n = n
        self.url_to_node = hash_table_expected.HashTable()

    # Access a page and update the cache so that it stores the most recently
    # accessed N pages. This needs to be done with mostly O(1).
    # 'url': The accessed URL
    # 'contents': The contents of the URL
    def access_page(self, url, contents):
        (node, _) = self.url_to_node.get(url)
        if node is not None: # Cache hit
            assert(node.prev)
            assert(node.next)
            # Update the contents.
            node.contents = contents
            node.prev.next = node.next
            node.next.prev = node.prev
        else: # Cache miss
            if self.url_to_node.size() >= self.n:
                # If the cache size reaches the limit, remove the oldest Node.
                tail = self.list_tail.prev
                self.url_to_node.delete(tail.url)
                tail.prev.next = self.list_tail
                self.list_tail.prev = tail.prev

            # Cache the new Node
            node = Node(url, contents)
            self.url_to_node.put(url, node)

        # Move the Node to the head because it's the newest.
        node.next = self.list_head.next
        node.prev = self.list_head
        self.list_head.next.prev = node
        self.list_head.next = node

    # Return the URLs stored in the cache. The URLs are ordered in the order
    # in which the URLs are mostly recently accessed.
    def get_pages(self):
        node = self.list_head.next
        urls = []
        while node.next: # Scan all nodes
            # Consistency checks
            assert(node.url != "")
            assert(self.url_to_node.get(node.url) == (node, True))
            assert(node.prev.next == node)
            assert(node.next.prev == node)
            
            urls.append(node.url)
            node = node.next
            
        assert(len(urls) == self.url_to_node.size())
        return urls


def cache_test():
    # Set the size of the cache to 4.
    cache = Cache(4)

    # Initially, no page is cached.
    assert cache.get_pages() == []

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # "a.com" is cached.
    assert cache.get_pages() == ["a.com"]

    # Access "b.com".
    cache.access_page("b.com", "BBB")
    # The cache is updated to:
    #   (new)<-- "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["b.com", "a.com"]

    # Access "c.com".
    cache.access_page("c.com", "CCC")
    # The cache is updated to:
    #   (new)<-- "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["c.com", "b.com", "a.com"]

    # Access "d.com".
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "d.com" again.
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "a.com" again.
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (new)<-- "a.com", "d.com", "c.com", "b.com" -->(old)
    assert cache.get_pages() == ["a.com", "d.com", "c.com", "b.com"]

    cache.access_page("c.com", "CCC")
    assert cache.get_pages() == ["c.com", "a.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is full, so we need to remove the least recently accessed page "b.com".
    # The cache is updated to:
    #   (new)<-- "e.com", "a.com", "c.com", "d.com" -->(old)
    assert cache.get_pages() == ["e.com", "a.com", "c.com", "d.com"]

    # Access "f.com".
    cache.access_page("f.com", "FFF")
    # The cache is full, so we need to remove the least recently accessed page "c.com".
    # The cache is updated to:
    #   (new)<-- "f.com", "e.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["f.com", "e.com", "a.com", "c.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is updated to:
    #   (new)<-- "e.com", "f.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["e.com", "f.com", "a.com", "c.com"]

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (new)<-- "a.com", "e.com", "f.com", "c.com" -->(old)
    assert cache.get_pages() == ["a.com", "e.com", "f.com", "c.com"]

    print("Tests passed!")


if __name__ == "__main__":
    cache_test()
