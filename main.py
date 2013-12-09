'''
Created on 2013-12-9

@author: kongfy
'''

def load_train_data():
    f_train = open('train.txt', 'r')
    for line in f_train:
        user, movie, rate = line.split()
        user = int(user); movie = int(movie); rate = int(rate)
        
        user_set.add(user)
        movie_set.add(movie)
        
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
    
def slope_one():
    movie_list.sort();
    for i in range(len(movie_list)):
        for j in range(i + 1, len(movie_list)):
            movie_i = movie_list[i]
            movie_j = movie_list[j]
            
            user_for_i = movie_userlist[movie_i]
            user_for_j = movie_userlist[movie_j]
            
            user_union = list(set(user_for_i) & set(user_for_j))
            
            total = 0
            count = len(user_union)
            
            if count == 0:
                continue
            
            for user in user_union:
                total += rating_data[user][movie_j] - rating_data[user][movie_i]
            
            temp = slope_one_info.get(movie_i, {})
            temp[movie_j] = (float(total) / count, count)
            slope_one_info[movie_i] = temp

def predict(user, movie):
    if not rating_data.get(user):
        print 'lazy user...'
        return 3
    
    if rating_data[user].get(movie):
        print 'already rated...'
        return rating_data[user][movie]
    
    movie_list = user_movielist[user]
    a = 0
    b = 0
    
    movie_b = movie
    for movie_a in movie_list:
        basic_rate = rating_data[user][movie_a]
        
        movie_i = movie_a
        movie_j = movie_b
        t = 1
        
        if (movie_b < movie_a):
            movie_i = movie_b
            movie_j = movie_a
            t = -1
            
        fix, count = slope_one_info[movie_i].get(movie_j, (0, 0))
        b += count
        a += count * (basic_rate + fix * t)
    
    print 'slope one...'
    return min(float(a) / b, 5.0)
    

if __name__ == '__main__':
    global user_set
    global movie_set
    
    global movie_userlist
    global user_movielist
    global rating_data
    
    user_set = set()
    movie_set = set()
    movie_userlist = {}
    user_movielist = {}
    rating_data = {}
    
    print 'laoding train.txt...'
    load_train_data()
    
    global movie_list
    global slope_one_info
    
    movie_list = list(movie_set)
    slope_one_info = {}
    
    print 'slope one...'
    slope_one()
    
    print 'testing...'
    f_test = open('test.txt', 'r')
    f_output = open('test.rate', 'w')
    for line in f_test:
        [user, movie] = line.split()
        user = int(user); movie = int(movie)
        rate = int(round(predict(user, movie)))
        f_output.write((str(rate)) + '\n')
    
    f_test.close()
    f_output.close()
    
    