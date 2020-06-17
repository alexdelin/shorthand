'''
Regular Expression Library used by Shorthand.
Patterns that begin with `"` characters are meant to be used with `grep`
via the command line
'''

# General
## Matches a valid Date Stamp
DATE_STAMP_PATTERN = r'[1-2][0-9]{3}\-[0-3][0-9]\-[0-3][0-9]'
## Matches a valid Date Stamp within parentheses
START_STAMP_PATTERN = r'\(' + DATE_STAMP_PATTERN + r'\)'
## Matches two valid Date Stamps within parentheses with an arrow between
END_STAMP_PATTERN = r'\(' + DATE_STAMP_PATTERN + r' -> ' + DATE_STAMP_PATTERN + r'\)'

# To-Dos
## Matches all valid prefixes for incomplete, complete, or skipped todos
CATCH_ALL_PATTERN = r'(^\s*)(\[[XS ]?\])( [a-zA-Z1-9\(\)])'
## Matches all incomplete todos with valid timestamps
VALID_INCOMPLETE_PATTERN = r'\[ \] ' + START_STAMP_PATTERN
## Matches all completed or skipped todos with valid start and end timestamps
VALID_COMPLETE_PATTERN = r'\[[XS]\] ' + END_STAMP_PATTERN
## Matches incomplete todos without a valid start timestamp
UNFINISHED_UNSTAMPED_PATTERN = r'(^\s*)(\[ ?\]) (?!' + START_STAMP_PATTERN + r')'
## Matches completed or skipped todos with only the start timestamp
FINISHED_START_STAMPED_PATTERN = r'(^\s*)(\[)([XS])(\] )(\()(' + DATE_STAMP_PATTERN + r')(\)) '
## Matches completed or skipped todos with no valid timestamp
FINISHED_UNSTAMPED_PATTERN = r'(^\s*)(\[)([XS])(\] )(?!(' + START_STAMP_PATTERN + r'|' + END_STAMP_PATTERN + r'))'
## Matches the prefix of a skipped todo
SKIPPED_PREFIX_GREP = r'(^\s*)(\[S\])( [a-zA-Z1-9\(\)])'
## Matches the prefix of an incomplete todo
INCOMPLETE_PREFIX_GREP = r'(^\s*)(\[ ?\])( [a-zA-Z1-9\(\)])'
## Matches the prefix of a complete todo
COMPLETE_PREFIX_GREP = r'(^\s*)(\[X\])( [a-zA-Z1-9\(\)])'
## matches a start stamp and todo without the prefix
START_STAMP_ONLY_PATTERN = r'(\()(' + DATE_STAMP_PATTERN + r')(\))( )(.*)'
## matches an end stamp and todo without the prefix
START_END_STAMP_ONLY_PATTERN = r'(\()(' + DATE_STAMP_PATTERN + r')( -> )(' + DATE_STAMP_PATTERN + r')(\))( )(.*)'

# Questions & Answers
## Matches a question
ALL_QUESTIONS_GREP = r'(^\s*)(\? )'
UNSTAMPED_QUESTION = r'(^\s*)(\? )(?!' + START_STAMP_PATTERN + r' )'
STAMPED_QUESTION = r'\? ' + START_STAMP_PATTERN + r' '
## Matches an answer
ANSWER_PATTERN = r'(^\s*)(@ )(.*)'
UNSTAMPED_ANSWER = r'(^\s*)(@ )(?!' + START_STAMP_PATTERN + r' )'
STAMPED_ANSWER = r'(@ )(\()' + DATE_STAMP_PATTERN + r'(\)) '

TODAY_GREP = r'"\\\today"'
TODAY_LINE_PATTERN = r'(.*)(\\today)(.*)'

TAG_FILTER = r'( :\w+:)'
TAG_PATTERN = r'( :\w+:)($|(?= ))'

DEFINITION_PATTERN = r"^(\s*)(\{.*\} )(.*)"
DEFINITION_GREP = r"^\(\\s*\)\({.*} \)\(.*\)"

HEADING_PATTERN = r'^(#+)( )(.*)'
DATED_HEADING_PATTERN = r'^(#+)( )(.*)(' + DATE_STAMP_PATTERN + r')'

RECORD_SET_PATTERN = r'^```rec-data$'

LINK_PATTERN = r'\[.*?\]\(.*?\)'
INTERNAL_LINK_PATTERN = r'(\[[^\[]*?\]\()(\/.*?)(\))'

CHARS_TO_ESCAPE = ['(', ')', '{', '}', '+', '|', '?', '`', '=']


def escape_for_grep(input_pattern):
    '''Patterns designed for the python `re` library need to be
    escaped before being used with grep via the command line.

    Note: The uses of backslashes as escape characters for
    parentheses are flipped between the two implementations.
        Python uses the backslash to escape the literal
        parentheses character
        Grep uses the backslask to escape parentheses around
        capture groups
    '''

    clean_pattern = ''

    while input_pattern:
        next_char = input_pattern[0]
        if next_char == '\\':
            next_two_chars = input_pattern[:2]
            if next_two_chars in ['\\(', '\\)', '\\?']:
                clean_pattern += next_two_chars[-1]
                input_pattern = input_pattern[2:]
            elif next_two_chars in ['\\[', '\\]']:
                clean_pattern += next_two_chars
                input_pattern = input_pattern[2:]
            else:
                clean_pattern += '\\\\'
                input_pattern = input_pattern[1:]
        elif next_char in CHARS_TO_ESCAPE:
            clean_pattern += '\\' + next_char
            input_pattern = input_pattern[1:]
        else:
            clean_pattern += next_char
            input_pattern = input_pattern[1:]

    return clean_pattern
