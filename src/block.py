#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
"""链接时间间隔检测模块"""

class SleepTime(object):
	"""docstring for SleepTime"""
	def __init__(self,sleeptime):
		self.switch=False
		self.sleeptime=sleeptime
		self.flag=0
		self.ran=[sleeptime,0]
		self.K=0.01
	def isBlocked(self,fail):
		if self.switch:
			return self.sleeptime
		print self.sleeptime,self.ran,fail>=10,fail
		if self.sleeptime<self.ran[1]:
			self.ran[0]=self.ran[1]
			self.ran[1]=self.sleeptime
		elif self.sleeptime<self.ran[0]:
			self.ran[1]=self.sleeptime
		# if sleeptime>ran[0]:			
		if fail>=2:
			print 'block happen'
			self.flag+=1
			if self.flag==1:
				self.ran[1]=(self.ran[0]+self.ran[1])/2.0
			self.sleeptime=self.ran[0]+self.flag
			print self.sleeptime
			return self.sleeptime
		else:
			if self.sleeptime<=self.K and self.sleeptime:
				self.sleeptime=0
				self.switch=True
				print 'get final time'
				return 0,True
			if (self.ran[0]-self.ran[1])<=self.K:
				self.sleeptime=(self.ran[0]+self.ran[1])/2.0
				self.switch=True
				print 'get final time'
				return self.sleeptime,True
			if self.flag==0:
				self.sleeptime=self.ran[1]/2.0
			else:
				self.sleeptime=(self.ran[0]+self.ran[1])/2.0
			self.flag=0
			return self.sleeptime	

if __name__ == '__main__':
	import random,time
	s=SleepTime(10)
	while True:
		n=random.randint(0,30)
		x=s.isBlocked(n)
		time.sleep(s.sleeptime)
		print 'st=',str(x),'   randint=',str(n)
	print  u'Finally sleeptime = ',s.isBlocked(random.randint(0,30))