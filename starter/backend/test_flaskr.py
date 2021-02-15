import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = f'postgres://postgres:123@127.0.0.1:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_create_question(self):
        before = Question.query.all()
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        after = Question.query.all()
        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(after) - len(before) == 1)
        self.assertIsNotNone(question)

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))


    def test_delete_question(self):
        question = Question(
            question=self.new_question['question'],
            answer=self.new_question['answer'],
            category=self.new_question['category'],
            difficulty=self.new_question['difficulty']
                            )
        question.insert()
        q_id = question.id
        before = Question.query.all()
        res = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(res.data)
        after = Question.query.all()
        question = Question.query.filter(Question.id == 1).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], q_id)
        self.assertTrue(len(before) - len(after) == 1)
        self.assertEqual(question, None)

    def test_search(self):

        res = self.client().post('/questions',json={'searchTerm': 'egyptians'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)


    def test_play_quiz_game(self):
        """Tests playing quiz game success"""

        # send post request with category and previous questions
        res = self.client().post('/quizzes',json={'prev_questions': [20, 21],
                                            'quiz_category': {'type': 'Science', 'id': '1'}})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()