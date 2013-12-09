'''
Created on 2013-12-9

@author: kongfy
'''

def load_train_data():
    pass

def predict(user, movie):
    return 0

if __name__ == '__main__':
    load_train_data()
    
    f_test = open('test.txt', 'r')
    f_output = open('test.rate', 'w')
    for line in f_test:
        [user, movie] = line.split()
        f_output.write(str(predict(user, movie)) + '\n')
    
    f_test.close()
    f_output.close()
    
    