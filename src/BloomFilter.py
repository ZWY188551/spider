#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
import BitVector,time
"""用于URL查重"""
class SimpleHash():    
      
	def __init__(self, cap, seed):  
		self.cap = cap  
		self.seed = seed  
      
	def hash(self, value):  
		ret =1
		for i in range(len(value)):  
			ret += self.seed*ret + ord(value[i])
		return (self.cap-1) & ret      
  
class BloomFilter():  
      
	def __init__(self, BIT_SIZE=1<<27):  
		self.BIT_SIZE = BIT_SIZE  
		self.seeds = [2, 3, 5, 7, 11, 13, 17]
		x=[5,7, 11, 13,31, 37, 61]   
		self.bitset = BitVector.BitVector(size=self.BIT_SIZE)  
		self.hashFunc = []  
		for i in range(len(self.seeds)):  
			self.hashFunc.append(SimpleHash(self.BIT_SIZE, self.seeds[i]))  
          
	def insert(self, value):  
		for f in self.hashFunc:  
			loc = f.hash(value)
			self.bitset[loc] = 1  
	def isContain(self, value):  
		if value == None:  
			return False  
		ret = True  
		for f in self.hashFunc:  
			loc = f.hash(value)  
			ret = ret & self.bitset[loc]  
		return ret  

if __name__ == '__main__':
	t1=time.time()
	bf=BloomFilter(BIT_SIZE=1<<27)
	print u'create-time= ',time.time()-t1
	url1=u'http://company.zhaopin.com/CC495095924.htm'
	url2=u'http://company.zhaopin.com/CC629615427.htm'
	bf.insert(url1)
	t2=time.time()
	bf.insert(url1)
	print u'insert-time= ',time.time()-t2
	t3=time.time()
	n=bf.isContain(url2)
	print u'search-time= ',time.time()-t3
	print n