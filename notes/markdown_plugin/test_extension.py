from __future__ import absolute_import
from __future__ import unicode_literals

import markdown
from markdown.extensions import Extension

from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import SimpleTagPattern
from markdown.util import etree
import re


class ABDNotesProcessor(BlockProcessor):
    """ Admonition extension for Python-Markdown. """

    RE = re.compile(r'(^|\n)(\s*\[[ XS]\] )(.*?)(\n|$)')

    def test(self, parent, block):
        match = bool(self.RE.search(block))
        print('------')
        print(block)
        print(match)
        return match

    def run(self, parent, blocks):
        raw_block = blocks.pop(0)
        block_lines = raw_block.split('\n')
        print(block_lines)
        todo_elem = etree.SubElement(parent, 'todo')
        todo_elem.text = 'hello!'
        blocks.insert(0, todo_elem)


class ABDNotesExtension(Extension):
    """ Add definition lists to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add Admonition to Markdown instance. """

        md.parser.blockprocessors.register(ABDNotesProcessor(md.parser), 'abd_notes', 25)


test_text = '''## ToDo List
[ ] (2019-03-20) more stuff to do
[X] (2019-03-20 -> 2019-03-20) Can even add to-dos into here'''

print(markdown.markdown(test_text, extensions=[ABDNotesExtension()]))
