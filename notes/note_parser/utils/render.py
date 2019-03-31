import markdown


def get_rendered_markdown(file_path):

    with open(file_path, 'r') as input_file_object:
        markdown_content = input_file_object.read()

    html_content = markdown.markdown(markdown_content, extensions=['fenced_code'])
    return html_content
