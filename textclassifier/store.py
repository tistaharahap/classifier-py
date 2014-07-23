from __future__ import division
from textblob import TextBlob
from math import log
import redis


class BasicStore(object):

    blob = None
    features = None
    tokenizer = None

    def __init__(self, tokenizer, features=None):
        self.blob = None
        self.features = features
        self.tokenizer = tokenizer

    def increment_word(self, word, cat):
        pass

    def increment_cat(self, cat):
        pass

    def train(self, text, cat):
        if self.blob is None:
            self.blob = TextBlob(text, tokenizer=self.tokenizer)
        else:
            self.blob += TextBlob(text=" %s" % text, tokenizer=self.tokenizer)

        for word in self.blob.tokenize():
            self.increment_word(word, cat)
            self.increment_cat(cat)

    def cat_scores(self, text):
        pass


class MemoryStore(BasicStore):

    db = {
        'categories': {},
        'wordcounts': {}
    }

    def __init__(self, tokenizer, features=None):
        self.tokenizer = tokenizer

        super(MemoryStore, self).__init__(features=features, tokenizer=tokenizer)

    def increment_word(self, word, cat):
        try:
            self.db['categories'][cat][word] += 1
        except KeyError:
            if not self.db['categories'].get(cat):
                self.db['categories'][cat] = {}

            self.db['categories'][cat][word] = 1

    def increment_cat(self, cat):
        try:
            self.db['wordcounts'][cat] += 1
        except KeyError:
            self.db['wordcounts'][cat] = 1

    def cat_scores(self, text):
        blob = TextBlob(text=text, tokenizer=self.tokenizer)
        tokens = blob.tokenize()

        scores = {}
        total_cats = len(self.db['categories'].items())

        prob_cat = log(1 / total_cats)

        for (cat, words) in self.db['categories'].iteritems():
            scores[cat] = prob_cat
            probs = [self.db['categories'][cat].get(token) for token in tokens]
            probs = [log(item / self.db['wordcounts'][cat]) for item in probs if item is not None]

            for prob in probs:
                scores[cat] += abs(prob)

        return scores


class RedisStore(BasicStore):

    redis_config = {
        'host': '127.0.0.1',
        'port': 6379
    }

    namespaces = {
        'prefix': 'classify',
        'categories': '',
        'category-names': '',
        'wordcounts': '',
    }

    redis = None

    def __init__(self, tokenizer, redis_config, flush_db=False):
        self.tokenizer = tokenizer

        if redis_config is not None and isinstance(redis_config, dict):
            if redis_config.get('host') is None:
                raise ValueError("Redis config must specify host")

            if redis_config.get('port') is None:
                raise ValueError("Redis config must specify port")

            self.redis_config['host'] = redis_config['host']
            self.redis_config['port'] = redis_config['port']

            self.namespaces['categories'] = '%s-categories' % self.namespaces['prefix']
            self.namespaces['category-names'] = '%s-category-names' % self.namespaces['prefix']
            self.namespaces['wordcounts'] = '%s-wordcounts' % self.namespaces['prefix']

            self.redis = redis.StrictRedis(host=self.redis_config['host'],
                                           port=self.redis_config['port'])

            if flush_db:
                self.redis.flushdb()

        super(RedisStore, self).__init__(tokenizer=tokenizer)

    def increment_cat(self, cat):
        self.redis.hincrby(self.namespaces['wordcounts'], '%s-%s' %
                                                          (self.namespaces['prefix'], cat), 1)

    def increment_word(self, word, cat):
        self.redis.hincrby(self.namespaces['categories'], '%s-%s-%s' %
                                                          (self.namespaces['prefix'], cat, word), 1)

        self.redis.hincrby(self.namespaces['category-names'], cat, 1)

    def cat_scores(self, text):
        blob = TextBlob(text=text, tokenizer=self.tokenizer)
        tokens = blob.tokenize()

        scores = {}
        total_cats = len(self.redis.hkeys(self.namespaces['category-names']))

        prob_cat = log(1 / total_cats)

        for cat in self.redis.hkeys(self.namespaces['category-names']):
            scores[cat] = prob_cat
            probs = [self.redis.hget(self.namespaces['categories'],
                                     '%s-%s-%s' % (self.namespaces['prefix'], cat, token))
                     for token in tokens]

            probs = [log(int(item) / int(self.redis.hget(self.namespaces['wordcounts'],
                                                '%s-%s' % (self.namespaces['prefix'], cat))))
                     for item in probs if item is not None]

            for prob in probs:
                scores[cat] += abs(prob)

        return scores
