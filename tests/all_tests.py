# -*- coding: utf-8 -*-
from textclassifier.store import MemoryStore, RedisStore
from textclassifier.tokenizer import StopwordsTokenizer
from textclassifier.classifier import NaiveBayesClassifier
import unittest


class TextClassifierTest(unittest.TestCase):

    training_data = {}

    def setUp(self):
        with open('tests/trainingdata.txt', 'r') as f:
            data = [line for line in f]
            for line in data:
                line = line.split('|')
                if line[1:] and line[0]:
                    self.training_data.update({
                        " ".join(line[1:]): line[0]
                    })

class MemoryStoreTest(TextClassifierTest):

    classifier = None

    def setUp(self):
        super(MemoryStoreTest, self).setUp()
        self.classifier = NaiveBayesClassifier(store=MemoryStore(tokenizer=StopwordsTokenizer()),
                                               train_set=self.training_data)

    def test_train_data(self):
        self.assertIsNone(self.classifier.train(self.training_data),
                          msg='The train() method must return None')

    def test_classify(self):
        cls = self.classifier.classify('Van Gaal', verbose=True)
        self.assertIsNotNone(cls, msg="Classifier classify must not return None")


class RedisStoreTest(TextClassifierTest):

    classifier = None

    def setUp(self):
        super(RedisStoreTest, self).setUp()

        self.store = RedisStore(tokenizer=StopwordsTokenizer(), redis_config={
            'host': '127.0.01',
            'port': 6379
        })
        self.store.redis.flushdb()

        self.classifier = NaiveBayesClassifier(store=self.store, train_set=self.training_data)

    def test_redis_conn_is_available(self):
        self.assertIsNotNone(self.store.redis, msg="Redis connection is not available")
        self.assertIs(self.store.redis.ping(), True, msg="Redis connection is not available")

    def test_required_methods_available(self):
        self.assertIs("increment_cat" in dir(self.store), True,
                      msg="The method: increment_cat() is required for a Store")
        self.assertIs("increment_word" in dir(self.store), True,
                      msg="The method: increment_word() is required for a Store")
        self.assertIs("train" in dir(self.store), True,
                      msg="The method: train() is required for a Store")
        self.assertIs("cat_scores" in dir(self.store), True,
                      msg="The method: cat_scores() is required for a Store")

    def test_train_data(self):
        self.store.redis.flushdb()
        self.assertIsNone(self.classifier.train(self.training_data), msg="The train() method must return None")

    def test_classify(self):
        cls = self.classifier.classify('Van Gaal', verbose=True)
        self.assertIsNotNone(cls, msg="Classifier classify must not return None")
