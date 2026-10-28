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


def get_links(markup, parser='html.parser'):
    """Return every <a> tag, parsing only the <a> tags via SoupStrainer."""
    only_a_tags = SoupStrainer("a")
    soup = BeautifulSoup(markup, parser, parse_only=only_a_tags)
    # task-2's job is to show all <a> tags
    return soup.find_all('a')


def main():
    if len(sys.argv) != 2:
        print("Please supply an argument for the relevant HTML file.")
        return
    parser = pick_parser(sys.argv[1])

    # 'rb' lets BeautifulSoup detect the file's encoding itself
    with open(sys.argv[1], 'rb') as fp:
        links = get_links(fp, parser)

    for link in links:
        print(link)              # prints the entire <a> tag and its contents
        print(link.get('href'))  # prints just the href attribute value
        print(link.text)         # prints just the visible text inside the tag


if __name__ == "__main__":
    main()