#include "types.h"
#include "user.h"
#include "syscall.h"
#define B_SIZE 3

// implement semaphore using mutex
// refer to http://www.csc.uvic.ca/~mcheng/460/notes/gensem.pdf
struct semaphore{
  int val;
  int mut;
  int cond;
};

struct semaphore *space;
struct semaphore *item;

void
sm_create(struct semaphore *s, int value){
  s->val = value;
  s->mut = mtx_create(0);
  s->cond = mtx_create(1);
}

void
sm_acquire(struct semaphore *s){
  mtx_lock(s->mut);
  s->val -= 1;
  //printf(1, "acquire %d\n", s->val);
  if(s->val < 0){
    mtx_unlock(s->mut);
    mtx_lock(s->cond);
  }
  else{
    mtx_unlock(s->mut);
  }
}

void
sm_release(struct semaphore *s){
  mtx_lock(s->mut);
  s->val += 1;
  //printf(1, "release %d\n", s->val);
  if(s->val <= 0)
    mtx_unlock(s->cond);
  mtx_unlock(s->mut);
}

// implement producer/consumer problem
int buffer[B_SIZE];
int mutex;
static int counter1;  // the number of objects in total added by producers
static int counter2;  // the number of objects in total removed by consumers

void
producer(void* par)
{
  int id = *((int*)par);
  int event1 = 0;
  int c = 0; // randomize sleep
  while(counter1 > 0){
    sm_acquire(space);
    //printf(1, "ac space");
    mtx_lock(mutex);
    printf(1, "Producer %d is adding buffer %d\n", id, event1);
    buffer[event1]++;
    counter1 --;
    event1 = (event1 + 1) % B_SIZE;
    mtx_unlock(mutex);
    sm_release(item);
    //printf(1, "rl item");
	
    c += 1;
    if(c%2 == 0)
      sleep(10);
    else
      sleep(5);
  }
  printf(1, "Producer %d is done\n", id);
}

void
consumer(void* par)
{
  int id = *((int*)par);
  int event2 = 0;
  int c = 0; // randomize sleep
  while(counter2 > 0){
    //printf(1, "counter1 %d, counter2 %d\n", counter1, counter2);
    //printf(1, "event2 %d, buffer %d\n", event2, buffer[event2]);
    if(buffer[event2] > 0){
      //printf(1, "try ac item");
      sm_acquire(item);
      //printf(1, "ac item");
      mtx_lock(mutex);
      printf(1, "Consumer %d is removing buffer %d\n", id, event2);
      buffer[event2]--;
      counter2--;
      event2 = (event2 + 1) % B_SIZE;
      mtx_unlock(mutex);
      sm_release(space);
      //printf(1, "rl space");
    }
    else
      event2 = (event2 + 1) % B_SIZE;
	
    c += 1;
    if(c%2 == 0)
      sleep(20);
    else
      sleep(12);
  }
  printf(1, "Consumer %d is done\n", id);
}

int
main(int argc, char *argv[]){
  int i;
  for(i=0;i<B_SIZE;i++){
    buffer[i] = 0;
  }

  space = malloc(sizeof(struct semaphore));
  item = malloc(sizeof(struct semaphore));
  sm_create(space, B_SIZE);
  sm_create(item, 0);
  mutex = mtx_create(0);

  counter1 = 20;
  counter2 = 20;

  int p_num = 2;
  int c_num = 3;
  
  void *st1[p_num];
  
  for(i=0;i<p_num;i++){
    st1[i] = malloc(4096);
    int *ar = malloc(sizeof(*ar));
    *ar = i+1;
    int p_id = thread_create(producer, st1[i]+4096-1, ar);
    printf(1, "Create producer %d with thread id %d\n", i+1, p_id);
  }
  
  void *st2[c_num];

  for(i=0;i<c_num;i++){
    st2[i] = malloc(4096);
    int *ar = malloc(sizeof(*ar));
    *ar = i+1;
    int c_id = thread_create(consumer, st2[i]+4096-1, ar);
    printf(1, "Create consumer %d with thread id %d\n", i+1, c_id);
  }

  void **pstack = 0;

  for(i=0;i<p_num;i++){
    thread_join(pstack);
    //printf(1, "st1 %x, pstack %x\n", st1[i], *pstack);
    free(*pstack);
  }

  for(i=0;i<c_num;i++){
    thread_join(pstack);
    //printf(1, "st2 %x, pstack %x\n", st2[i], *pstack);
    free(*pstack);
  }

  exit();
}

