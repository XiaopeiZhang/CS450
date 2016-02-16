# This program was written under Python 2.7. Please test with Python 2.7 if Python 3 does not work well.
# It will ask for 2 variables. If you just press enter, it will use default values 2 leaders, and 5 followers.

__author__ = 'Xiaopei'

from threading import Thread, Semaphore
from time import sleep
from collections import deque
from itertools import cycle

class DanceMixer:

    def __init__(self, num_leader, num_follower):
        self.num_leader = num_leader
        self.num_follower = num_follower
        self.leader_q = [] # record leaders in the floor
        self.follower_q = [] # record followers in the floor
        self.partner = -1 # pass current pairing follower to leader
        self.music = None # signal whether there is a current music
        self.mutex1 = Semaphore(1) # mutex pairing process for leaders
        self.multiplex1 = Semaphore(min(self.num_leader, self.num_follower)) # max multiplex for leaders
        self.mutex2 = Semaphore(1) # mutex pairing process for followers
        self.multiplex2 = Semaphore(min(self.num_leader, self.num_follower)) # max multiplex for followers
        self.mutex3 = Semaphore(1) # mutex leader_q modification
        self.mutex4 = Semaphore(1) # mutex follower_q modification
        self.l_arrived = Semaphore(0)
        self.f_arrived = Semaphore(0)

    def band(self):
        for music in cycle(['waltz', 'tango', 'foxtrot']):
            self.mutex1.acquire()   # make sure no more pairs in the floor
            self.mutex2.acquire()
            print('** Band leader starts playing {:>5s} **'.format(music))
            self.music = music
            self.mutex1.release()
            self.mutex2.release()
            sleep(5)    # play for 5 seconds
            self.music = None       # signal that current music is about to stop
            # wait for leaders and followers to get back in line
            while len(self.leader_q) != 0 or len(self.follower_q) != 0:
                #print('wait', self.leader_q, self.follower_q)
                sleep(1)
            print('** Band leader stops playing {:>5s} **'.format(music))   # stop current music

    def leader(self, id):
        while(True):
            self.multiplex1.acquire()
            if self.music:
                self.mutex1.acquire
                # pairing leader and follower
                self.l_arrived.release()
                self.leader_q.append(id)
                print('Leader {:>1d} entering floor.'.format(id))
                self.f_arrived.acquire()
                # wait for follower to pair
                while self.partner == -1:
                    sleep(0.1)
                print('Leader {:>1d} and Follower {:>1d} are dancing.'.format(id, self.partner))
                self.partner = -1
                self.mutex1.release()
                sleep(1)

            #print(self.leader_q, 'l')
            if id in self.leader_q:
                self.mutex3.acquire()
                self.leader_q.remove(id)
                print('Leader {:>1d} getting back in line.'.format(id))
                self.mutex3.release()
            self.multiplex1.release()
            sleep(1)


    def follower(self, id):
        while(True):
            self.multiplex2.acquire()
            if self.music and self.partner == -1: # make sure no other follower is pairing
                self.mutex2.acquire()
                self.f_arrived.release()
                self.follower_q.append(id)
                self.partner = id
                print('Follower {:>1d} entering floor.'.format(id))
                self.l_arrived.acquire()
                self.mutex2.release()
                sleep(1)

            #print(self.follower_q, 'f')
            if id in self.follower_q:
                self.mutex4.acquire()
                self.follower_q.remove(id)
                print('Follower {:>1d} getting back in line.'.format(id))
                self.mutex4.release()
            self.multiplex2.release()
            sleep(1)


def main():
    num_leader = 2
    num_follower = 5

    user_input = raw_input('Enter the number of leaders: ')
    if user_input.isdigit():
        num_leader = int(user_input)
    print('The number of leaders is ' + str(num_leader))

    user_input = raw_input('Enter the number of followers: ')
    if user_input.isdigit():
        num_follower = int(user_input)
    print('The number of followers is ' + str(num_follower))

    ts = []
    dance_mixer = DanceMixer(num_leader, num_follower)
    t = Thread(target=dance_mixer.band)
    ts.append(t)
    for i in range(num_follower):
        t = Thread(target=dance_mixer.follower, args=[i])
        ts.append(t)
    for i in range(num_leader):
        t = Thread(target=dance_mixer.leader, args=[i])
        ts.append(t)
    for t in ts:t.start()
    for t in ts:t.join()

if __name__ == '__main__':
    main()
