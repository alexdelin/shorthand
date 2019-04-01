from subprocess import Popen, PIPE
import re
from collections import OrderedDict
import json
import codecs

from nltk import bigrams, trigrams
from nltk.tokenize import sent_tokenize, WhitespaceTokenizer, \
        LineTokenizer


FORBIDDEN_CHARS = [
    '[', ']', '(', ')', '\\', '/', '.', ',',
    '?', '!', '@', '#', '$', '`', "'", '"',
    '-', '_', '=', '+', '*']


def update_ngram_database(notes_directory, ngram_db_dir):

    line_tokenizer = LineTokenizer(blanklines='discard')
    word_tokenizer = WhitespaceTokenizer()

    grep_command = 'find {} | grep ".note$"'.format(notes_directory)

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    all_notes_files = output.split('\n')
    # print(all_notes_files)

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

        with codecs.open(note_file, mode="r", encoding="utf-8") as note_file_object:
            note_file_content = note_file_object.read()

        note_file_content = note_file_content.lower()

        lines = line_tokenizer.tokenize(note_file_content)
        for line in lines:

            sentences = sent_tokenize(line)
            for sentence in sentences:

                sentence_safe_split = []

                all_words = word_tokenizer.tokenize(sentence)
                for word in all_words:

                    first_and_last = [word[0], word[-1]]
                    for forbidden_char in FORBIDDEN_CHARS:
                        if forbidden_char in first_and_last:
                            word = word.replace(forbidden_char, '')

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

        # Only process the first file for now
        # break

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
            if not isinstance(single_token, basestring):
                single_token = ' '.join(single_token)
            if not weighted_tokens.get(single_token):
                weighted_tokens[single_token] = 1
            else:
                weighted_tokens[single_token] = weighted_tokens[single_token] + 1

        tokens[token_type] = OrderedDict(sorted(
            weighted_tokens.iteritems(),
            key=lambda t: t[1],
            reverse=True))

    # Write Ngram Databases to Disk
    unigrams_file_path = ngram_db_dir + '/unigrams.txt'
    with open(unigrams_file_path, 'w') as unigrams_file_object:
        json.dump(tokens['unigrams'], unigrams_file_object)
    bigrams_file_path = ngram_db_dir + '/bigrams.txt'
    with open(bigrams_file_path, 'w') as bigrams_file_object:
        json.dump(tokens['bigrams'], bigrams_file_object)
    trigrams_file_path = ngram_db_dir + '/trigrams.txt'
    with open(trigrams_file_path, 'w') as trigrams_file_object:
        json.dump(tokens['trigrams'], trigrams_file_object)


update_ngram_database('/Users/alexdelin/Desktop/Notes', '/Users/alexdelin/Desktop/ngram_db')
