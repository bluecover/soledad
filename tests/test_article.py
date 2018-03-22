# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.article.article import Article, STATUS
from core.models.article.viewpoint import ViewPoint
from core.models.article.question import Question

from core.models.article.consts import (VIEWPOINT, QUESTION)


class ViewPointTest(BaseTestCase):
    def test_add_article(self):
        a = ViewPoint.add()
        self.assertTrue(a)
        a.title = 'title'
        a.content = 'content'
        a.author = 'author'
        self.assertTrue(a)
        self.assertFalse(a.is_published())
        aid = a.id
        a.publish()
        a = ViewPoint.get(aid)
        self.assertTrue(a.is_published())

    def test_get_article(self):
        a = ViewPoint.add()
        self.assertTrue(a)
        a.title = 'title'
        a.content = 'content'
        a.author = 'author'
        aid = a.id
        a = ViewPoint.get(aid)
        self.assertTrue(a)
        self.assertEqual(a.title, 'title')
        self.assertEqual(a.content, 'content')
        self.assertEqual(a.author, 'author')

    def test_delete_article(self):
        a = ViewPoint.add()
        self.assertTrue(a)
        self.assertFalse(a.is_deleted())
        aid = a.id
        a.delete()
        a = ViewPoint.get(aid)
        self.assertTrue(a.is_deleted())

    def test_get_by_type_and_categry(self):
        article = ViewPoint.add()
        articles = Article.get_articles_by_type_and_category(
            VIEWPOINT.TYPE, 0, STATUS.NONE)
        ids = [a.id for a in articles]
        self.assertTrue(article.id in ids)

        article = ViewPoint.add(category=1)
        articles = Article.get_articles_by_type_and_category(
            VIEWPOINT.TYPE, 1, STATUS.NONE)
        ids = [a.id for a in articles]
        self.assertTrue(article.id in ids)

    def test_get_all(self):
        articles = ViewPoint.get_all()
        ids = [a.id for a in articles]
        article = ViewPoint.add()
        article.publish()
        self.assertFalse(article.id in ids)
        articles = ViewPoint.get_all()
        ids = [a.id for a in articles]
        self.assertTrue(article.id in ids)


class QuestionTest(BaseTestCase):
    def test_add_article(self):
        a = Question.add()
        self.assertTrue(a)
        a.ask = 'some thing?'
        a.answer = 'yes it is!'
        self.assertTrue(a)
        self.assertFalse(a.is_published())
        aid = a.id
        a.publish()
        a = Question.get(aid)
        self.assertTrue(a.is_published())

    def test_get_article(self):
        a = Question.add()
        self.assertTrue(a)
        a.ask = 'some thing?'
        a.answer = 'yes it is!'
        aid = a.id
        a = Question.get(aid)
        self.assertTrue(a)
        self.assertEqual(a.ask, 'some thing?')
        self.assertEqual(a.answer, 'yes it is!')

    def test_delete_article(self):
        a = Question.add()
        self.assertTrue(a)
        self.assertFalse(a.is_deleted())
        aid = a.id
        a.delete()
        a = Question.get(aid)
        self.assertTrue(a.is_deleted())

    def test_get_by_type_and_categry(self):
        article = Question.add()
        articles = Article.get_articles_by_type_and_category(
            QUESTION.TYPE, 0, STATUS.NONE)
        ids = [a.id for a in articles]
        self.assertTrue(article.id in ids)

        article = Question.add(category=1)
        articles = Article.get_articles_by_type_and_category(
            QUESTION.TYPE, 1, STATUS.NONE)
        ids = [a.id for a in articles]
        self.assertTrue(article.id in ids)

    def test_get_all(self):
        articles = Question.get_all()
        ids = [a.id for a in articles]
        article = Question.add()
        article.publish()
        self.assertFalse(article.id in ids)
        articles = Question.get_all()
        ids = [a.id for a in articles]
        self.assertTrue(article.id in ids)
