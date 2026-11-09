import pytest
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

    def test_error_when_only_one_tag_given(self):
        with pytest.raises(ValueError):
            SoupReplacer("b")

    def test_error_when_nothing_given(self):
        with pytest.raises(ValueError):
            SoupReplacer()

    def test_name_xformer_renames_tag(self):
        html = "<p>Hi <b>there</b></p>"
        b_to_blockquote = SoupReplacer(name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name)
        soup = self.soup(html, replacer=b_to_blockquote)
        assert soup.decode() == "<p>Hi <blockquote>there</blockquote></p>"
    
    def test_name_xformer_closes_tag_correctly(self):
        html = "<p><b>bold</b> after</p>"
        replacer = SoupReplacer(name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name)
        soup = self.soup(html, replacer=replacer)
        assert soup.decode() == "<p><blockquote>bold</blockquote> after</p>"

    def test_attrs_xformer_replaces_attributes(self):
        def add_test_class(tag):
            if tag.name == "p":
                new_attrs = dict(tag.attrs)
                new_attrs["class"] = "test"
                return new_attrs
            return tag.attrs

        html = "<p>a</p><p>b</p>"
        replacer = SoupReplacer(attrs_xformer=add_test_class)
        soup = self.soup(html, replacer=replacer)
        assert soup.decode() == "<p class=\"test\">a</p><p class=\"test\">b</p>"

    def test_xformer_side_effect_changes_tag(self):
        def remove_class_attr(tag):
            if "class" in tag.attrs:
                del tag.attrs["class"]

        html = "<p class=\"x\">hi</p>"
        remover = SoupReplacer(xformer=remove_class_attr)
        soup = self.soup(html, replacer=remover)
        assert soup.decode() == "<p>hi</p>"