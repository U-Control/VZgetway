'''
Created on 2 Jun 2020

@author: USER
'''
from ThingBoardConection.BinaryFileBuffer import   RotatingBinaryFileBuffer

from random import randint
def randstr(strlen):
    # include only printable characters
    return ''.join(chr(randint(32, 126)) for i in range(strlen))
buf = RotatingBinaryFileBuffer('data')
buf.write_ts(randstr(60))
for item in buf:
    print(item)
buflen = max(i for i,_ in enumerate(buf)) + 1
print("\nBytes per entry: {}".format(buf.size/buflen))