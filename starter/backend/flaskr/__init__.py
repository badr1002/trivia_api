import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.expression import func
from werkzeug.exceptions import HTTPException
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.route
    def after_request(res):
        res.handlers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
        res.handlers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
        return res

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        categories_list = {}
        for categ in categories:
            categories_list[categ.id] = categ.type

        if (len(categories_list) == 0):
            abort(404)
        else:
            return jsonify({'categories': categories_list})

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories = Category.query.all()
        questions = [question.format() for question in Question.query.all()]

        page = int(request.args.get('page', '0'))
        up_lim = page * 10
        low_lim = up_lim - 10

        categories_list = {}
        for categ in categories:
            categories_list[categ.id] = categ.type

        return jsonify({
            'questions': questions[low_lim:up_lim] if page else questions,
            'all_questions': len(questions),
            'categories': categories
        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question:
            question.delete()
            return jsonify({'deleted': True})
        else:
            return abort(404)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.route('/questions', methods=['POST'])
    def post_question():
        question = request.json.get('question')
        answer = request.json.get('answer')
        category = request.json.get('category')
        difficulty = request.json.get('difficulty')

        if (question and answer and category and difficulty):
            new_question = Question(question, answer, category, difficulty)
            new_question.insert()
            return jsonify({'question': new_question.format()})
        else:
            return abort(400)

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    @app.route('/search', methods=['POST'])
    def search():
        search_term = request.json.get('searchTerm', '')
        questions = [question.format() for question in Question.query.all() if
                     question.question.ilike('%' + search_term + '%')]
        return jsonify({
            'questions': questions,
            'total_questions': len(questions)
        })

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id)
        if category_id:
            get_questions = [q.format() for q in questions]
            return jsonify({
                'questions': get_questions,
                'total_questions': len(get_questions),
                'current_category': category_id
            })
        else:
            return abort(400)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        prev_questions = request.json.get('previous_questions')
        quiz_category = request.json.get('quiz_category')

        if quiz_category:
            category_id = int(quiz_category.get('id'))
            questions = Question.query.filter(
                Question.category == category_id,
                Question.id.in_(prev_questions)) if category_id else Question.query.filter(
                ~Question.id.in_(prev_questions))

            question = questions.order_by(func.random()).first()
            return jsonify({'question': question.format()})
        else:
            return abort(400)

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request!'
        }), 400

    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        return jsonify({
            'success': False,
            'error': 402,
            'message': 'Payment Required!'
        }), 402

    @app.errorhandler(HTTPException)
    def http_exception_handler(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found!'
        }), 404

    return app
