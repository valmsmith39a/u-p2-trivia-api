import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route("/categories")
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        return jsonify(
            {
                "success": True,
                "categories": [category.format() for category in selection],
                "total_categories": len(selection),
            }
        )

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                question_id == Question.id).one_or_none()
            # question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                }
            )
        except:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        search_term = body.get("searchTerm", None)

        try:
            if search_term is not None:
                selection = Question.query.filter(
                    Question.question.ilike("%{}%".format(search_term))
                ).all()
                questions_found = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": questions_found,
                        "total_questions": len(selection),
                    }
                )

            question = body.get("question", None)
            answer = body.get("answer", None)
            difficulty = body.get("difficulty", None)
            category = body.get("category", None)

            new_question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            )

            new_question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": new_question.format(),
                    "questions": current_questions,
                    "total_questions": len(selection),
                }
            )

        except:
            abort(422)

    @app.route("/categories/<int:category_id>/questions")
    def retrieve_question_with_category(category_id):
        selection = Question.query.filter(
            category_id == Question.category).all()
        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in selection],
                "total_questions": len(selection),
            }
        )

    @app.route("/")
    def root():
        return "hello universe"

    return app
