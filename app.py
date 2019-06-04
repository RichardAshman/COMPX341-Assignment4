import time

import redis
from flask import Flask

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

totalKeysStored = 0

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)
@app.route('/isPrime/<int:inputNum>')
def isPrime(inputNum):
    global totalKeysStored

    # Corner cases 
    if (inputNum <= 1) : 
        return '{} is not prime.\n'.format(inputNum)
    if (inputNum <= 3) : 
        if(cache.get("p" + str(inputNum)) is None) :
            cache.set("p" + str(inputNum), inputNum)
            cache.set("primeNo" + str(totalKeysStored), inputNum)
            totalKeysStored += 1
            return '{} is prime.\n'.format(inputNum)
  
    # www.geeksforgeeks.org/python-program-to-check-whether-a-number-is-prime-or-not/
    # This is checked so that we can skip middle five numbers in below loop 
    if (inputNum % 2 == 0 or inputNum % 3 == 0) : 
        return '{} is not prime.\n'.format(inputNum)
  
    i = 5
    while(i * i <= inputNum) : 
        if (inputNum % i == 0 or inputNum % (i + 2) == 0) : 
            return '{} is not prime.\n'.format(inputNum)
        i = i + 6
    # store inputNum into Redis
    # if("".join(map(chr, cache.get("p" + str(inputNum)))) is none) :
    if(cache.get("p" + str(inputNum)) is None) :
        cache.set("p" + str(inputNum), inputNum)
        cache.set("primeNo" + str(totalKeysStored), inputNum)
        totalKeysStored += 1
    return '{} is prime.\n'.format(inputNum)

@app.route('/primesStored')
def primesStored():
    global totalKeysStored

    r = ""
    keyCount = 0
    while(keyCount <= totalKeysStored-1) :
        reqName = "primeNo" + str(keyCount)
        data = "".join(map(chr, cache.get(reqName)))

        if data is not None:
            r = r + data + " "
        keyCount += 1
    return r + "\n"
