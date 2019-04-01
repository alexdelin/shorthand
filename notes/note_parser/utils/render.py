import codecs

import markdown


def get_rendered_markdown(file_path):

    with codecs.open(file_path, mode="r", encoding="utf-8") as input_file_object:
        markdown_content = input_file_object.read()

    html_content = markdown.markdown(markdown_content, extensions=['fenced_code'])
    return html_content
