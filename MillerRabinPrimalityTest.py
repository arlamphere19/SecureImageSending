#Miller Rabin Primality Test
#Amanda Lamphere
#This module performs the algorithm described in the
#Miller-Rabin Primality Test. For more description on this,
#visit: https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test

import random
import pandas as pd
import numpy as np
from datetime import datetime
import os

#Method to generate a large random number
def generateBigOddNumber():
    n = random.randint(pow(10,18), pow(10,19))
    if n % 2 == 0:
        return generateBigOddNumber()
    else:
        return n

#Factors for k in the equation n=(2^k)m
def factorForK(num) -> int:
    k = 0
    x = num % 2
    n = num
    while x == 0:
        k = k + 1
        n = n / 2
        x = n % 2
    return k

#Factors for m in the equation n=(2^k)m
def factorForM(num, k) -> int:
    return (num / (2**k))
        
#Perform the Miller-Rabin Primality Test
def primalityTest(n, a, k, m) -> bool:
    b = pow(a,m,n)
    i = 0
    if (b == 1 or b == (n-1)):
        return True
    else:
        i = i + 1
        while (i < k - 1):
            b = pow(b,2,n)
            if (b == (n-1)):
                return True
            elif (b == 1):
                return False
            i = i + 1
        b = pow(b,2,n)
        if (b != (n-1)):
            return False
        else:
            return True

#Set up prime diction, primitive root dictionary, and list of 'a' values
primeDictionary = []
rootDictionary = []
a = [2,3,5,7,11]

#Main Method
#Repeat until there are 100 primes
bigOdd = generateBigOddNumber()
while (len(primeDictionary) != 100):
    bigOdd = bigOdd + 2
    k = factorForK(bigOdd-1)
    m = int(factorForM(bigOdd-1, k))
    i = 0
    #Test primality for all 'a's
    while (i < 5):
        if (primalityTest(bigOdd, a[i], k, m)):
            i = i + 1
        else:
            break
    #If true, add to dictionary.
    if (i == 5):
        primeDictionary.append(bigOdd)
        rootDictionary.append(k)

#Set up dataframe for CSV file
columns = ['Primes', 'Primitive Roots']
df = pd.DataFrame([primeDictionary, rootDictionary], index=columns)
df = df.T

#Save to filepath where this application is located
df.to_csv(str(os.getcwd()) + "/out.csv", index=False)
