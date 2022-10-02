'''
Regular Expression Library used by Shorthand.
'''

# General
#   Matches a valid Date Stamp
DATE_STAMP_PATTERN = r'[1-2][0-9]{3}\-[0-3][0-9]\-[0-3][0-9]'
#   Matches a valid Date Stamp within parentheses
START_STAMP_PATTERN = r'\(' + DATE_STAMP_PATTERN + r'\)'
#   Matches two valid Date Stamps within parentheses with an arrow between
END_STAMP_PATTERN = r'\(' + DATE_STAMP_PATTERN + r' -> ' + \
                    DATE_STAMP_PATTERN + r'\)'

# To-Dos
#   Matches all valid prefixes for incomplete, complete, or skipped todos
CATCH_ALL_PATTERN = r'(^\s*)([-+*] )(\[[XS ]?\])( [a-zA-Z1-9\(\)])'
#   Matches all incomplete todos with valid timestamps
VALID_INCOMPLETE_PATTERN = r'[-+*] \[ \] ' + START_STAMP_PATTERN
#   Matches all completed or skipped todos with valid start and end timestamps
VALID_COMPLETE_PATTERN = r'[-+*] \[[XS]\] ' + END_STAMP_PATTERN
#   Matches incomplete todos without a valid start timestamp
UNFINISHED_UNSTAMPED_PATTERN = r'(^\s*)([-+*] )(\[ ?\]) (?!' + \
                               START_STAMP_PATTERN + r')'
#   Matches completed or skipped todos with only the start timestamp
FINISHED_START_STAMPED_PATTERN = r'(^\s*)([-+*] )(\[)([XS])(\] )(\()(' + \
                                 DATE_STAMP_PATTERN + r')(\)) '
#   Matches completed or skipped todos with no valid timestamp
FINISHED_UNSTAMPED_PATTERN = r'(^\s*)([-+*] )(\[)([XS])(\] )(?!(' + \
                             START_STAMP_PATTERN + r'|' + \
                             END_STAMP_PATTERN + r'))'
#   Matches the prefix of a skipped todo
SKIPPED_PREFIX_GREP = r'(^\s*)([-+*] )(\[S\])( [a-zA-Z1-9\(\)])'
#   Matches the prefix of an incomplete todo
INCOMPLETE_PREFIX_GREP = r'(^\s*)([-+*] )(\[ ?\])( [a-zA-Z1-9\(\)])'
#   Matches the prefix of a complete todo
COMPLETE_PREFIX_GREP = r'(^\s*)([-+*] )(\[X\])( [a-zA-Z1-9\(\)])'
#   Matches a start stamp and todo without the prefix
START_STAMP_ONLY_PATTERN = r'(\()(' + DATE_STAMP_PATTERN + r')(\))( )(.*)'
#   Matches an end stamp and todo without the prefix
START_END_STAMP_ONLY_PATTERN = r'(\()(' + DATE_STAMP_PATTERN + r')( -> )(' + \
                               DATE_STAMP_PATTERN + r')(\))( )(.*)'

# Questions & Answers
#   Matches either a question or answer
QUESTION_OR_ANSWER = r'(^\s*)([-+*] )([\?@] )(.*)'
#   Matches a question
ALL_QUESTIONS = r'(^\s*)([-+*] )(\? )(.*)'
UNSTAMPED_QUESTION = r'(^\s*)([-+*] )(\? )(?!' + START_STAMP_PATTERN + r' )'
STAMPED_QUESTION = r'\? ' + START_STAMP_PATTERN + r' '
#   Matches an answer
ANSWER_PATTERN = r'(^\s*)([-+*] )(@ )(.*)'
UNSTAMPED_ANSWER = r'(^\s*)([-+*] )(@ )(?!' + START_STAMP_PATTERN + r' )'
STAMPED_ANSWER = r'(@ )(\()' + DATE_STAMP_PATTERN + r'(\)) '

#   Matches a today placeholder
TODAY_GREP = r'"\\\today"'
TODAY_LINE_PATTERN = r'(.*)(\\today)(.*)'

#   Matches a tag
TAG_FILTER = r'( :\w+:)'
TAG_PATTERN = r'( :\w+:)($|(?= ))'

#   Matches a definition
DEFINITION_PATTERN = r"^(\s*)([-+*] )(\{[-_+ \w]*?\} )(.*)"

#   Matches any heading
HEADING_PATTERN = r'^(#+)( )(.*)'
#   Matches any heading which ends with a datestamp
DATED_HEADING_PATTERN = r'^(#+)( )(.*)(' + DATE_STAMP_PATTERN + r')'

#   Matches the beginning of a record set
RECORD_SET_PATTERN = r'^```rec-data$'

#   Matches any link
LINK_PATTERN = r'\s\[.*?\]\(.*?\)'
ALL_LINK_PATTERN = r'\s(\[[^\[]*?\]\()(.*?)(\))'
#   Matches a link to another note
INTERNAL_LINK_PATTERN = r'(\s)(\[[^\[]*?\]\()((?!(https://|http://)).*?)(\))'

# Matches any Image
IMAGE_PATTERN = r'!\[(.*?)\]\((.*?)\)'

#   Matches a GPS location
GPS_PATTERN = r"(GPS\[)(-?1?\d{1,2}\.\d{3,6})(, ?)"\
              r"(-?1?\d{1,2}\.\d{3,6})(, ?)?([\w ]+)?(\])"


CHARS_TO_ESCAPE = ['`']


def escape_for_cli(input_pattern):
    '''Patterns which include special characters must
    be escaped before being used on the command line
    '''

    clean_pattern = ''

    while input_pattern:
        next_char = input_pattern[0]
        if next_char in CHARS_TO_ESCAPE:
            clean_pattern += '\\' + next_char
            input_pattern = input_pattern[1:]
        else:
            clean_pattern += next_char
            input_pattern = input_pattern[1:]

    return clean_pattern
