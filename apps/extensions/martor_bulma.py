import logging
import re

import markdown

logger = logging.getLogger(__name__)


class BulmaHeaderPostprocessor(markdown.postprocessors.Postprocessor):
    RE = re.compile(r"<h(\d)>")

    def run(self, text):
        text, _ = self.RE.subn(r'<h\1 class="title is-\1">', text)
        return text


class BulmaStyleExtension(markdown.extensions.Extension):
    """Add required style for Bulma"""

    def extendMarkdown(self, md: markdown.Markdown, md_globals):
        md.registerExtension(self)
        md.postprocessors.register(BulmaHeaderPostprocessor(self), "bulma-header", 10)


def makeExtension(**kwargs):
    return BulmaStyleExtension(**kwargs)
