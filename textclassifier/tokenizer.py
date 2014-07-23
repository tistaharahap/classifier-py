from text.tokenizers import WordTokenizer
from nltk.tokenize import RegexpTokenizer
import re
import nltk


class StopwordsTokenizer(WordTokenizer):

    stopwords = []
    try:
        stopwords.extend(nltk.corpus.stopwords.words('indonesian'))
        stopwords.extend(nltk.corpus.stopwords.words('english'))
    except IOError:
        pass
    except LookupError:
        pass

    regx = [
        '(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?',
        '(\@.*)?',
        '(\'.*)?'
    ]

    def __init__(self, _stopwords=None):
        if _stopwords is not None and not isinstance(_stopwords, list):
            raise TypeError("Stopwords must be a List")

        self.stopwords.append(_stopwords)
        super(StopwordsTokenizer, self).__init__()

    def tokenize(self, text, include_punc=True):
        tk = RegexpTokenizer("[\w']+", flags=re.UNICODE)
        for pattern in self.regx:
            text = re.sub(pattern=pattern, repl='', string=text)
        tokens = tk.tokenize(text=text)
        return [token for token in tokens if token not in self.stopwords]
