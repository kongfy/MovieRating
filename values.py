'''
Created on 2013-12-13

@author: kongfy
'''

if __name__ == '__main__':
    f = open('test.rate', 'r')
    
    rates = set()
    for line in f:
        rate = int(line)
        if rate not in rates:
            print rate
        rates.add(rate)
        
    f.close() 