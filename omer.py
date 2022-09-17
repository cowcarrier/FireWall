import time
import functools


def timed(func):
    #this decorator will print the amount of time a function takes to run
    def wrappedFunc(*args,**kwargs):
        start = time.time()
        returnedVal = func(*args,**kwargs)
        if time.time()-start > 0.01:
            print(f"the function {func.__name__} took {time.time()-start} seconds to run")
        return returnedVal
    return wrappedFunc


def writen(functionName = None):
    #this decorator will write th values given to the function and the function's output
    def writenSubFunc(func):
        def wrappedFunc(*args, **kwargs):
            returnedVal = func(*args, **kwargs)
            print(f"{functionName} was called \nand was given the values {[i for i in args]} \nit returned {returnedVal}")
            return returnedVal
        return wrappedFunc

    def writenSubFuncNameIsNone(func):
        functionName = func.__name__
        def wrappedFunc(*args,**kwargs):
            returnedVal = func(*args,**kwargs)
            print(f"{functionName} was called \nand was given the values {[i for i in args]} \nit returned {returnedVal}" )
            return returnedVal
        return wrappedFunc

    if functionName == None:
        return writenSubFuncNameIsNone
    return writenSubFunc

def goodlyWrittenCode():
    import string;
    print(''.join((z := ' ' + string.ascii_lowercase + '.,')[z.index(i) - 2] for i in 'yj.bkubgxgt.vjkpibjgtgbuqbygktf'))


def theMeaningOfLife():
    return(True << True << True << True << True << True | True << True | True << True << True << True)


@writen("new name")
@timed
def badFibo(x):
    return badFiboRecursive(x)


def badFiboRecursive(x):
    if x <= 1:
        return 1
    return badFiboRecursive(x-1) + badFiboRecursive(x-2)

badFibo(35)