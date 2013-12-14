'''
Created on 2013-12-13

@author: kongfy
'''

import math
import random
import os
import sys

def load_train_data():
    global average_rate, user_count, movie_count
    
    average_rate = user_count = movie_count = 0
    
    f_train = open('train.txt', 'r')
    total_rate = 0
    total_count = 0
    
    for line in f_train:
        user, movie, rate = line.split()
        user = int(user); movie = int(movie); rate = int(rate)
        
        if user_dict.get(user) == None:
            user_dict[user] = user_count
            user_count += 1
            
        if movie_dict.get(movie) == None:
            movie_dict[movie] = movie_count
            movie_count += 1
        
        user = user_dict[user]
        movie = movie_dict[movie]
        
        total_rate += rate
        total_count += 1
        
        total, count = movie_rate.get(movie, (0, 0))
        movie_rate[movie] = (total + rate, count + 1)
        
        total, count = user_rate.get(user, (0, 0))
        user_rate[user] = (total + rate, count + 1)
        
        user_rating = rating_data.get(user, {})
        user_rating[movie] = rate
        rating_data[user] = user_rating
        
        average_rate = float(total_rate) / total_count
        
    f_train.close()
    
def iner_product(v1, v2):
    result = 0
    for i in range(len(v1)):
        result += v1[i] * v2[i]
    return result
    
def predict_svd(user, movie):
    rate = average_rate + bu[user] + bi[movie] + iner_product(pu[user], qi[movie])
    if rate < 1:
        rate = 1.0
    if rate > 5:
        rate = 5.0
    return rate
    
def svd():
    global bi, bu, qi, pu
    
    factor = 2
    learn_rate = 0.01
    regularization = 0.05
    
    temp = math.sqrt(factor)
    bi = [0.0 for i in xrange(movie_count)]
    bu = [0.0 for i in xrange(user_count)]
    qi = [[(0.1 * random.random() / temp) for j in xrange(factor)] for i in xrange(movie_count)]
    pu = [[(0.1 * random.random() / temp) for j in xrange(factor)] for i in xrange(user_count)]
    
    preRmse = 10.0
    for r in xrange(1000):
        for user, user_rates in rating_data.iteritems():
            for movie, rate in user_rates.iteritems():
                prediction = predict_svd(user, movie)
                
            eui = rate - prediction
        
            bu[user] += learn_rate * (eui - regularization * bu[user])
            bi[movie] += learn_rate * (eui - regularization * bi[movie])
                
            for k in xrange(factor):
                temp = pu[user][k]
                pu[user][k] += learn_rate * (eui * qi[movie][k] - regularization * pu[user][k])
                qi[movie][k] += learn_rate * (eui * temp - regularization * qi[movie][k])
        
        #learn_rate *= 0.9
        curRmse = validate(bu, bi, pu, qi)
        print("round %d: %f" %(r, curRmse))
        if curRmse >= preRmse:
            break
        else:
            preRmse = curRmse
    
def validate(bu, bi, pu, qi):
    rmse = 0
    count = 0
    for user, user_rates in rating_data.iteritems():
        for movie, rate in user_rates.iteritems():
            count += 1            
            prediction = predict_svd(user, movie)
            rmse += (rate - prediction) ** 2
    return math.sqrt(float(rmse) / count)

def average_rate_on_movie(movie):
    total, count = movie_rate.get(movie, (0, 0))
    if (count == 0):
        return 1.0
    return float(total) / count

def average_rate_by_user(user):
    total, count = user_rate.get(user, (0, 0))
    if count == 0:
        return 1.0
    return float(total) / count

def predict(user, movie):
    user = user_dict.get(user, -1)
    movie = movie_dict.get(movie, -1)
    
    if user < 0:
        if movie < 0:
            rate = 3.0
        else:
            rate = rate = average_rate_on_movie(movie)
        return rate
    
    if movie < 0:
        rate = average_rate_by_user(user)
        return rate
    
    if rating_data[user].get(movie):
        rate = rating_data[user][movie]
        return rate
    
    return predict_svd(user, movie)

if __name__ == '__main__':
    global user_dict, movie_dict
    global rating_data
    global movie_rate, user_rate
    global average_rate, user_count, movie_count
    global bi, bu, qi, pu
    
    user_dict = {}
    movie_dict = {}
    rating_data = {}
    movie_rate = {}
    user_rate = {}
    
    if not os.path.exists('model.dat'):
        print 'loading train.txt...'
        load_train_data()
    
        print 'training SVD model...'
        svd()
    
    print 'testing...'
    f_test = open('test.txt', 'r')
    f_output = open('test.rate', 'w')
    i = 0
    
    for line in f_test:
        i += 1
        sys.stdout.write("\rpredicting : %s / 250000" % (i))
        sys.stdout.flush()
        [user, movie] = line.split()
        user = int(user); movie = int(movie)
        rate = int(round(predict(user, movie)))
        if rate < 1:
            rate = 1
        if rate > 5:
            rate = 5
        f_output.write((str(rate)) + '\n')
    sys.stdout.write('\n')
    
    f_test.close()
    f_output.close()