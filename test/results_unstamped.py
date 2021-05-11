EMPTY_RESULTS = {
    'count': 0,
    'items': []
}

ALL_INCOMPLETE_TODOS = {
    'count': 7,
    'items': [
        {
            'end_date': None,
            'file_path': '/bugs.note',
            'line_number': '7',
            'start_date': None,
            'status': 'incomplete',
            'todo_text': 'Read through https://url-that-looks-like-a-tag.com/foo:bar:baz',
            'tags': []
        }, {
            'end_date': None,
            'file_path': '/section/mixed.note',
            'line_number': '23',
            'start_date': None,
            'status': 'incomplete',
            'tags': ['food', 'baking'],
            'todo_text': 'Test different cooking times for this recipe',
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '6',
            'start_date': None,
            'status': 'incomplete',
            'todo_text': 'Something to do',
            'tags': []
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '7',
            'start_date': None,
            'status': 'incomplete',
            'todo_text': 'With a space in the brackets already',
            'tags': []
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '8',
            'start_date': '2120-06-01',
            'status': 'incomplete',
            'todo_text': 'Indented todo which won\'t start for a **long** time',
            'tags': ['future']
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '12',
            'start_date': '2019-05-30',
            'status': 'incomplete',
            'todo_text': 'A follow up item which is still open',
            'tags': []
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '15',
            'start_date': None,
            'status': 'incomplete',
            'todo_text': 'A more specific todo',
            'tags': ['nested']
        }
    ]
}

ALL_SKIPPED_TODOS = {
    'count': 4,
    'items': [
        {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '20',
            'start_date': None,
            'status': 'skipped',
            'tags': [],
            'todo_text': "Something that I could have done but didn't"
        }, {
            'end_date': '2019-06-03',
            'file_path': '/todos.note',
            'line_number': '21',
            'start_date': '2019-05-30',
            'status': 'skipped',
            'tags': ['pointless'],
            'todo_text': 'Indented'
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '25',
            'start_date': '2019-05-30',
            'status': 'skipped',
            'tags': [],
            'todo_text': 'A follow up item which seemed like a good idea but wasn\'t'
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '28',
            'start_date': None,
            'status': 'skipped',
            'tags': ['nested'],
            'todo_text': 'A more specific todo'
        }
    ]
}

ALL_COMPLETE_TODOS = {
    'count': 4,
    'items': [
        {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '33',
            'start_date': None,
            'status': 'complete',
            'tags': [],
            'todo_text': 'Something that got completed'
        }, {
            'end_date': '2019-06-04',
            'file_path': '/todos.note',
            'line_number': '34',
            'start_date': '2019-05-27',
            'status': 'complete',
            'tags': ['topic'],
            'todo_text': 'Indented and with both start and end stamped'
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '38',
            'start_date': '2019-05-30',
            'status': 'complete',
            'tags': [],
            'todo_text': 'A follow up item which seemed like a good idea and is now finished'
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '41',
            'start_date': None,
            'status': 'complete',
            'tags': ['nested'],
            'todo_text': 'A more specific todo'
        }
    ]
}

ALL_QUESTIONS = {
    'count': 7,
    'items': [
        {
            'answer': 'Granny Smith',
            'file_path': '/section/mixed.note',
            'line_number': '20',
            'question': 'Which kind of apples make the best apple pie',
            'tags': ['baking'],
            'question_date': None,
            'answer_date': None
        }, {
            'answer': '42',
            'file_path': '/questions.note',
            'line_number': '6',
            'question': 'What is the meaning of life',
            'tags': ['philosophy'],
            'question_date': None,
            'answer_date': None
        }, {
            'answer': 'blue',
            'file_path': '/questions.note',
            'line_number': '8',
            'question': 'What color is the sky',
            'tags': [],
            'question_date': None,
            'answer_date': None
        }, {
            'answer': 'To get to the other side',
            'file_path': '/questions.note',
            'line_number': '12',
            'question': 'Why did the chicken cross the road',
            'tags': [],
            'question_date': None,
            'answer_date': None
        }, {
            'answer': None,
            'file_path': '/questions.note',
            'line_number': '16',
            'question': 'Is the world eternal',
            'tags': [],
            'question_date': None,
            'answer_date': None
        }, {
            'answer': None,
            'file_path': '/questions.note',
            'line_number': '17',
            'question': 'What is the best kind of cereal',
            'tags': ['food'],
            'question_date': None,
            'answer_date': None
        }, {
            'answer': None,
            'file_path': '/questions.note',
            'line_number': '21',
            'question': 'How do you write software with no bugs',
            'tags': ['software'],
            'question_date': None,
            'answer_date': None
        }
    ]
}

SEARCH_RESULTS_FOOD = {
    'count': 4,
    'items': [
        {
            'file_path': '/definitions.note',
            'line_number': '7',
            'match_content': r'{food} Something that you eat when you are hungry'
        }, {
            'file_path': '/section/mixed.note',
            'line_number': '23',
            'match_content': '[] Test different cooking times for this recipe :food: :baking:'
        }, {
            'file_path': '/questions.note',
            'line_number': '17',
            'match_content': '? What is the best kind of cereal :food:'
        }, {
            'file_path': '/questions.note',
            'line_number': '19',
            'match_content': 'Food is an essential part of a balanced diet'
        }
    ]
}

SEARCH_RESULTS_FOOD_SENSITIVE = {
    'count': 1,
    'items': [
        {
            'file_path': '/questions.note',
            'line_number': '19',
            'match_content': 'Food is an essential part of a balanced diet'
        }
    ]
}

