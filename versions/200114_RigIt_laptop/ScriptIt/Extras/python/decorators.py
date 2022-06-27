# Decorators
#1.
def add(a, b):
    return a + b
print add(1, 2)

print add.__call__

print add.__call__(1, 2)


#2.
def nothing(func):
    return func
print nothing(add)(1, 2)


#3.
def makeadd():
    def adder(a, b):
        return a + b
    return adder
print makeadd()(1, 2)

#4.
def makeadd(adder):
    def inner(a, b):
        return adder(a, b)
    return inner
print makeadd(add)(1, 2)

#5.
def announce(adder):
    def inner(a, b):
        print 'Adding', a, b
        result = adder(a, b)
        print 'Got', result
        return result
    return inner
print announce(add)(1, 2)

#6.
def announce(func):
    def inner(a, b):
        print 'Calling', func.__name__, a, b
        result = func(a, b)
        print 'Got', result
        return result
    return inner
def subtract(a, b):
    return a - b
print announce(subtract)(1, 2)

#7.
def announce(func):
    def inner(*args, **kwargs):
        print 'Calling', func.__name__, args, kwargs
        result = func(*args, **kwargs)
        print 'Got', result
        return result
    return inner
def add3(a, b, c):
    return a + b + c
print announce(add)(1, 2)
print announce(subtract)(1, 2)
print announce(add3)(1, 2, 3)

#8.
loud_add = announce(add)
print loud_add(1, 2)

#9. it will have the print behavior imbued into it through announce
add = announce(add)
print add(1, 2)

#10.
@announce
def divide(a, b):
    return a / b
print divide(10, 2)



