import os
from multiprocessing import Process
from queue import Queue
import time

def producer(queue):
    for i in range(5):
        time.sleep(1)  # Simulate some work
        item = f"Item {i}"
        queue.put(item)
        print(f"Producer: Put {item} into the queue")

def consumer(queue):
    while True:
        item = queue.get()
        print(f"Consumer: Retrieved {item} from the queue")
        time.sleep(2)  # Simulate some work

if __name__ == '__main__':
    queue = Queue()

    p1 = Process(target=producer, args=(queue,))
    p2 = Process(target=consumer, args=(queue,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