SEARCH_RESULTS_BALANCED_DIET = {
    'count': 1,
    'items': [
        {
            'file_path': '/questions.note',
            'line_number': '19',
            'match_content': 'Food is an essential part of a balanced diet'
        }
    ]
}

ALL_DEFINITIONS = [
    {'definition': 'A formal meaning attached to a specific term',
     'display_path': 'definitions.note',
     'file_path': '/definitions.note',
     'line_number': '5',
     'term': 'definition'},
    {'definition': 'A tool you can use to make your life easier and better',
     'display_path': 'definitions.note',
     'file_path': '/definitions.note',
     'line_number': '6',
     'term': 'software'},
    {'definition': 'Something that you eat when you are hungry',
     'display_path': 'definitions.note',
     'file_path': '/definitions.note',
     'line_number': '7',
     'term': 'food'},
    {'definition': 'The flaky part at the bottom of the pie :baking:',
     'display_path': 'section → mixed.note',
     'file_path': '/section/mixed.note',
     'line_number': '9',
     'term': 'crust'}
]

ALL_LOCATIONS = [
    {'latitude': '40.757898',
     'longitude': '-73.985502',
     'name': 'Times Square',
     'file_path': '/locations.note',
     'display_path': 'locations.note',
     'line_number': '4'},
    {'latitude': '29.978938',
     'longitude': '31.134116',
     'name': 'The Great Pyramid',
     'file_path': '/locations.note',
     'display_path': 'locations.note',
     'line_number': '5'},
    {'latitude': '36.193521',
     'longitude': '-112.048667',
     'name': 'The Grand Canyon',
     'file_path': '/locations.note',
     'display_path': 'locations.note',
     'line_number': '6'},
    {'latitude': '48.858212',
     'longitude': '2.294513',
     'name': '',
     'file_path': '/locations.note',
     'display_path': 'locations.note',
     'line_number': '7'}
]

ALL_FILES = [
    '/questions.note',
    '/rec.note',
    '/locations.note',
    '/todos.note',
    '/section/mixed.note',
    '/definitions.note',
    '/bugs.note'
]

TOC = {
    'dirs': [
        {
            'dirs': [],
            'files': ['mixed.note'],
            'path': '/section',
            'text': 'section'
        }
    ],
    'files': [
        'bugs.note',
        'definitions.note',
        'todos.note',
        'locations.note',
        'rec.note',
        'questions.note'
    ],
    'path': '',
    'text': '',
}

CALENDAR = {
    '2019': {
        '05': {
            '30': [
                {
                    'date': '2019-05-30',
                    'element_id': '',
                    'event': 'A follow up item which is still open',
                    'file_path': '/todos.note',
                    'line_number': '12',
                    'type': 'incomplete_todo'
                }
            ]
        },
        '06': {
            '03': [
                {
                    'date': '2019-06-03',
                    'element_id': '',
                    'event': 'Indented',
                    'file_path': '/todos.note',
                    'line_number': '21',
                    'type': 'skipped_todo'
                }
            ],
            '04': [
                {
                    'date': '2019-06-04',
                    'element_id': '',
                    'event': 'Indented and with both start and end stamped',
                    'file_path': '/todos.note',
                    'line_number': '34',
                    'type': 'completed_todo'
                }
            ]
        }
    }
}

ALL_LINKS = [
    {
        'line_number': '26',
        'source': '/section/mixed.note',
        'target': '/todos.note',
        'text': 'todos'
    }, {
        'line_number': '26',
        'source': '/section/mixed.note',
        'target': '/questions.note',
        'text': 'questions'
    }, {
        'line_number': '26',
        'source': '/section/mixed.note',
        'target': '/definitions.note',
        'text': 'definitions'
    }, {
        'line_number': '30',
        'source': '/section/mixed.note',
        'target': '/does/not/exist.note',
        'text': 'broken'
    }, {
        'line_number': '30',
        'source': '/section/mixed.note',
        'target': '/lokations.note',
        'text': 'typos'
    }, {
        'line_number': '2',
        'source': '/todos.note',
        'target': '/section/mixed.note',
        'text': 'the mixed example'
    }, {
        'line_number': '57',
        'source': '/todos.note',
        'target': '/bugs.note',
        'text': 'bugs document'
    }, {
        'line_number': '23',
        'source': '/questions.note',
        'target': '/section/mixed.note',
        'text': 'mixed example'
    }, {
        'line_number': '28',
        'source': '/section/mixed.note',
        'target': 'https://nytimes.com',
        'text': 'NY Times'
    }, {
        'line_number': '32',
        'source': '/section/mixed.note',
        'target': '/todos.note',
        'text': 'relative paths'
    }, {
        'line_number': '13',
        'source': '/bugs.note',
        'target': '/todos.note',
        'text': 'todos'
    }, {
        'line_number': '13',
        'source': '/bugs.note',
        'target': '/locations.note',
        'text': 'locations'
    }, {
        'line_number': '13',
        'target': '/README.md',
        'text': 'outside',
        'source': '/bugs.note'
    }
]

INVALID_LINKS = [
    {
        'line_number': '30',
        'path': '/section/mixed.note',
        'link_target': '/does/not/exist.note',
        'link_text': 'broken'
    }, {
        'line_number': '30',
        'link_target': '/lokations.note',
        'link_text': 'typos',
        'path': '/section/mixed.note'
    }, {
        'line_number': '13',
        'link_target': '/README.md',
        'link_text': 'outside',
        'path': '/bugs.note'
    },
]
