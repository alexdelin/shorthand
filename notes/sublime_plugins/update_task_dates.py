import sublime
import sublime_plugin

from datetime import datetime
import re


class ExampleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        all_content_region = sublime.Region(self.view.substr(sublime.Region(0, self.view.size())))
        print(type(all_content_region))
        all_lines = self.view.split_by_newlines(all_content_region)
        print(len(all_lines))


class TriggerUpdateTaskDates(sublime_plugin.EventListener):
    '''
    Process can be simply done via find and
    replce with these regexes

    Unstamped unfinished todos:
        '(\[ \]|\[\]) (?!\([1-2]\d{3}\-\d{2}\-\d{2}\))'
        '\[ \] (date-string) '

    Unstamped finished todos with start stamped:
        '\[X\] \([1-2]\d{3}\-\d{2}\-\d{2}\) '
        '\[X\] (date-string -> date-string) '

    Unstamped finished todos with no stamp:
        '\[X\] (?!(\([1-2]\d{3}\-\d{2}\-\d{2}\)|\([1-2]\d{3}\-\d{2}\-\d{2} -> [1-2]\d{3}\-\d{2}\-\d{2}\)))'
        '\[X\] (date-string -> date-string) '
    '''
    def on_pre_save(self, edit):

        # all_content = edit.substr(sublime.Region(0, edit.size()))
        # all_content_region = sublime.Region(all_content)
        edit.run_command('example')
        '''

        new_content = []

        for line in all_lines:
            print(line)

            if line.lstrip()[:3] == '[] ' or line.lstrip()[:4] == '[ ]':
                # Apply Regex for Unfinished To-Dos
                new_content.append(line)
            elif line.lstrip()[:4] == '[X]':
                # Apply Regexes for Finished To-Dos
                new_content.append(line)
            else:
                # Line is not a To-Do
                new_content.append(line)

        final_content = '\n'.join(new_content)

        # Erase full document
        # Replace with new document
'''
