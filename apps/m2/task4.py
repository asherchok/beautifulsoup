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


def get_tags_with_id(markup, parser='html.parser'):
    """Return every tag that has an id attribute."""
    # Match any tag that possesses an 'id' attribute
    only_id = SoupStrainer(id=True)
    soup = BeautifulSoup(markup, parser, parse_only=only_id)
    # The strainer keeps a matched tag's whole subtree, so children without
    # an id survive parsing; find_all(id=True) filters them back out.
    # task-4's job is to print out all the tags that have an id attribute.
    return soup.find_all(id=True)


def main():
    if len(sys.argv) != 2:
        print("Please supply an argument for the relevant HTML file.")
        return
    parser = pick_parser(sys.argv[1])

    # 'rb' lets BeautifulSoup detect the file's encoding itself
    with open(sys.argv[1], 'rb') as fp:
        tags = get_tags_with_id(fp, parser)

    for tag in tags:
        print(tag.name, tag['id'])  # str(tag) serializes the whole subtree: too slow on GB nested files


if __name__ == "__main__":
    main()