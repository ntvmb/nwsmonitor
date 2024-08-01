from html.parser import HTMLParser


class RSSParser(HTMLParser):
    _last_article = {}
    _article_list = []
    _next_data = None

    def handle_starttag(self, tag, attrs):
        if tag == "item":
            self._last_article.clear()
        if tag != "pre":
            self._next_data = tag

    def handle_endtag(self, tag):
        if tag == "item":
            self._article_list.append(self._last_article.copy())

    def handle_data(self, data):
        self._last_article[self._next_data] = data

    def unknown_decl(self, decl: str):
        # Interpret as data
        self.handle_data("\n".join(decl.splitlines()[1:-1]))

    def reset(self):
        super().reset()
        self._last_article.clear()
        self._article_list.clear()

    @property
    def article_list(self):
        return self._article_list
