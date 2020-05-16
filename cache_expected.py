import sys

# Cache is a data structure that stores the most recently accessed N pages.
# See the below test cases to see how it should work.
class Cache:
  # Initializes the cache.
  # |n|: The size of the cache.
  def __init__(self, n):
    assert(n >= 1)
    self.list_head_ = {"page": "", "prev": None, "next": None}
    self.list_tail_ = {"page": "", "prev": None, "next": None}
    self.list_head_["next"] = self.list_tail_
    self.list_tail_["prev"] = self.list_head_
    self.n_ = n
    self.count_ = 0
    self.page_to_node_ = {}

  # Access a page and update the contents of the cache so that it stores
  # the most recently accessed N pages. This needs to be done with mostly O(1).
  # |page|: The accessed page
  def access_page(self, page):
    node = None
    if page in self.page_to_node_:
      node = self.page_to_node_[page]
      assert(node["prev"])
      assert(node["next"])
      node["prev"]["next"] = node["next"]
      node["next"]["prev"] = node["prev"]
    else:
      if self.count_ >= self.n_:
        tail = self.list_tail_["prev"]
        del self.page_to_node_[tail["page"]]
        tail["prev"]["next"] = self.list_tail_
        self.list_tail_["prev"] = tail["prev"]
        self.count_ -= 1
      node = {"page": page, "prev": None, "next": None}
      self.page_to_node_[page] = node
      self.count_ += 1
    node["next"] = self.list_head_["next"]
    node["prev"] = self.list_head_
    self.list_head_["next"]["prev"] = node
    self.list_head_["next"] = node

  # Return the contents of the cache as a list. The contents must be ordered
  # in the order in which the pages are mostly recently accessed.
  def get_pages(self):
    node = self.list_head_["next"]
    pages = []
    count = 0
    while node["next"]:
      assert(node["page"] != "")
      assert(self.page_to_node_[node["page"]] == node)
      assert(node["prev"]["next"] == node)
      assert(node["next"]["prev"] == node)
      pages.append(node["page"])
      node = node["next"]
      count += 1
    assert(count == self.count_)
    return pages


# Does your code pass all test cases? :)
def cache_test():
  # Set the size of the cache to 4.
  cache = Cache(4)
  # Initially, no page is cached.
  equal(cache.get_pages(), [])
  # Access "A". Imagine that "A" means the pair of ("a.com", the page contents).
  cache.access_page("A")
  # "A" is cached.
  equal(cache.get_pages(), ["A"])
  # Access "B".
  cache.access_page("B")
  # The cache is updated to:
  #   (most recently accessed)<-- "B", "A" -->(least recently accessed)
  equal(cache.get_pages(), ["B", "A"])
  # Access "C".
  cache.access_page("C")
  # The cache is updated to:
  #   (most recently accessed)<-- "C", "B", "A" -->(least recently accessed)
  equal(cache.get_pages(), ["C", "B", "A"])
  # Access "D".
  cache.access_page("D")
  # The cache is updated to:
  #   (most recently accessed)<-- "D", "C", "B", "A" -->(least recently accessed)
  equal(cache.get_pages(), ["D", "C", "B", "A"])
  # Access "D" again.
  cache.access_page("D")
  # The cache is updated to:
  #   (most recently accessed)<-- "D", "C", "B", "A" -->(least recently accessed)
  equal(cache.get_pages(), ["D", "C", "B", "A"])
  # Access "A" again.
  cache.access_page("A")
  # The cache is updated to:
  #   (most recently accessed)<-- "A", "D", "C", "B" -->(least recently accessed)
  equal(cache.get_pages(), ["A", "D", "C", "B"])
  cache.access_page("C")
  equal(cache.get_pages(), ["C", "A", "D", "B"])
  cache.access_page("A")
  equal(cache.get_pages(), ["A", "C", "D", "B"])
  cache.access_page("A")
  equal(cache.get_pages(), ["A", "C", "D", "B"])
  # Access "E".
  cache.access_page("E")
  # The cache is full, so we need to remove the least recently accessed page "B".
  # The cache is updated to:
  #   (most recently accessed)<-- "E", "A", "C", "D" -->(least recently accessed)
  equal(cache.get_pages(), ["E", "A", "C", "D"])
  # Access "F".
  cache.access_page("F")
  # The cache is full, so we need to remove the least recently accessed page "C".
  # The cache is updated to:
  #   (most recently accessed)<-- "F", "E", "A", "C" -->(least recently accessed)
  equal(cache.get_pages(), ["F", "E", "A", "C"])
  print("OK!")

# A helper function to check if the contents of the two lists is the same.
def equal(list1, list2):
  if len(list1) != len(list2):
    return False
  for i in range(len(list1)):
    if list1[i] != list2[i]:
      return False
  return True

if __name__ == "__main__":
  cache_test()
