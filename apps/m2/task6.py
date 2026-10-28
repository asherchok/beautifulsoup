import csv
import json
import sys, os
from bs4 import BeautifulSoup, SoupReplacer

def main():
    if len(sys.argv) < 2:
        print("Please supply an argument for the relevant HTML file.")
        return
    filename = os.path.splitext(sys.argv[1])[0]
    file_ext = os.path.splitext(sys.argv[1])[1].lstrip('.')

    with open(sys.argv[1]) as fp:
        if file_ext == "html":
            soup = BeautifulSoup(fp, 'html.parser', replacer=SoupReplacer("b", "blockquote"))
        elif file_ext == "xml":
            soup = BeautifulSoup(fp, 'xml', replacer=SoupReplacer("b", "blockquote"))
        else:
            raise NotImplementedError(f"{file_ext} has not been implemented.")

    # task-6's job is to change all the <b> tags to <blockquote> tags and write the tree onto a file.
    # Instead of this (in M1), it is passed to argument above
    # target_headers = soup.find_all("b")
    #
    # for header in target_headers:
    #    header.name = "blockquote"
    

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