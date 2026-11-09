import csv
import json
import sys, os
from bs4 import BeautifulSoup, SoupReplacer

# from test_replacer
def add_test_class(tag):
    if tag.name == "p":
        new_attrs = dict(tag.attrs)
        new_attrs["class"] = "test"
        return new_attrs
    return tag.attrs

def main():
    if len(sys.argv) < 2:
        print("Please supply an argument for the relevant HTML file.")
        return
    filename = os.path.splitext(sys.argv[1])[0]
    file_ext = os.path.splitext(sys.argv[1])[1].lstrip('.')

    replacer = SoupReplacer(attrs_xformer=add_test_class)

    with open(sys.argv[1]) as fp:
        if file_ext == "html":
            soup = BeautifulSoup(fp, 'html.parser', replacer=replacer)
        elif file_ext == "xml":
            soup = BeautifulSoup(fp, 'xml', replacer=replacer)
        else:
            raise NotImplementedError(f"{file_ext} has not been implemented.")
        
    # task-7: class="test" was already added to every <p> during parsing
    # (attrs_xformer above), so there is no second pass over the tree.

    if (len(sys.argv) < 3): # default to HTML
        new_filename = filename + "-soup.html"

        with open(new_filename, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
    else:
        if sys.argv[2] == "txt":
            new_filename = filename + "-soup.txt"
            
            with open(new_filename, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
        elif sys.argv[2] == "csv":
            new_filename = filename + "-soup.csv"  # assign filename
            links = [[a.get('href'), a.text] for a in soup.find_all('a')]  # extract data
            with open(new_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['href', 'text'])
                writer.writerows(links)            # write data rows
        elif sys.argv[2] == "json":
            new_filename = filename + "-soup.json"
            links = [{'href': a.get('href'), 'text': a.text} for a in soup.find_all('a')]  # extract data
            with open(new_filename, 'w', encoding='utf-8') as f:
                json.dump(links, f, ensure_ascii=False, indent=2)
        else:
            raise NotImplementedError(f"{sys.argv[2]} has not been implemented.")


if __name__ == "__main__":
    main()