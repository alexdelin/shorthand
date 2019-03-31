import markdown2


def get_rendered_markdown(file_path):

    with open(file_path, 'r') as input_file_object:
        markdown_content = input_file_object.read()

    html_content = markdown2.markdown(markdown_content)
    return html_content
