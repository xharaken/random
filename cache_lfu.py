import random, sys
import hash_table_expected # Use the hash table you implemented in Homework #2

###########################################################################
#                                                                         #
# Implement a cache that stores the most frequently accessed items from   #
# scratch!                                                                #
#                                                                         #
# Please do not use Python's dictionary or Python's collections library.  #
# The goal is to implement the data structure yourself.                   #
#                                                                         #
###########################################################################

class FreqNode:
    # A node representing a specific access frequency.
    # It contains a doubly linked list of Pages that share this frequency.
    def __init__(self, freq):
        self.freq = freq
        self.prev = None
        self.next = None
        # Head and tail dummy pages for the doubly linked list of pages
        self.list_head = Page("", "")
        self.list_tail = Page("", "")
        self.list_head.next = self.list_tail
        self.list_tail.prev = self.list_head

    def is_empty(self):
        return self.list_head.next == self.list_tail

    def insert_page_at_head(self, page):
        page.next = self.list_head.next
        page.prev = self.list_head
        self.list_head.next.prev = page
        self.list_head.next = page
        page.parent_freq = self

    def remove_page(self, page):
        page.prev.next = page.next
        page.next.prev = page.prev


class Page:
    def __init__(self, url, contents):
        # URL
        self.url = url
        # The contents of the URL
        self.contents = contents
        # Previous page in the horizontal frequency list
        self.prev = None
        # Next page in the horizontal frequency list
        self.next = None
        # Pointer to the parent FreqNode (vertical list)
        self.parent_freq = None


class Cache:
    # Initialize the cache.
    # 'limit': The size limit of the cache.
    def __init__(self, limit):
        assert(limit >= 1)
        self.limit = limit
        self.hit_count = 0 # Increment on a cache hit
        self.miss_count = 0 # Increment on a cache miss
        
        # Dummy head and tail for the frequency doubly linked list
        self.freq_head = FreqNode(0)
        self.freq_tail = FreqNode(float('inf'))
        self.freq_head.next = self.freq_tail
        self.freq_tail.prev = self.freq_head
        
        self.url_to_page = hash_table_expected.HashTable()

    # Helper function to insert a new FreqNode
    def _insert_freq_node_after(self, new_node, prev_node):
        new_node.next = prev_node.next
        new_node.prev = prev_node
        prev_node.next.prev = new_node
        prev_node.next = new_node

    # Helper function to remove an empty FreqNode
    def _remove_freq_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    # Access a page and update the cache so that it stores the most frequently
    # accessed pages up to the 'limit'. This needs to be done with mostly O(1).
    # 'url': The accessed URL
    # 'contents': The contents of the URL
    def access_page(self, url, contents):
        (page, _) = self.url_to_page.get(url)
        
        if page is not None: # Cache hit
            # Update the contents.
            page.contents = contents
            self.hit_count += 1
            
            current_freq_node = page.parent_freq
            next_freq = current_freq_node.freq + 1
            
            # Remove page from its current frequency list
            current_freq_node.remove_page(page)
            
            # If the next frequency node doesn't exist, create it
            if current_freq_node.next.freq != next_freq:
                new_freq_node = FreqNode(next_freq)
                self._insert_freq_node_after(new_freq_node, current_freq_node)
            
            # Insert page to the head of the new frequency list (LRU tie-breaker)
            current_freq_node.next.insert_page_at_head(page)
            
            # Clean up empty frequency nodes (except dummies)
            if current_freq_node.is_empty():
                self._remove_freq_node(current_freq_node)
                
        else: # Cache miss
            if self.url_to_page.size() >= self.limit:
                # If the cache size reaches the limit, remove the least frequently used page.
                # The LFU page is at the tail of the lowest frequency node.
                lfu_node = self.freq_head.next
                if lfu_node != self.freq_tail:
                    evict_page = lfu_node.list_tail.prev
                    lfu_node.remove_page(evict_page)
                    self.url_to_page.delete(evict_page.url)
                    
                    if lfu_node.is_empty():
                        self._remove_freq_node(lfu_node)

            # Cache the new page
            page = Page(url, contents)
            self.url_to_page.put(url, page)
            self.miss_count += 1
            
            # The new page has frequency 1. Create FreqNode(1) if it doesn't exist.
            if self.freq_head.next.freq != 1:
                new_freq_node = FreqNode(1)
                self._insert_freq_node_after(new_freq_node, self.freq_head)
            
            # Insert the new page at the head of frequency 1 list
            self.freq_head.next.insert_page_at_head(page)


    # Return the URLs stored in the cache. The URLs are ordered by frequency 
    # (highest first). In case of ties, ordered by most recently accessed first.
    def get_pages(self):
        urls = []
        # Start from the highest frequency
        curr_freq = self.freq_tail.prev
        
        while curr_freq != self.freq_head: # Scan all frequency nodes
            page = curr_freq.list_head.next
            while page != curr_freq.list_tail: # Scan all pages in this frequency
                # Consistency checks
                assert(page.url != "")
                assert(self.url_to_page.get(page.url) == (page, True))
                assert(page.prev.next == page)
                assert(page.next.prev == page)
                assert(page.parent_freq == curr_freq)
                
                urls.append(page.url)
                page = page.next
                
            curr_freq = curr_freq.prev
            
        assert(len(urls) == self.url_to_page.size())
        return urls


    # Return the cache hit rate.
    def get_hitrate(self):
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0

    
def functional_test():
    pass


def performance_test():
    # Set the size of the cache to 100.
    cache = Cache(100)

    # Generate queries based on the Zipf law.
    ALPHA = 1.5
    NUM_QUERIES = 1000000
    NUM_PAGES = 1000
    ranks = range(1, NUM_PAGES + 1)
    weights = [1.0 / (r ** ALPHA) for r in ranks]
    random.seed(1)
    queries = random.choices(ranks, weights=weights, k=NUM_QUERIES)    
    for query in queries:
        cache.access_page(str(query), "")

    # If your cache implementation is correct, the hit rate will be 91%.
    print("Cache hit rate = %d %%" % (cache.get_hitrate() * 100))
    print("Performance tests passed!")
    

if __name__ == "__main__":
    functional_test()
    performance_test()

