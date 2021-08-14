# AUTOGENERATED! DO NOT EDIT! File to edit: 04_pickle.ipynb (unless otherwise specified).

__all__ = ['label', 'cos_sim', 'create_dict_whole_book', 'create_label_whole_book', 'create_label',
           'get_embed_method_and_name']

# Cell
import os
import numpy as np
import pickle
import string
from numpy import dot
from numpy.linalg import norm

# Cell
def label(arg):
    """
    Returns the full name of the model based on the abbreviation
    """
    switcher = {
        'dcltr_base': "DeCLUTR Base",
        'dcltr_sm': "DeCLUTR Small",
        'distil': "DistilBERT",
        'if_FT': "InferSent FastText",
        'if_glove': "InferSent GloVe",
        'roberta': "RoBERTa",
        'use': "USE",
        'new_lex': 'Lexical Vectors',
        'old_lex': 'Lexical Weights',
        'lexical_wt': 'Lexical Weights',
        'lex_vect': 'Lexical Vectors',
        'lex_vect_corr_ts': 'Lexical Vectors (Corr)'
    }
    return switcher.get(arg)

# Cell
def cos_sim(a, b):
    """
    Returns the cosine similarity between 2 vectors.
    """
    return dot(a, b)/(norm(a)*norm(b))

# Cell
def create_dict_whole_book(embedding_path, k):
    mdict = {}
    parent_dir = os.path.basename(os.path.dirname(embedding_path))
    sub_dict = {}
    for fx in os.listdir(embedding_path):
        if fx.endswith('.npy'):
            name = fx[:-4]
            embed = np.load(embedding_path+fx)
            book_name, method = get_embed_method_and_name(name)
            ts = successive_similarities(embed, k)

            name = create_label_whole_book(method, parent_dir)

            sub_dict[name] = ts

        if fx.endswith('_vect.npy'):
            name = fx[:-4]
            embed = np.load(embedding_path+fx)
            book_name, method = get_embed_method_and_name(name)
            # ts = successive_similarities(embed, k)

            name = create_label_whole_book(method, parent_dir)

            sub_dict[name] = embed


        if fx.endswith('_wt.npy'):
            name = fx[:-4]
            embed = np.load(embedding_path+fx)
            book_name, method = get_embed_method_and_name(name)
            # ts = successive_similarities(embed, k)

            name = create_label_whole_book(method, parent_dir)

            sub_dict[name] = embed

        if fx.endswith('_corr_ts.npy'):
            name = fx[:-4]
            embed = np.load(embedding_path+fx)
            book_name, method = get_embed_method_and_name(name)
            # ts = successive_similarities(embed, k)

            name = create_label_whole_book(method, parent_dir)
            print('Found Lex Corr', name)
            sub_dict[name] = embed


    mdict[0] = sub_dict
    pickle.dump(mdict, open(parent_dir +'_whole.pkl', 'wb'))

# Cell
def create_label_whole_book(method, parent_dir):
    # returns only the method name
    return label(method)

    # Format of Book name + Method
    # return parent_dir.title() + ' ' + label(method)


# Cell
def create_label(index, method, parent_dir):
    met = label(method)
    return 'Book ' +str(index + 1) + " " + parent_dir.title() + " " + met


# Cell
def get_embed_method_and_name(fname):
    """
    Returns the name of the file and the method by
    splitting on the word '_cleaned_'
    """
    t = fname.split('_cleaned_')
    return  t[0].split()[-1], t[-1]