'''
Created on 2013-12-9

@author: kongfy
'''

import math
import sys
import os
import cPickle
import gc

config = {'K' : 10000,
          }

def load_train_data():
    f_train = open('train.txt', 'r')
    for line in f_train:
        user, movie, rate = line.split()
        user = int(user); movie = int(movie); rate = int(rate)
        
        user_set.add(user)
        movie_set.add(movie)
        
        total, count = movie_rate.get(movie, (0, 0))
        movie_rate[movie] = (total + rate, count + 1)
        
        total, count = user_rate.get(user, (0, 0))
        user_rate[user] = (total + rate, count + 1)
        
        user_list = movie_userlist.get(movie, [])
        user_list.append(user)
        movie_userlist[movie] = user_list
        
        movie_list = user_movielist.get(user, [])
        movie_list.append(movie)
        user_movielist[user] = movie_list
        
        user_rating = rating_data.get(user, {})
        user_rating[movie] = rate
        rating_data[user] = user_rating
        
    f_train.close()
            
def average_rate_on_movie(movie):
    total, count = movie_rate.get(movie, (0, 0))
    if (count == 0):
        return 3.0
    return float(total) / count

def average_rate_by_user(user):
    total, count = user_rate.get(user, (0, 0))
    if count == 0:
        return 3.0
    return float(total) / count

def similarity_between_movies(movie_i, movie_j):
    user_i = movie_userlist[movie_i]
    user_j = movie_userlist[movie_j]
    users = set(user_i) & set(user_j)
    
    if len(users) == 0:
        return 0.0
    
    average_rate_i = average_rate_on_movie(movie_i)
    average_rate_j = average_rate_on_movie(movie_j)
    a = 0.0
    b = 0.0
    c = 0.0
    for user in users:
        a += (rating_data[user][movie_i] - average_rate_i) * (rating_data[user][movie_j] - average_rate_j)
        b += (rating_data[user][movie_i] - average_rate_i) ** 2
        c += (rating_data[user][movie_j] - average_rate_j) ** 2
    if b * c == 0:
        return 0.0
    similarity = a / math.sqrt(b * c)
    if similarity < 0:
        return 0.0
    return similarity

def get_w(t):
    movie, w = t
    return w

def k_similar_movie(movie, k):
    return item_relations[movie]
    
    #temp = item_relations[movie].items()
    #temp = sorted(temp, key = get_w, reverse = True)
    #return temp[:k]

def sort_relations():
    n = len(movie_list)
    
    for i in xrange(n):
        sys.stdout.write("\rsorting relations %s / %s" % (i + 1, n))
        sys.stdout.flush()
        movie = movie_list[i]
        temp = item_relations[movie].items()
        temp = sorted(temp, key = get_w, reverse = True)
        item_relations[movie] = temp

        if i % 100 == 0:
            gc.collect()
    sys.stdout.write('\n')
    gc.collect()
    
def item_based_CF():
    n = len(movie_list)
    
    for i in xrange(n):
        sys.stdout.write("\rcalulating relations %s / %s" % (i + 1, n))
        sys.stdout.flush()
        movie_i = movie_list[i]
        relations = {}
        for j in xrange(0, i):
            movie_j = movie_list[j]
            similarty = item_relations[movie_j].get(movie_i, 0)
            if similarty != 0:
                relations[movie_j] = similarty
        for j in xrange(i + 1, n):
            movie_j = movie_list[j]
            similarty = similarity_between_movies(movie_i, movie_j)
            if similarty != 0:
                relations[movie_j] = similarty 
        item_relations[movie_i] = relations
    sys.stdout.write('\n')

def predict(user, movie):
    if not rating_data.get(user):
        rate = average_rate_on_movie(movie)
        #print 'lazy user %d, rate for movie %d: %f' % (user, movie, rate)
        return rate
    
    if rating_data[user].get(movie):
        rate = rating_data[user][movie]
        #print 'already rated, user %d, movie %d, rate: %f' % (user, movie, rate)
        return rate
    
    if not movie_userlist.get(movie):
        rate = average_rate_by_user(user)
        #print 'cold movie %d, rate for user %d: %f' % (movie, user, rate)
        return rate
                
    
    basic_rate = average_rate_on_movie(movie)
    ref_movies = k_similar_movie(movie, config['K'])
    
    a = 0.0
    b = 0.0
    for ref_movie, w in ref_movies:
        ref_rate = rating_data[user].get(ref_movie)
        if ref_rate:
            a += w * (ref_rate - basic_rate)
            b += abs(w)
    if b == 0:
        return basic_rate
    return basic_rate + a / b;

if __name__ == '__main__':
    global user_set
    global movie_set
    
    global movie_userlist
    global user_movielist
    global rating_data
    global movie_rate
    global user_rate
    
    global movie_list
    global item_relations
    
    if os.path.exists('train.dat'):
        datFile = open('train.dat', 'r')
        movie_rate = cPickle.load(datFile)
        user_rate = cPickle.load(datFile)
        movie_userlist = cPickle.load(datFile)
        rating_data = cPickle.load(datFile)
        item_relations = cPickle.load(datFile)
        datFile.close()
    else:
        user_set = set()
        movie_set = set()
        movie_userlist = {}
        user_movielist = {}
        rating_data = {}
        movie_rate = {}
        user_rate = {}
        
        print 'laoding train.txt...'
        load_train_data()
        
        movie_list = list(movie_set)
        item_relations = {}
        
        print 'CF...'
        item_based_CF()
        sort_relations()
        
        datFile = open('train.dat', 'w')
        cPickle.dump(movie_rate, datFile)
        cPickle.dump(user_rate, datFile)
        cPickle.dump(movie_userlist, datFile)
        cPickle.dump(rating_data, datFile)
        cPickle.dump(item_relations, datFile)
        datFile.close()

    
    
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
        if rate == 0:
            rate = 3
        if rate > 5:
            rate = 5
        f_output.write((str(rate)) + '\n')
    sys.stdout.write('\n')
    
    f_test.close()
    f_output.close()
    
    
