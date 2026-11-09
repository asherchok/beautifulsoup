# Milestone-4

## Iterable BeautifulSoup

A `BeautifulSoup` object can now be looped over directly. The loop visits **every node in the tree** (tags, text, comments), one at a time, in document order:

```python
soup = BeautifulSoup(html_doc, "html.parser")
for node in soup:
    print(node)
```

For `<div><p>A<b>B</b></p><i>C</i></div>` this produces `div, p, "A", b, "B", i, "C"`, a depth-first pre-order traversal (each node before its children, children left to right).

### The change

`bs4/__init__.py:495`, in `class BeautifulSoup(Tag)`:

```python
def __iter__(self):
    return self.descendants
```

### Justification for this fix
Why is this change so minimal?

**1. The library already has a lazy pre-order walker.** `Tag.descendants` (`bs4/element.py:2764`) is a generator. It starts at the first child and follows each node's `.next_element` link, `yield`ing one node at a time. It never collects the nodes onto a list, which is exactly what this milestone requires. Writing a second walker would duplicate it.

**2. BeautifulSoup itself trusts it.** `Tag.__deepcopy__` (`bs4/element.py:1758`) copies a whole tree by walking `self.descendants` (line 1768), specifically so that it can do this "without making any recursive function calls" (line 1766). Reusing the same walker keeps one implementation of tree traversal in the code base.

**3. It handles cases a hand-written walk would have to reinvent.** `descendants` computes a `stopNode` (line 2774), the node after the last descendant, so it stops exactly at the end of the subtree instead of running on along the `.next_element` chain. It also returns immediately for an empty document.

**4. Every loop gets a fresh generator.** `descendants` is a property, so each `iter(soup)` creates a new generator. Two loops over the same soup are independent, and the soup can be looped over any number of times.

**5. It is not recursive.** It is a `while` loop, so it works on documents nested deeper than Python's recursion limit (~1000). The tests use 3000 levels.

Why was the change applied to only `BeautifulSoup`, not every `Tag`? `Tag.__iter__` (`bs4/element.py:2208`) iterates over a tag's **direct children** (`iter(self.contents)`). Existing user code and BeautifulSoup's own tests rely on that. The assignment asks for the *soup* to be iterable, so the override is placed on `BeautifulSoup` only.

### Misc

**AI caught an error on the existing documentation.** The docstrings of `descendants` and `self_and_descendants` (`bs4/element.py:2766` and `2759`) say "breadth-first sequence". That is incorrect: the traversal is depth-first pre-order. Breadth-first would visit `div, p, i, "A", b, "C", "B"`, level by level. The behaviour was checked directly rather than taken from the docstring.

### Tests

`bs4/tests/test_soup.py`, class `TestMileStoneFourIterableSoup`:

- `test_iteration_is_lazy`: each `next()` produces exactly the next node in pre-order.
- `test_iteration_stops_after_last_node`: all nodes come out once, then `StopIteration`. (`islice` caps the count, so an endless iterator fails the test instead of hanging it.)
- `test_void_tags_are_visited_without_children`: `<br>`, `<br/>` and `<img/>` are visited, and the text after them is a sibling, not a child.
- `test_each_iter_gets_fresh_generator`: two iterators are independent, and the soup can be looped over repeatedly.
- `test_deep_nesting_does_not_raise_recursion_error`: 3000 nested `<div>`s, generated at runtime, are all visited in order.