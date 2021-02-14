#!/usr/bin/env python3
# coding: utf-8

import os
import pickle
import time

class BinaryFileBuffer:
    def __init__(self, basename):
        self.basename = basename

    @property
    def fname(self):
    # call other function for better inherit-and-overwrite-behaviour
        return self.get_filename()

    def get_filename(self):
        return '{}.bin'.format(self.basename)

    def write(self, data):
        with open(self.fname, 'ba') as f:
            pickle.dump(data, f)

    def write_ts(self, data):
        self.write((time.time(), data))

    @property
    def size(self):
        return int(os.path.isfile(self.fname) \
                and os.path.getsize(self.fname))

    def __iter__(self):
        if self.size > 0:
            try:
                with open(self.fname, 'br') as f:
                    while True:
                        yield pickle.load(f)
            except EOFError:
                return

    def flush(self):
        if self.size > 0:
            os.remove(self.fname)
            
            
            
            
            
class RotatingBinaryFileBuffer(BinaryFileBuffer):
    def get_filename(self):
        # append year and week number to basename ]_[year]_[month][day]_[h]_[m][s].bin
        return '{}_{}.bin'.format( \
                 self.basename, time.strftime('%Y_%m_%d_%H_%M_%S'))