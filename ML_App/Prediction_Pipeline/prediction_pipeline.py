'''
Script contain all nesseasry transformers and function for unserializing prediction pipeline.
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string
import re
import pickle
import pandas as pd


class DataFrameSelector(BaseEstimator, TransformerMixin):
    ''' 
    Transformer for select given columns from dataframe
    '''
    def __init__(self, attribute_names):
        self.attribute_names = attribute_names
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        return X[self.attribute_names]

    
def title_analyzer(txt):
    '''
    Function performs full text preprocessing for TfidfVectorizer
    '''
    # text standarization (lower case)
    txt_lower = txt.lower()
    
    # removing punctuation using translate method
    punctuation_table = str.maketrans( {key: None for key in string.punctuation} ) 
    txt_lower.translate(punctuation_table)
    
    # tokenization
    token_pattern = re.compile(r'\b\w\w+\b', re.ASCII)
    tokens = re.findall(token_pattern, txt_lower)
    
    # tokens standarization and cleaning
    tokens_stemmed = [PorterStemmer().stem(token) for token in tokens]
    tokens_without_stopwords = [token for token in tokens_stemmed if token not in stopwords.words('english')]
    tokens_without_numbers = [token for token in tokens_without_stopwords if not token.isdigit()]

    return tokens_without_numbers


def make_prediction(request):
    '''
    Function make prediction from serialized data
    '''
    print(request)
    algorithm = request.algorithm
    print(algorithm)
    print(algorithm.file.path)
    with open(algorithm.file.path, 'rb') as f:
        model = pickle.load(f)
    
    # transform JSON to pandas DataFrame
    df = pd.DataFrame(
        { 
          'course_title': [request.course_title],
          'price' : [request.price], 
          'content_duration': [request.content_duration], 
          'num_lectures' : [request.num_lectures],
          'days' : [request.days],
          'level' : [request.level]
        }
    )
    prediction = model.predict(df)
    return prediction