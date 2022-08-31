import threading
import time
sem_producer = threading.Semaphore()
sem_consumper = threading.Semaphore()

def consumer():
    while True:
        sem_producer.acquire()
        print("Im consumer")
        sem_consumper.release()
        time.sleep(0.01)

def producer():
    while True:
        sem_consumper.acquire()
        print("Im producer")
        sem_producer.release()
        time.sleep(5)

t = threading.Thread(target = consumer)
t.start()
t2 = threading.Thread(target = producer)
t2.start()