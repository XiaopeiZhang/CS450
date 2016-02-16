#include "types.h"
#include "x86.h"
#include "defs.h"
#include "param.h"
#include "memlayout.h"
#include "mmu.h"
#include "proc.h"

int
sys_fork(void)
{
  return fork();
}

int
sys_exit(void)
{
  exit();
  return 0;  // not reached
}

int
sys_wait(void)
{
  return wait();
}

int
sys_kill(void)
{
  int pid;

  if(argint(0, &pid) < 0)
    return -1;
  return kill(pid);
}

int
sys_getpid(void)
{
  return proc->pid;
}

int
sys_sbrk(void)
{
  int addr;
  int n;

  if(argint(0, &n) < 0)
    return -1;
  addr = proc->sz;
  if(growproc(n) < 0)
    return -1;
  return addr;
}

int
sys_sleep(void)
{
  int n;
  uint ticks0;
  
  if(argint(0, &n) < 0)
    return -1;
  acquire(&tickslock);
  ticks0 = ticks;
  while(ticks - ticks0 < n){
    if(proc->killed){
      release(&tickslock);
      return -1;
    }
    sleep(&ticks, &tickslock);
  }
  release(&tickslock);
  return 0;
}

// return how many clock tick interrupts have occurred
// since start.
int
sys_uptime(void)
{
  uint xticks;
  
  acquire(&tickslock);
  xticks = ticks;
  release(&tickslock);
  return xticks;
}

// return how many times the system call is invoked since start.
int
sys_getcount(void)
{
  int num;
  if(argint(0, &num) < 0)		// locate the position of the system call
    return -1;
  return getcount(num);
}

int
sys_thread_create(void)
{
  void *tmain;
  void *stack;
  void *arg;
  if(argptr(0, (char **)&tmain, sizeof(void *)) < 0 || argptr(1, (char **)&stack, sizeof(void *)) < 0 || argptr(2, (char **)&arg, sizeof(void *)) < 0)
    return -1;
  return thread_create(tmain, stack, arg);
}

int
sys_thread_join(void)
{
  void **stack;
  if(argptr(0, (char **)&stack, sizeof(void *)) < 0)
    return -1;
  return thread_join(stack);
}

int
sys_mtx_create(void)
{
  int locked;
  if(argint(0, &locked) < 0)
    return -1;
  return mtx_create(locked);
}

int
sys_mtx_lock(void)
{
  int lock_id;
  if(argint(0, &lock_id) < 0)
    return -1;
  return mtx_lock(lock_id);
}

int
sys_mtx_unlock(void)
{
  int lock_id;
  if(argint(0, &lock_id) < 0)
    return -1;
  return mtx_unlock(lock_id);
}