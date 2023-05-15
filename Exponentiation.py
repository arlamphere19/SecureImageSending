#Amanda Lamphere
#Exponentiation
#This module performs the creation of the one-time pad
#as described by Dougherty et al. This pad is the length
#of the number of pixels of the image times three for each
#(R, G, B) value.

class Exponentiation:

    #Initialize each varaible
    def __init__(self, s, prime, primitiveRoot, rows, columns):
        self.s = s
        self.prime = prime
        self.primitiveRoot = primitiveRoot
        self.rows = rows
        self.columns = columns

    #Creation of One-Time Pad
    def oneTimePad(self):

        #S is calculated from another class
        elements = list(range(self.s,(self.rows*self.columns*3) + self.s))

        divisor = int(self.prime/pow(2, self.primitiveRoot))
        exponent = (int)((self.prime - 1)/divisor)

        #New list of elements
        newElements = [pow(i, exponent, divisor) for i in elements]

        return newElements
