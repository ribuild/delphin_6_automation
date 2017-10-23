import threading
import subprocess
from queue import Queue
import time


# replace with asyncio

def exampleJob(filename):
    print('\n========== Running : {} ==========\n'.format(filename))
    delphin_executable = r'C:\Program Files\IBK\Delphin 6.0\delphinSolver.exe'
    subprocess.run([delphin_executable, filename])

def threader():
    while True:
        filename = q.get()
        exampleJob(filename)
        q.task_done()

q = Queue()

for x in range(3):
    t = threading.Thread(target = threader)
    t.daemon = True
    t.start()

start = time.time()

for _ in range(999):
    q.put("./delphin_files/template_0.d6p")
    q.put("./delphin_files/template_1.d6p")
    q.put("./delphin_files/template_2.d6p")
    q.put("./delphin_files/template_3.d6p")
    q.put("./delphin_files/template_4.d6p")

q.join()


print("entire job took:", time.time() - start)
