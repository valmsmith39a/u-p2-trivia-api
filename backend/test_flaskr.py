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
            "category": 3
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
        self.assertTrue(data["total_questions"])

    def test_delete_question(self):
        res = self.client().delete("/questions/18")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 18)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        new_question = data["created"]
        del new_question["id"]
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertDictEqual(new_question, self.new_question)
        self.assertTrue(data["total_questions"])

    def test_search_questions(self):
        res = self.client().post("/questions", json={"searchTerm": "what"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 9)
        self.assertTrue(data["total_questions"])

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_quizzes(self):
        res = self.client().post(
            "/quizzes", json={"previous_questions": [64, 20], "quiz_category": 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], 1)
        self.assertNotEqual(data["question"]["id"], 64)
        self.assertNotEqual(data["question"]["id"], 20)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
