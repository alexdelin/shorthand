EMPTY_RESULTS = {
    'count': 0,
    'items': []
}

ALL_INCOMPLETE_TODOS = {
    'count': 6,
    'items': [
        {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '12',
            'start_date': '2019-05-30',
            'status': 'incomplete',
            'todo_text': 'A follow up item',
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
            'start_date': None,
            'status': 'incomplete',
            'todo_text': 'Indented',
            'tags': ['topic']
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
            'todo_text': 'A follow up item which seemed like a good idea'
        }, {
            'end_date': None,
            'file_path': '/todos.note',
            'line_number': '20',
            'start_date': None,
            'status': 'skipped',
            'tags': [],
            'todo_text': "Something that I could have done but didn't"
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
            'line_number': '38',
            'start_date': '2019-05-30',
            'status': 'complete',
            'tags': [],
            'todo_text': 'A follow up item which seemed like a good idea'
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
            'line_number': '33',
            'start_date': None,
            'status': 'complete',
            'tags': [],
            'todo_text': 'Something that got completed'
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

ALL_ANSWERED_QUESTIONS = {
    'count': 4,
    'items': [
        {
            'answer': 'Granny Smith',
            'file_path': '/section/mixed.note',
            'line_number': '20',
            'question': 'Which kind of apples make the best apple pie :baking:'
        }, {
            'answer': '42',
            'file_path': '/questions.note',
            'line_number': '6',
            'question': 'What is the meaning of life :philosophy:'
        }, {
            'answer': 'blue',
            'file_path': '/questions.note',
            'line_number': '8',
            'question': 'What color is the sky'
        }, {
            'answer': 'To get to the other side',
            'file_path': '/questions.note',
            'line_number': '12',
            'question': 'Why did the chicken cross the road'
        }
    ]
}

ALL_UNANSWERED_QUESTIONS = {
    'count': 3,
    'items': [
        {
            'answer': None,
            'file_path': '/questions.note',
            'line_number': '16',
            'question': 'Is the world eternal'
        }, {
            'answer': None,
            'file_path': '/questions.note',
            'line_number': '17',
            'question': 'What is the best kind of cereal :food:'
        }, {
            'answer': None,
            'file_path': '/questions.note',
            'line_number': '21',
            'question': 'How do you write software with no bugs :software:'
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
