import re
from bs4 import BeautifulSoup
"""
一个用于过滤文档中的HTML标签的工具类
"""


class HtmlExtractor:
    @staticmethod
    def handle(text):
        bs = BeautifulSoup(text, 'lxml')

    @staticmethod
    def clean_format(text):
        """
        clean text format for text extract from html
        :param text:
        :return:
        """
        pattern = re.compile(r'\s+')
        return re.sub(pattern, " ", text.replace('\n', ' ').replace(u'\u00a0', " "))

    @staticmethod
    def clean_html_text(html_text):
        if html_text is None or html_text == "":
            return ""
        soup = BeautifulSoup(html_text, "lxml")
        # codeTags = soup.find_all(name=["pre", 'blockquote'])
        code_block_tags = soup.find_all(name=['blockquote', 'pre'])
        code_tags = soup.find_all(name=['code'])
        clean_text = soup.get_text()
        # cleanText = clean_format(cleanText)
        for tag in code_block_tags:
            if tag.text:
                a = "<expression>" + tag.get_text() + "</expression>"
                clean_text = clean_text.replace(tag.get_text(), a)
        for tag in code_tags:
            if tag.text:
                a = "<code>" + tag.get_text() + "</code>"
                clean_text = clean_text.replace(tag.get_text(), a)
        clean_text = clean_text.replace("<expression><expression>","<expression>")
        clean_text = clean_text.replace("</expression></expression>","</expression>")
        return HtmlExtractor.clean_format(clean_text)

    @staticmethod
    def replace(text):
        """
        {@code} {@docroot} {@link}
        :param text:
        :return:
        """
        code_pattern = re.compile('\{\@code\s(#.*?)?(.*?)\}', )
        link_pattern = re.compile('\{\@link\s(#.*?)?(.*?)\}')
        linkplain_pattern = re.compile('\{\@linkplain\s(#.*?)?(.*?)\}')
        ra = re.finditer(code_pattern, text)
        rl = re.finditer(link_pattern, text)
        rlp = re.finditer(linkplain_pattern, text)
        if ra:
            for i in ra:
                text = text.replace(i.group(), "<noun>"+i.group(2)+"</noun>")
        if rl:
            for i in rl:
                sp = i.group(2).split(" ")
                replaced = sp[1] if len(sp) > 1 else sp[0]
                text = text.replace(i.group(), "<noun>"+replaced+"</noun>")
        if rlp:
            for i in rlp:
                sp = i.group(2).split(" ")
                if len(sp) > 1:
                    sp.pop(0)
                    replaced = " ".join(sp)
                else:
                    replaced = sp[0]
                print(sp)
                text = text.replace(i.group(), "<noun>"+replaced+"</noun>")
        return text

    @staticmethod
    def remove(text):
        text = text.replace("<noun>", "")
        text = text.replace("</noun>", "")
        text = text.replace("<code>", "")
        text = text.replace("</code>", "")
        text = text.replace("<expression>", "")
        text = text.replace("</expression>", "")
        text = text.replace("/**", "")
        text = text.replace("*/", "")
        text = text.replace(" * ", " ")
        text = text.replace("@serial", "")
        text = text.replace("@serialData", "")
        text = text.replace("@serialField", "")
        text = text.replace("@see", "see")
        return text

    @staticmethod
    def html_remove(text):
        text = HtmlExtractor.clean_html_text(text)
        text = HtmlExtractor.clean_format(text)
        text = HtmlExtractor.remove(text)
        text = HtmlExtractor.replace(text)
        return text
