# This program was written under Python 2.7. Please test with Python 2.7 if Python 3 does not work well.
# It will ask for 3 variables. If you just press enter, it will use default values 20 stack size, 5 discs per bucket and 3 folfers.

__author__ = 'Xiaopei'

from threading import Thread, Semaphore
from time import sleep
import random

rng = random.Random()
rng.seed(100)

class DiscGolfRange:

    def __init__(self, sizeStash, numDisc, numFrolfer):
        self.size_stash = sizeStash
        self.num_disc = numDisc
        self.num_frolfer = numFrolfer
        self.discs_on_field = 0
        self.multiplex = Semaphore(self.num_frolfer) # multiplex for frolfers
        self.empty_stash = Semaphore(0)
        self.full_stash = Semaphore(0)

    def frolfer(self, id):
        discs = 0
        while True:
            self.multiplex.acquire()

            if discs == 0:
                print('Frolfer {:>1d} calling for bucket'.format(id))
                if self.size_stash < self.num_disc:
                    self.empty_stash.release()
                    self.full_stash.acquire()
                discs = self.num_disc
                self.size_stash -= self.num_disc
                print('Frolfer {:1d} got {:>1d} discs; Stash = {:>1d}'.format(id, self.num_disc, self.size_stash))
                self.multiplex.release()
                sleep(1)        # frolfers do not have to throw right after get discs
                self.multiplex.acquire()

            print('Frolfer {:1d} threw disc {:>1d}'.format(id, self.num_disc-discs))
            self.discs_on_field += 1
            discs -= 1
            self.multiplex.release()
            sleep(rng.random())

    def cart(self):
        while True:
            self.empty_stash.acquire()
            for i in range(self.num_frolfer-1):       # make sure no other frolfers can do anything
                self.multiplex.acquire()
            print('################################################################################')
            print('stash = {:>1d}; Cart entering field'.format(self.size_stash))
            self.size_stash += self.discs_on_field
            print('Cart done, gathered {:>1d} discs; Stash = {:>1d}'.format(self.discs_on_field, self.size_stash))
            print('################################################################################')
            self.discs_on_field = 0
            for i in range(self.num_frolfer-1):
                self.multiplex.release()
            self.full_stash.release()

def main():
    stash = 20
    discs = 5
    num = 3

    user_input = raw_input('Enter the size of the stash: ')
    if user_input.isdigit():
        stash = int(user_input)
    print('The size of the stash is ' + str(stash))

    user_input = raw_input('Enter the number of discs per bucket: ')
    if user_input.isdigit():
        discs = int(user_input)
    print('The number of discs per bucket is ' + str(discs))

    user_input = raw_input('Enter the number of frolfer threads: ')
    if user_input.isdigit():
        num = int(user_input)
    print('The number of frolfer threads is ' + str(num))

    ts = []
    disc_golf_range = DiscGolfRange(stash, discs, num)
    for i in range(num):
        t = Thread(target=disc_golf_range.frolfer, args=[i])
        ts.append(t)
    t = Thread(target=disc_golf_range.cart)
    ts.append(t)
    for t in ts:t.start()
    for t in ts:t.join()

if __name__ == '__main__':
    main()
