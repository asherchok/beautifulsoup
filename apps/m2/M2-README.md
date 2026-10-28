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
