from subprocess import Popen, PIPE
from collections import OrderedDict
import json
import codecs
import logging

from nltk import bigrams, trigrams
from nltk.tokenize import sent_tokenize, WhitespaceTokenizer, \
        LineTokenizer


FORBIDDEN_CHARS = [
    '[', ']', '(', ')', '\\', '/', '.', ',',
    '?', '!', '@', '#', '$', '`', "'", '"',
    '-', '_', '=', '+', '*', '%', ':', '{',
    '}']


log = logging.getLogger(__name__)


def _get_typeahead_suggestions(ngram_db_dir, query_string, limit=10):
    '''Get typeahead suggestions for the current active query.
    This can be a large query that we only want to provide
    suggestions for extending the last word or term of
    '''

    num_quotes = query_string.count('"')
    if num_quotes % 2 != 0:
        # Provide suggestions for a multi-word term enclosed in quotes

        # we have unclosed quotes
        split_terms = query_string.split('"')
        current_term = split_terms[-1]
        previous_query = '"'.join(split_terms[:-1])

        # Can only provide suggestions up to trigrams
        num_words_in_term = len(current_term.split(' '))
        if num_words_in_term > 3:
            return []
        elif num_words_in_term == 3:
            matches = search_ngram_db(ngram_db_dir + '/trigrams.txt',
                                      current_term, limit)
            return [previous_query + '"' + match + '"' for match in matches]
        elif num_words_in_term == 2:
            matches = search_ngram_db(ngram_db_dir + '/bigrams.txt',
                                      current_term, limit)
            return [previous_query + '"' + match + '"' for match in matches]
        elif num_words_in_term == 1:
            matches = search_ngram_db(ngram_db_dir + '/unigrams.txt',
                                      current_term, limit)
            return [previous_query + '"' + match + '"' for match in matches]

    else:
        # Only provide suggestions for the current word
        # This can be improved eventually
        split_terms = query_string.split(' ')
        current_term = split_terms[-1]
        previous_query = ' '.join(split_terms[:-1])

        matches = search_ngram_db(ngram_db_dir + '/unigrams.txt',
                                  current_term, limit)
        clean = []
        for match in matches:
            if previous_query:
                clean.append(previous_query + ' ' + match)
            else:
                clean.append(match)
        return clean


def search_ngram_db(database_file, search_string, limit):
    '''Search an ngram DB file for terms starting with a given string
    As always, do the search with grep
    '''

    grep_pattern = '"^{raw_pattern}"'.format(raw_pattern=search_string)

    grep_command = 'grep {pattern} {file} | head -n {limit}'.format(
                        pattern=grep_pattern,
                        file=database_file,
                        limit=limit)

    proc = Popen(grep_command,
                 stdout=PIPE, stderr=PIPE,
                 shell=True)

    output, err = proc.communicate()
    matching_terms = output.decode().split('\n')
    matching_terms = [term for term in matching_terms if len(term)]
    return matching_terms


def _update_ngram_database(notes_directory, ngram_db_dir):

    line_tokenizer = LineTokenizer(blanklines='discard')
    word_tokenizer = WhitespaceTokenizer()

    grep_command = 'find {} | grep ".note$"'.format(notes_directory)

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    all_notes_files = output.decode().split('\n')

    '''
    Create master list of all raw tokens. Will look like:
        tokens = {
            'unigrams': ['all', 'unigrams'],
            'bigrams': [('all', 'bigrams')],
            'trigrams': [('all', 'the', 'trigrams')]
        }
    '''

    tokens = {
        'unigrams': [],
        'bigrams': [],
        'trigrams': []
    }

    for note_file in all_notes_files:

        if not note_file:
            continue

        with codecs.open(note_file, mode="r", encoding="utf-8") \
                as note_file_object:
            note_file_content = note_file_object.read()

        note_file_content = note_file_content.lower()

        lines = line_tokenizer.tokenize(note_file_content)
        for line in lines:

            sentences = sent_tokenize(line)
            for sentence in sentences:

                sentence_safe_split = []

                all_words = word_tokenizer.tokenize(sentence)
                for word in all_words:

                    # Skip any word with a forbidden character
                    if any([char in word for char in FORBIDDEN_CHARS]):
                        continue

                    has_letters = False
                    for char in word:
                        if char.isalpha():
                            has_letters = True
                            break

                    if word and has_letters:
                        sentence_safe_split.append(word)

                tokens['unigrams'].extend(sentence_safe_split)
                tokens['bigrams'].extend(bigrams(sentence_safe_split))
                tokens['trigrams'].extend(trigrams(sentence_safe_split))

    '''
    Squash the list of tokens into a dict that tracks
    the number of occurences of each token. Will look like:
    tokens = {
        'unigrams': {
            'foo': 17,
            'bar': 42,
            ...
        },
        ...
    }
    '''

    for token_type in tokens.keys():

        all_tokens_of_type = tokens[token_type]
        weighted_tokens = {}

        for single_token in all_tokens_of_type:
            if not isinstance(single_token, str):
                single_token = ' '.join(single_token)
            if not weighted_tokens.get(single_token):
                weighted_tokens[single_token] = 1
            else:
                weighted_tokens[single_token] = weighted_tokens[single_token]+1

        tokens[token_type] = OrderedDict(sorted(
            weighted_tokens.items(),
            key=lambda t: t[1],
            reverse=True))

    # Write Unigrams to Disk
    unigrams_json_file_path = ngram_db_dir + '/unigrams.json'
    unigrams_text_file_path = ngram_db_dir + '/unigrams.txt'
    with open(unigrams_json_file_path, 'w') as unigrams_json_file_object:
        json.dump(tokens['unigrams'], unigrams_json_file_object)
    with codecs.open(unigrams_text_file_path, mode="w", encoding="utf-8") \
            as unigrams_text_file_object:
        for unigram, frequency in tokens['unigrams'].items():
            unigrams_text_file_object.write(unigram + '\n')

    # Write Bigrams to Disk
    bigrams_json_file_path = ngram_db_dir + '/bigrams.json'
    bigrams_text_file_path = ngram_db_dir + '/bigrams.txt'
    with open(bigrams_json_file_path, 'w') as bigrams_json_file_object:
        json.dump(tokens['bigrams'], bigrams_json_file_object)
    with codecs.open(bigrams_text_file_path, mode="w", encoding="utf-8") \
            as bigrams_text_file_object:
        for bigram, frequency in tokens['bigrams'].items():
            bigrams_text_file_object.write(bigram + '\n')

    # Write Trigrams to Disk
    trigrams_json_file_path = ngram_db_dir + '/trigrams.json'
    trigrams_text_file_path = ngram_db_dir + '/trigrams.txt'
    with open(trigrams_json_file_path, 'w') as trigrams_json_file_object:
        json.dump(tokens['trigrams'], trigrams_json_file_object)
    with codecs.open(trigrams_text_file_path, mode="w", encoding="utf-8") \
            as trigrams_text_file_object:
        for trigram, frequency in tokens['trigrams'].items():
            trigrams_text_file_object.write(trigram + '\n')
