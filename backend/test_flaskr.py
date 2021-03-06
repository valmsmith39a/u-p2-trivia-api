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
        self.database_name = "trivia_test"
        self.database_path = os.getenv("SQL_URI")
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Who's on first?",
            "answer": "John",
            "difficulty": 5,
            "category": 3,
        }

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

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_categories"])

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        new_question = data["created"]
        self.new_question["id"] = new_question["id"]
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertDictEqual(new_question, self.new_question)
        self.assertTrue(data["total_questions"])

    def test_create_question_failure(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_question(self):
        # select a question id that exists
        res = self.client().get("/questions")
        data = json.loads(res.data)
        delete_id = data["questions"][0]["id"]

        res = self.client().delete("/questions" + "/" + str(delete_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], delete_id)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_delete_question_failure(self):
        res = self.client().delete("/questions/10000")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        res = self.client().post(
            "/questions",
            json={"searchTerm": "a new question"},
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_search_questions_failure(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_get_questions_by_category_failure(self):
        res = self.client().get("/categories/9999/questions")
        data = json.loads(res.data)

        self.assertEqual(data["error"], 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_quizzes(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [64, 20],
                "quiz_category": {"type": "Art", "id": 2},
            },
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], 2)
        self.assertNotEqual(data["question"]["id"], 64)
        self.assertNotEqual(data["question"]["id"], 20)

    def test_quizzes_failure(self):
        res = self.client().post("/quizzes")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_404_if_question_does_not_exist(self):
        res = self.client().get("/questions/no-resource-here")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_422_unprocessable(self):
        res = self.client().post(
            "/questions",
            content_type="multipart/form-data",
            data={"question": "test", "answer": "test ans", "category": 1},
        )
        data = json.loads(res.data)
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_400_bad_request(self):
        # trigger error with mispelling of "previous_questions"
        res = self.client().post(
            "/quizzes",
            json={
                "previous_question": [4],
                "quiz_category": {"type": "Geography", "id": 1},
            },
        )
        data = json.loads(res.data)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
