import sys, os
import cv2 as cv
from random import randint
from reedmuller import reedmuller
from src.Helper import Helper


class Coder(object):
    order = 2
    dimension = 5
    rm = reedmuller.ReedMuller(order, dimension)

    def __init__(self):    
        pass

    @staticmethod
    def encode(message):
        binary_message = Helper.StringToBinary(message)
        if len(message)%2!=0:
            binary_message+= 8*"0"

        n = 8*Coder.order
        binary_message+= n*"0"
        chunks = [binary_message[i:i+n] for i in range(0, len(binary_message), n)]
        encoded = []
        for chunk in chunks:
            encoded.append(''.join(map(str, Coder.rm.encode(list(map(int, chunk)))))) 
        return ''.join(encoded)

    @staticmethod
    def decode(encoded):
        n = 8*Coder.order*2
        chunks = [encoded[i:i+n] for i in range(0, len(encoded), n)]
        decoded = []
        for chunk in chunks:
            try:
                decoded.append(''.join(map(str, Coder.rm.decode(list(map(int, chunk))))))
            except Exception as error:
                decoded.append("")
        return ''.join(decoded)

    

    @staticmethod
    def replaceCharByIndex(str, i):
        # bin = "0" if(str[i]=="1") else "1"
        bin = ""
        if(str[i]=="1"):
            bin = "0"
        else:
            bin = "1"
        print(f'{str[i]}<>{bin}')
        return str[: i] + bin + str[i + 1:]

    @staticmethod
    def makeErrors(encoded):
        n = 8*Coder.order*2
        chunks = [encoded[i:i+n] for i in range(0, len(encoded), n)]
        max_errors = Coder.order+1
        encoded_with_errors = []
        for chunk in chunks:
            indexes = [randint(0, len(chunk)-1) for e in range(0, max_errors )]
            print(f'{len(indexes)} : {indexes}')
            chunk_errors = chunk
            for index in indexes:
                chunk_errors = Coder.replaceCharByIndex(chunk_errors, index)
            encoded_with_errors.append(chunk_errors)
        return ''.join(encoded_with_errors)



"""
# message = '1100110101010101'
# encoded =             '10111000011101000001110111010001'
# encoded_with_errors = '10111010011101000101010111010001'

data = [ "dev", "loker", "30", "m", "clinic01", "AE4569" ]
# data = { "name": "devloker", "date": "07-21-1990" }
message = ""
data_type = type(data).__name__
if(data_type=="dict"):
    message = json.dumps(data, indent=0)
if(data_type=="list"):
    message = ','.join(data)

print(message)
encoded = Coder.encode(message)
# print(encoded)

# encoded_with_errors = Coder.makeErrors(encoded)
# print(encoded_with_errors)
# Helper.deff_binary(encoded, encoded_with_errors)


decoded = Coder.decode(encoded)
print(decoded)
print(Helper.BinaryToString(decoded))

"""
