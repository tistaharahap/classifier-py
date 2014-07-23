# -*- coding: utf-8 -*-
from __future__ import division
from store import BasicStore


class Classifier(object):
    pass


class NaiveBayesClassifier(object):

    thresholds = {}
    store = None

    def __init__(self, store, train_set, thresholds={}):
        if not isinstance(store, BasicStore):
            raise TypeError("Store must be an instance of BasicStore")

        self.store = store
        self.thresholds = thresholds

        if not isinstance(train_set, dict):
            raise TypeError("Train Set must be an instance of Dictionary")

        self.store = store
        self.train(train_set=train_set)

    def train(self, train_set):
        if not isinstance(train_set, dict):
            raise TypeError("Train Set should be a dictionary of text: category")

        for (t, c) in train_set.iteritems():
            self.store.train(text=t, cat=c)

    def cat_scores(self, text):
        return self.store.cat_scores(text=text)

    def classify(self, text, default_cat=None, verbose=False):
        max_prob = -1000000000.0
        best = None

        scores = self.cat_scores(text)
        if verbose:
            print scores

        for (cat, prob) in scores.iteritems():
            if prob > max_prob:
                max_prob = prob
                best = cat

        if not best:
            return default_cat

        if self.thresholds and self.thresholds.get(best):
            threshold = self.thresholds[best]
        else:
            threshold = 1.0

        for (cat, prob) in scores.iteritems():
            if cat == best:
                break

            if prob * threshold > max_prob:
                return default_cat

        return best