import sys, os
from bs4 import BeautifulSoup, SoupStrainer


def pick_parser(path):
    """Choose a parser from the file extension (.html -> html.parser, .xml -> xml)."""
    file_ext = os.path.splitext(path)[1].lstrip('.')
    if file_ext == "html":
        return 'html.parser'
    elif file_ext == "xml":
        # The 'xml' parser needs lxml installed (pip install lxml).
        return 'xml'
    else:
        raise NotImplementedError(f"{file_ext} has not been implemented.")


def get_tag_names(markup, parser='html.parser'):
    """Return the name of every tag in the document, in document order."""
    # An empty SoupStrainer matches everything, so nothing is skipped...??
    # Just leave it like this. Hopefully it'd do something to memory efficiency
    # task 3 needs every tag, which leaves SoupStrainer nothing to filter out.
    soop = SoupStrainer()
    soup = BeautifulSoup(markup, parser, parse_only=soop)
    # task-3's job is print out all the tags in the document.
    return [tag.name for tag in soup.find_all()]


def main():
    if len(sys.argv) != 2:
        print("Please supply an argument for the relevant HTML file.")
        return
    parser = pick_parser(sys.argv[1])

    # 'rb' lets BeautifulSoup detect the file's encoding itself
    with open(sys.argv[1], 'rb') as fp:
        names = get_tag_names(fp, parser)

    for name in names:
        print(name)


if __name__ == "__main__":
    main()