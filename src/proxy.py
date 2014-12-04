#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
"""代理池"""
import requests,threading,time

path=r'E:\python\PTHL\0.2\ip.txt'

class ProxyPool(object):
	"""代理池类"""
	def __init__(self):
		self.path=path
		self.content=self.getAll()
		self.pool=list(set(self.getAll()))
		self.curse=self.getOne()
		self.ips=self.pool
	def getAll(self):
		with open(self.path) as f:
			return f.read().strip().split('\n')
	def getOne(self):
		for x in self.pool:
			if x==self.pool[-1]:
				print 'LAST'
			yield x
	def write(self,list):
		w=''
		for x in list:
			w+=x+'\n'
		with open(path,'w') as f:
			f.write(w.strip())
		print w
	def flush(self):
		lock=threading.lock()
		while True:
			lock.acquire()
			try:
				proxy=self.curse.next()
				proxies = {"http": 'http://'+proxy}
			except StopIteration:
				print 'not available'
				break
			try:
				r=requests.get('http://www.baidu.com',proxies=proxies,timeout=5)
			except:
				self.ips.remove(proxy)
				print proxy+' Can`t connect!'+' No.'+str(self.content.index(proxy))
				continue
			print r.content
		self.write(self.ips)
	def scan(self,url,headers,timeout=15):
		t=time.time()
		while True:
			if time.time()-t<timeout:
				try:
					proxy=self.curse.next()
					proxies = {"http": 'http://'+proxy}
				except StopIteration:
					return None
				try:
					r=requests.get(url,headers=headers,proxies=proxies,timeout=5)
				except:
					continue
				return r
			else:
				return None

if __name__ == '__main__':
	p=ProxyPool()
	# print p.scan('http://www.baidu.com',u'百度')
	for x in xrange(1,30):
		t=threading.Thread(target=p.flush)
		t.start()
