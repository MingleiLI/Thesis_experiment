# coding: utf-8
from load_data import load_CVAT_2
from load_data import load_CVAW
from VA_prediction import clean_str_word
from evaluate import regression_evaluate
from sklearn import cross_validation
import numpy as np
from sklearn import linear_model


def mean_ratings(texts, lexicon, mean_method):
    predicted_ratings = []

    def tf_geo(text):  # tf_geo
        sum_valence = 1
        count = 0
        word_list = text.split()
        for word in word_list:
            for line in lexicon:
                if word == line:
                    count = count + 1
                    sum_valence = sum_valence * lexicon[line]
        return 5 if count == 0 else sum_valence ** (1. / count)  # geo

    def tf_mean(text):  # tf_mean
        sum_valence = 0
        count = 0
        word_list = text.split()
        for word in word_list:
            for line in lexicon:
                if word == line:
                    count = count + 1
                    sum_valence = sum_valence + lexicon[line]
        return 5 if count == 0 else sum_valence / count

    if mean_method == 'tf_geo':
        VA_mean = tf_geo
    elif mean_method == 'tf_mean':
        VA_mean = tf_mean
    else:
        raise Exception('Parameters Wrong.')

    for text in texts:
        V = VA_mean(clean_str_word(text))
        predicted_ratings.append(V)
    print(predicted_ratings[:200])
    return predicted_ratings


def linear_regression(X_train, X_test, Y_train, Y_test, plot=False):
    # Create linear regression object
    # The training data should be column vectors
    X_train, X_test = np.array(X_train).reshape((len(X_train), 1)), np.array(X_test).reshape((len(X_test), 1))
    regr = linear_model.LinearRegression()
    # Train the model using the training sets
    regr.fit(X_train, Y_train)
    predict = regr.predict(X_test)
    regression_evaluate(Y_test, predict)


def cv(data, target):
    X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(data, target, test_size=0.2, random_state=2)
    linear_regression(X_train, X_test, Y_train, Y_test, plot=False)


if __name__ == '__main__':

    ####################### Hyper-parameters #########################
    using_extended_lexicon = False  # 'True' or 'False'
    option = 'V'  # 'V' or 'A'
    mean_method = 'tf_geo'  # values: 'tf_geo', 'tf_mean'
    sigma = 1.0  # values: '1.0', '1.5', '2.0'
    ##################################################################

    texts, valence, arousal = load_CVAT_2('./resources/CVAT2.0(sigma=' + str(sigma) + ').csv')
    lexicon = load_CVAW(extended=using_extended_lexicon)
    d = dict()
    ind = 1 if option == 'V' else 2
    for l in lexicon:
        d[l[0]] = l[ind]

    predicted_ratings = mean_ratings(texts, d, mean_method)
    print(predicted_ratings)
    print(valence)
    regression_evaluate(valence, predicted_ratings)

    cv(predicted_ratings, valence)