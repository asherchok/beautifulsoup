# Milestone-3

## SoupReplacer with transformer functions

`SoupReplacer` now also accepts functions ("transformers") that are called on every tag **during parsing**:

```python
SoupReplacer(og_tag=None, alt_tag=None, *, name_xformer=None, attrs_xformer=None, xformer=None)
```

| Argument | Receives | Must | Example |
|---|---|---|---|
| `name_xformer` | the tag | return the new name | `lambda tag: "blockquote" if tag.name == "b" else tag.name` |
| `attrs_xformer` | the tag | return the new attributes (a dict) | add `class="test"` to every `<p>` |
| `xformer` | the tag | change the tag directly, return nothing | delete every `class` attribute |

The Milestone 2 form, `SoupReplacer("b", "blockquote")`, still works. The transformers are keyword-only (after `*`), so they cannot be mixed up with `og_tag`/`alt_tag` by position. A `ValueError` is raised if only one of `og_tag`/`alt_tag` is given, or if nothing is given at all.

### Changes to the source

- `bs4/filter.py`: the new constructor arguments, stored on the object, plus the `ValueError` checks.
- `bs4/__init__.py`:
  - `handle_starttag`: right after the `Tag` is created, the transformers run in a fixed order: `name_xformer`, then `attrs_xformer`, then `xformer`. They need the tag object, so this has to happen after creation (in Milestone 2 the name was swapped before creation).
  - `handle_endtag`: a closing tag still carries the **original** name (`</b>`), while the open tag may now be called `blockquote`. Each tag therefore records its original name (`_original_name`) when it is created, and `handle_endtag` closes the open tag whose original name matches. This also covers an `xformer` that renames a tag.

### Tests

`bs4/tests/test_replacer.py`, 6 new tests:

- `test_error_when_only_one_tag_given`, `test_error_when_nothing_given`: invalid constructor calls raise `ValueError`.
- `test_name_xformer_renames_tag`: `<b>` becomes `<blockquote>`.
- `test_name_xformer_closes_tag_correctly`: text after a renamed tag stays outside it (end-tag matching).
- `test_attrs_xformer_replaces_attributes`: every `<p>` gets `class="test"`.
- `test_xformer_side_effect_changes_tag`: an `xformer` deletes the `class` attribute.

The full suite passes (747 passed, with lxml 5.x).

### Application: task7.py

Milestone 1 task 7 (add `class="test"` to every `<p>`), done during parsing with `SoupReplacer(attrs_xformer=add_test_class)` instead of a loop afterwards:

```bash
python3 task7.py small.html        # writes small-soup.html
```

## Technical brief: SoupReplacer in Milestone 2 vs. Milestone 3

**Milestone 2: `SoupReplacer(og_tag, alt_tag)`**

- Easy to read and impossible to misuse: one tag name in, one tag name out.
- The library knows exactly what will change (only names), so matching end tags is a one-line lookup.
- Very limited. It can rename one tag per replacer, and nothing else: no attributes, no conditions (e.g. "only `<b>` inside a `<p>`").

**Milestone 3: transformer functions**

- Much more powerful. Any rule that can be written as a Python function works, including conditions on the tag's attributes or parent. The Milestone 2 form is just a special case (`name_xformer` that renames one tag).
- Harder to use correctly. Users must know which functions return a value and which mutate the tag, and quirks like `class` being a list leak into their code.
- Harder to implement safely. `xformer` can change anything, so the library has to defend against changes it cannot predict. For example, renaming forced us to remember every tag's original name to keep end tags matching.
- Limited by when it runs. Transformers are called when the start tag is seen, so the tag's text and children do not exist yet and cannot be used in a rule. They also cannot remove a tag or add new ones.
- Every transformer is a Python call on every tag, even tags it does not change, which adds parsing cost on large documents.

**Recommendation**


1. Keep the simple `SoupReplacer(og_tag, alt_tag)` form as the documented, everyday API, implemented on top of the transformer machinery so there is only one code path.
2. Offer `name_xformer` and `attrs_xformer` as the main extension points. They return values instead of mutating, so they are easier to reason about and test.
3. Treat `xformer` as an advanced escape hatch, and document clearly what it may and may not change.
4. Document the limits: transformers see the tag before its contents are parsed, run in a fixed order, and do not apply to the `html5lib` builder, which builds its tree without going through `handle_starttag`/`handle_endtag`.
