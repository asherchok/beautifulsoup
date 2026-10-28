from bs4 import SoupReplacer
from . import SoupTest

class TestSoupReplacer(SoupTest):
    """Test the ability to replace tags in real time"""
    def test_replacer_to_handle_alt_tag(self):
        html = "<p>Hi <b>there</b></p>"
        soup = self.soup(html, replacer=SoupReplacer("b", "blockquote"))
        assert soup.decode() == "<p>Hi <blockquote>there</blockquote></p>"

    def test_replacer_closes_tag_correctly(self):
        html = "<p><b>bold</b> after</p>"
        soup = self.soup(html, replacer=SoupReplacer("b", "blockquote"))
        assert soup.decode() == "<p><blockquote>bold</blockquote> after</p>"