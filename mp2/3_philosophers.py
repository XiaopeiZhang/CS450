# This program was written under Python 2.7. Please test with Python 2.7 if Python 3 does not work well.
# It will ask for 2 variables. If you just press enter, it will use default values 20 philosophers, and 1000 meals.

__author__ = 'Xiaopei'

from threading import Thread, Semaphore
from time import sleep
import random, datetime

rng = random.Random()
rng.seed(1)

class Footman:

    def __init__(self, num_philosophers, num_meals):
        self.num_philosophers = num_philosophers
        self.num_meals = num_meals
        self.forks = [Semaphore(1) for i in range(self.num_philosophers)]
        self.footman = Semaphore(self.num_philosophers-1) # at most one philosopher cannot dine

    def left(self, i):
        return i

    def right(self, i):
        return (i+1)%self.num_philosophers

    def get_forks(self, i):
        self.footman.acquire()
        self.forks[self.right(i)].acquire()
        self.forks[self.left(i)].acquire()
        
    def put_forks(self, i):       
        self.forks[self.right(i)].release()
        self.forks[self.left(i)].release()        
        self.footman.release()

    def philosopher(self, id):
        while(self.num_meals > 0):
            self.get_forks(id)
            # eating
            self.num_meals -= 1
            sleep(rng.random()/100)
            self.put_forks(id)
            # thinking
            sleep(rng.random()/100)

class Lefthanded:
    def __init__(self, num_philosophers, num_meals):
        self.num_philosophers = num_philosophers
        self.num_meals = num_meals
        self.forks = [Semaphore(1) for i in range(self.num_philosophers)]

    def left(self, i):
        return i

    def right(self, i):
        return (i+1)%self.num_philosophers

    def get_forks(self, i):
        if i == self.num_philosophers-1: # suppose the last philosopher is a leftie
            self.forks[self.left(i)].acquire()
            self.forks[self.right(i)].acquire()
        else: # the rest are righties
            self.forks[self.right(i)].acquire()
            self.forks[self.left(i)].acquire()
        
    def put_forks(self, i):        
        self.forks[self.right(i)].release()
        self.forks[self.left(i)].release()
        
    def philosopher(self, id):
        while(self.num_meals > 0):
            self.get_forks(id)
            # eating
            self.num_meals -= 1
            sleep(rng.random()/100)
            self.put_forks(id)
            # thinking
            sleep(rng.random()/100)

class Tanenbaum:
    def __init__(self, num_philosophers, num_meals):
        self.num_philosophers = num_philosophers
        self.num_meals = num_meals
        self.state = ['thinking']*self.num_philosophers
        self.sem = [Semaphore(0) for i in range(self.num_philosophers)]
        self.mutex = Semaphore(1)

    def left(self, i): # the philosopher at left
        return (i-1)%self.num_philosophers

    def right(self, i): # the philosopher at right
        return (i+1)%self.num_philosophers

    def get_forks(self, i):
        self.mutex.acquire()
        self.state[i] = 'hungry'
        self.test(i)
        self.mutex.release()
        self.sem[i].acquire()
        
    def put_forks(self, i):     
        self.mutex.acquire()  
        self.state[i] = 'thinking'
        self.test(self.right(i))
        self.test(self.left(i))
        self.mutex.release()

    def test(self, i):
        if self.state[i] == 'hungry'\
        and self.state[self.left(i)] != 'eating'\
        and self.state[self.right(i)] != 'eating':
            self.state[i] = 'eating'
            self.sem[i].release()

    def philosopher(self, id):
        while (self.num_meals > 0):
            self.get_forks(id)
            # eating
            self.num_meals -= 1
            sleep(rng.random()/100)
            self.put_forks(id)
            # thinking
            sleep(rng.random()/100)


def main():
    numPhilosophers = 20
    numMeals = 10000

    user_input = raw_input('Enter the number of philosophers: ')
    if user_input.isdigit():
        numPhilosophers = int(user_input)
    user_input = raw_input('Enter the number of meals per philosopher: ')
    if user_input.isdigit():
        numMeals = int(user_input)
    print('Running dining philosophers simulation: ' + str(numPhilosophers) + ' philosophers, ' + str(numMeals) + ' meals each')

    startT = datetime.datetime.now()
    footman = Footman(numPhilosophers, numMeals)
    ts = list()
    for i in range(numPhilosophers):
        t = Thread(target=footman.philosopher, args=[i])
        ts.append(t)
    for t in ts:t.start()
    for t in ts:t.join()
    endT = datetime.datetime.now()
    print("1. Footman solution, time elapsed: " + str((endT - startT).total_seconds()))

    startT = datetime.datetime.now()
    lefthanded = Lefthanded(numPhilosophers, numMeals)
    ts = list()
    for i in range(numPhilosophers):
        t = Thread(target=lefthanded.philosopher, args=[i])
        ts.append(t)
    for t in ts:t.start()
    for t in ts:t.join()
    endT = datetime.datetime.now()
    print("2. Left-handed solution, time elapsed: " + str((endT - startT).total_seconds()))

    startT = datetime.datetime.now()
    tanenbaum = Tanenbaum(numPhilosophers, numMeals)
    ts = list()
    for i in range(numPhilosophers):
        t = Thread(target=tanenbaum.philosopher, args=[i])
        ts.append(t)
    for t in ts:t.start()
    for t in ts:t.join()
    endT = datetime.datetime.now()
    print("3. Tanenbaum's solution, time elapsed: " + str((endT - startT).total_seconds()))
    
if __name__ == '__main__':
    main()