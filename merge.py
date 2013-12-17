'''
Created on 2013-12-13

@author: kongfy
'''

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

def distance(x, y):
    return abs(x - y)


if __name__ == '__main__':
    global user_dict, movie_dict
    global rating_data
    global movie_rate, user_rate
    global average_rate, user_count, movie_count
    
    user_dict = {}
    movie_dict = {}
    rating_data = {}
    movie_rate = {}
    user_rate = {}
    
    print 'loading train.txt...'
    load_train_data()
    
    f_test = open('test.txt', 'r')
    f_output = open('output_merge.rate', 'w')
    f_1 = open('04581_200.rate', 'r')
    f_2 = open('04575.rate', 'r')
    
    i = 0
    
    for line in f_test:
        user, movie = line.split()
        
        user = user_dict.get(int(user), -1)
        movie = movie_dict.get(int(movie), -1)
        
        rate = 0
        a = int(f_1.readline())
        b = int(f_2.readline())
        
        
        if a == b:
            rate = a
        else:
            #print 'user %s, movie %s, u_average %s, i_average %s, rate: %s %s' % (user, movie, average_rate_by_user(user), average_rate_on_movie(movie), a, b)
            base_line = average_rate_on_movie(movie)
            if distance(base_line, a) < distance(base_line, b):
                rate = a
            else:
                rate = b
            
        f_output.write((str(rate)) + '\n')
    
    f_test.close()
    f_output.close()
    f_1.close()
    f_2.close()