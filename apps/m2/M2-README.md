# Milestone-2

## Part 1: SoupStrainer on a large file

### Test file

`big.html` is a **1.36 GB** synthetic HTML file made by the Milestone 1 generator (`test/Synthetic/generate.py`, `depth=1200`, `repeat=500`), with one `<a>` tag added per block:

- 500 blocks, each **1200 `<div>`s nested inside one another** (600,000 divs in total)
- **every `<div>` has an `id`** (`id='block-{i}-depth-{d}'`)
- at the deepest level of each block: one `<p>` and one `<a href=...>` (500 of each)
- most of the file size is indentation whitespace

The file is not committed (it is listed in `.gitignore`). It can be regenerated with the Milestone 1 generator (that script is not part of this repository):

```bash
python3 path/to/Milestone-1/test/Synthetic/generate.py big.html
```

### Method

Each Milestone 2 task was timed against its Milestone 1 version (no SoupStrainer), on the same machine, one run each, with the printed output sent to `/dev/null` so that only parsing and searching are measured:

```bash
/usr/bin/time -l python3 <script>.py big.html > /dev/null
```

`real` is wall-clock time; memory is the "maximum resident set size" (peak memory).

### Results

| Task | Strainer used | Without SoupStrainer (M1) | With SoupStrainer (M2) | Time saved | Peak memory: M1 → M2 |
|---|---|---|---|---|---|
| 2: all `<a>` tags | `SoupStrainer("a")` | 81.4 s | **54.5 s** | **−33%** | 3.45 GB → **2.95 GB** |
| 3: all tags | `SoupStrainer()` | 78.1 s | 76.1 s | ~0% (noise) | 3.84 GB → 3.88 GB |
| 4: tags with an `id` | `SoupStrainer(id=True)` | 76.5 s | 77.1 s | ~0% (noise) | 3.87 GB → 3.87 GB |

All three Milestone 2 programs processed the 1.36 GB file successfully.

### Discussion

**SoupStrainer only helps when it can throw parts of the document away.** It decides, during parsing, which nodes get built into the tree; anything it does not match is never created.

- **Task 2** is the best case. Only 500 of about 600,000 elements are `<a>` tags, so the strainer skips building almost the whole tree. Parsing was 33% faster and peak memory dropped by about 0.5 GB.
- **Task 3** is the worst case by definition. Listing every tag means the strainer has to keep every tag, so an empty `SoupStrainer()` matches everything and does the same work as no strainer at all. SoupStrainer cannot make this task cheaper.
- **Task 4** is also a worst case, but because of the file. Every `<div>` has an `id`, and when SoupStrainer matches a tag it keeps that tag's **entire subtree**. The outermost div of each block matches, so every block is kept whole, and so is the whole document. On a file where only a few elements had an `id`, task 4 would behave like task 2.

**Memory does not go down much, even in the best case.** With almost nothing kept (task 2), peak memory is still about 2.95 GB, more than twice the file size. BeautifulSoup reads the entire document into memory before parsing starts, and SoupStrainer only shrinks the tree that gets built *from* it. To process files much larger than available memory, the input would have to be read and parsed in pieces (streaming), which this API does not do.

**Note on printing.** In Milestone 1, tasks 3 and 4 printed `str(tag)`, which serializes a tag *together with everything inside it*. In a document nested 1200 levels deep, that adds up to hundreds of GB of output, and those versions never finish on `big.html`. For these measurements, both the M1 and M2 versions of tasks 3 and 4 print `tag.name` (plus `tag['id']` for task 4) instead.

## Part 2: API function locations

Locations of every BeautifulSoup API used in Milestone 1 (tasks 1–8) and Milestone 2 Part 1, in the original, unmodified source.

| API | Used in | Defined at |
|---|---|---|
| `BeautifulSoup(...)` | all tasks | `bs4/__init__.py:133` (class), `:209` (`__init__`) |
| `parse_only=` | M2 tasks 2–4 | `bs4/__init__.py:214` |
| `SoupStrainer(...)` | M2 tasks 2–4 | `bs4/filter.py:313` (class), `:345` (`__init__`) |
| `prettify()` | M1 tasks 1, 6–8 | `bs4/element.py:2601` |
| `find_all()` | M1 tasks 1–8, M2 tasks 2–4 | `bs4/element.py:2715` |
| `find_parent()` | M1 task 5 | `bs4/element.py:992` |
| `get()` | M1 tasks 1, 2, 6–8; M2 task 2 | `bs4/element.py:2160` |
| `.text` | M1 tasks 1, 2, 6–8; M2 task 2 | `bs4/element.py:550` (property for `get_text`, `:524`) |
| `.name` (read and assign) | M1 tasks 3, 6; M2 tasks 3, 4 | `bs4/element.py:1648` (set in `Tag.__init__`) |
| `tag['class'] = ...` | M1 task 7 | `bs4/element.py:2223` (`Tag.__setitem__`) |
| `tag['id']` | M2 task 4 | `bs4/element.py:2203` (`Tag.__getitem__`) |
| `.string` | M1 task 8 | `bs4/element.py:1837` |
| `wrap()` | M1 task 8 | `bs4/element.py:577` |
| `new_tag()` | M1 task 8 | `bs4/__init__.py:682` |

## Part 3: SoupReplacer

`SoupReplacer` renames tags **during parsing**, so there is no second pass over the finished tree (Milestone 1 task 6 parsed first, then looped over `find_all("b")` to rename each tag).

```python
from bs4 import BeautifulSoup, SoupReplacer

b_to_blockquote = SoupReplacer("b", "blockquote")
print(BeautifulSoup(html_doc, "html.parser", replacer=b_to_blockquote).prettify())
```

### Changes to the source

- `bs4/filter.py`: new `SoupReplacer(og_tag, alt_tag)` class, next to `SoupStrainer`. `get_replacement_name(name)` returns `alt_tag` when `name == og_tag`, otherwise `name` unchanged.
- `bs4/__init__.py`:
  - `SoupReplacer` is imported, so `from bs4 import SoupReplacer` works.
  - `BeautifulSoup.__init__` takes an optional `replacer=None` argument, stored as `self.replacer` (the same pattern as `parse_only`).
  - `handle_starttag` and `handle_endtag` replace `name` before the tag is created or closed. Both are needed: if only the start tag were renamed, `</b>` would not close the `<blockquote>`, and the text after it would end up inside it.

The `html.parser`, `lxml` and `xml` tree builders all call these two `BeautifulSoup` methods, so the replacer works with all of them, and for self-closing tags too. (`html5lib` builds its tree differently and is not covered.)

### Tests

`bs4/tests/test_replacer.py`:

- `test_replacer_to_handle_alt_tag`: `<b>` is renamed to `<blockquote>`, other tags are untouched.
- `test_replacer_closes_tag_correctly`: text after `</b>` stays outside the new `<blockquote>`, which checks the end-tag handling.

The full test suite passes (741 passed) with lxml 5.x. Note: lxml 6 makes 3 existing tests in `test_lxml.py` fail, in the original code as well, independent of these changes.

### Application: task6.py

Milestone 1 task 6 (change all `<b>` tags to `<blockquote>`), now using `SoupReplacer` instead of a loop after parsing. For example, take a random `small.html` file:

```bash
python3 task6.py small.html        # writes small-soup.html
```

`small.html` covers text after a `<b>`, `<b>` in different places, untouched tags, and nested `<b>` tags. All of them come out as correctly nested `<blockquote>`s.
