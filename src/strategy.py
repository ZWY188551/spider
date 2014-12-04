#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
"""单一网站的处理策略"""
import logging,Queue,requests,re,time,sys,os
from bs4 import BeautifulSoup
from BloomFilter import BloomFilter
from Route import Routor
from proxy import ProxyPool
from block import SleepTime
from deal import deal
reload(sys)
sys.setdefaultencoding('utf-8')
"""logging设置"""

"""全局参数"""
count=0
# proxyPool=ProxyPool()


class Strategy(object):
	"""爬取策略"""
	def __init__(self, name,path,switch=False,solr=None):
		self.name=name
		self.switch=switch
		self.path=path+'\logs\\'+self.name
		if not os.path.exists(path+'\logs'):
			os.mkdir(path+'\logs')
		if not os.path.exists(self.path):
			os.mkdir(self.path)
		self.routor=Routor(name,path)
		self.queue=Queue.Queue(maxsize=0)
		self.failQueue=Queue.Queue(maxsize=0)#失败队列
		self.logger=self.newLogging(name)
		self.bloomfilter=BloomFilter()
		self.count=0
		self.queue.put(self.routor.route[0]['pattern'])
		self.sleeptime=self.routor.route[-1]['sleeptime']
		self.block=SleepTime(self.sleeptime)#屏蔽模块
		self.fail=0
		self.job=deal(name,'job',path,solr)
		self.company=deal(name,'company',path,solr)

	def newLogging(self,name):
		logger = logging.getLogger(name)
		logger.setLevel(logging.DEBUG)
		# 创建一个handler，用于写入日志文件
		fh = logging.FileHandler(self.path+'\\'+name+'.log')
		fh.setLevel(logging.DEBUG)
		# 再创建一个handler，用于输出到控制台
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		# 定义handler的输出格式
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		# 给logger添加handler
		logger.addHandler(fh)
		logger.addHandler(ch)
		return logger
	"""功能函数包装"""
	def link_and_check(func):
		def _wrapper(*args,**kw):
			url=unicode(args[1])
			headers ={'Accept':'text/html;q=0.9,*/*;q=0.8','Accept-Charset':'ISO-8859-1,utf-8,gb2312;q=0.7,*;q=0.3','Accept-Encoding':'gzip','Connection':'close','Referer':None}
			headers['User-Agent']=getHeader()
			#注意如果依然不能抓取的话，Referer可以设置抓取网站的host
			try:
				try:
					req=requests.get(url,timeout=5,headers=headers)
				except Exception as e:
					raise FailException(args[0],'bad requests:'+str(type(e))[8:])
				if req:
					if req.content:
						kw['content']=req.content
						return func(*args,**kw)
				else:
					args[0].logger.warning('No Content in URL: %s'%url)
					raise FailException(args[0],'No Content in URL')
			except FailException as e:
				args[0].logger.warning('URL: %s | info: %s'%(url,e.info))
				args[0].logger.warning('fail: %s | Stime: %s'%(args[0].fail,args[0].sleeptime))
				if args[0].switch:
					print 'put in failQueue'
					args[0].failQueue.put(url)
			finally:
				if args[0].switch:
					tim=args[0].block.isBlocked(args[0].fail)
					if isinstance(tim,tuple):
						if tim[1]:
							#学习停止
							args[0].switch=False
							args[0].routor.setST(tim[0])
							tim=tim[0]
					args[0].sleeptime=tim
					print args[0].sleeptime
					if args[0].fail==0 or not args[0].switch:
						if not args[0].failQueue.empty():
							for x in range(args[0].failQueue.qsize()):
								u=args[0].failQueue.get()
								args[0].queue.put(u)
		return _wrapper
	"""功能函数"""
	@link_and_check
	def enter(self,url,**kw):
		#处理需要进入并且获取网页指定区域子连接的URL
		text=kw['content']
		area=self.getArea(text,kw['loc'])
		linklist=self.getAllAch(area)
		for link in linklist:
			if not self.bloomfilter.isContain(link):
				self.queue.put(link)
				self.bloomfilter.insert(link)
		self.fail=0

	@link_and_check
	def need(self,url,**kw):
		#处理目标页面的文本信息，直接下载到本地
		text=kw['content']
		if kw['ctg']=='job':
			filename='\job_save.log'
			self.job.txt=text
			self.job.url=url
			forsave= self.job.send('update')[0]
		else:
			filename='\company_save.log'
			self.company.txt=text
			self.company.url=url
			forsave= self.company.send('update')[0]
		with open(self.path+filename,'a') as f:
			f.write(forsave)

		self.fail=0


	def auto(self,url,**kw):
		#处理需要调用URLgenerator的URL
		self.logger.warning('BEGIN USING ATUO generator!')
		self.routor.match(url,submodel=True)
		if len(kw['replace'])==2:
			replace=[str(n) for n in xrange(kw['replace'][0],kw['replace'][1])]
		else:
			replace=kw['replace']

		for x in replace:
			u=urlGenerator(url,kw['between'],x)
			if not self.bloomfilter.isContain(u):
				self.distributor(u)
				self.bloomfilter.insert(u)
		self.routor.match(url,submodel=False)
				
	"""策略核心"""
	def core(self):
		ti=time.time()
		isFinish=False #退出判定
		t=time.time()-ti #计时退出

		# try:
		# 	while not isFinish:
		# 	# size=self.queue.qsize()
		# 	# self.logger.info('before get url, Queue size = %s'%size)
		# 		url=self.queue.get()
		# 		self.distributor(url)
		# 		t=time.time()-ti
		# 		if t>3600:
		# 			isFinish=True
		# 			print 'COUNTE = ',self.count
		# 			self.logger.info('COUNT = %s'%self.count)
		# except:
		# 	print 'FINISH ! In Time:',t
		# 	print self.queue.qsize()
		# 	self.logger.info('FINISH ! In Time: %s'%t)

		while not isFinish:
			url=self.queue.get()
			self.distributor(url)

			#退出机制，测试用
			# t=time.time()-ti
			# if t>3600:
			# 	isFinish=True
			# 	print 'COUNTE = ',self.count
			# 	self.logger.info('COUNT = %s'%self.count)

		print 'FINISH ! In Time:',t
		print self.queue.qsize()
		self.logger.info('FINISH ! In Time: %s'%t)

	def distributor(self,url):
		#分发链接
		afterRoute=self.routor.match(url)
		if afterRoute:
			self.count+=1
			self.logger.info('%s: %s'%(afterRoute['model'],url))
			if afterRoute['model']=='enter':
				self.enter(url,**afterRoute['args'])
			elif afterRoute['model']=='need':
				self.need(url,**afterRoute['args'])
			elif afterRoute['model']=='auto':
				self.auto(url,**afterRoute['args'])
			# time.sleep(self.sleeptime)
		else:
			self.logger.warning('URL: %s is not found in Pattern !'%url)

	"""工具方法"""
	def getArea(self,text,loc):
		#获取指定文本之间的文本
		for k,v in loc.iteritems():
			l=[k,v]
			t=getContent(text,l)
			if t:
				return t
		print text
		raise FailException(self,'No Area is Done')

	def getAllAch(self,text):
		#获取指定文本中的链接，并查重，返回list
		soup=BeautifulSoup(text)
		linklist=[link.get('href') for link in soup.find_all('a')]
		if len(linklist)==0:
			raise FailException(self,'No link in content')
		legallink=[]
		for link in linklist:
			link=str(link)
			if re.match(r'http://.*',link):
				legallink.append(link)
		linklist=legallink
		for script in soup.find_all('script'):
			scr=str(script)
			r=re.findall(r'"http://.*?"',scr)
			for sc in r:
				if sc:
					rs=re.search(r'"http://.*?"',sc)
					if rs:
						l=rs.group().replace('"','')
						linklist.append(l)
		return linklist

def urlGenerator(url,between,replace):
	st=between[0]
	en=between[1]
	#loop
	# try:
	if st and en:
		restr='(.*)'+st+'(.*)'+en+'(.*)'
		rem=re.match(restr,url)
		loc1=rem.group(1)+st
		loc2=en+rem.group(3)
		fin=loc1+replace+loc2
	elif en=='':
		restr='(.*)'+st+'(.*)'
		rem=re.match(restr,url)
		loc1=rem.group(1)+st
		fin=loc1+replace
	# except Exception, e:
	# 	raise AttributeError('AUTO has NO SUCH Attribute,cannot match them !')
	#loop
	return fin

def getContent(text,loc):
	start=loc[0]
	end=loc[1]
	n=0
	if start and end:
		pattern=r'([\s\S]*?)'+start+r'([\s\S]*?)'+end+r'([\s\S]*)'
		n=2
	elif start=='':
		pattern=r'([\s\S]*?)'+end+r'([\s\S]*)'
		n=1
	elif end=='':
		pattern=r'([\s\S]*?)'+start+r'([\s\S]*)'
		n=2
	m=re.match(pattern,text)
	if m:
		return m.group(n)
	else:
		return None

headers=[
	'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
	'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT6.0)',
	'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT5.2)',
	'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT5.1)',
	'Mozilla/4.0 (compatible; MSIE 5.0; WindowsNT)',
	'Mozilla/5.0 (Windows; U; Windows NT 5.2)Gecko/2008070208 Firefox/3.0.1',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1)Gecko/20070309 Firefox/2.0.0.3',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1)Gecko/20070803 Firefox/1.5.0.12',
	'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
	'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
	'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en)Opera 8.0',
	'Mozilla/5.0 (Windows; U; Windows NT 5.2)AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1Safari/525.13',
	'Mozilla/5.0 (iPhone; U; CPU like Mac OS X)AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93Safari/419.3',
	'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML,like Gecko) Chrome/0.2.149.27 Safari/525.13',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12)Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6'
]

def getHeader():
	import random
	return headers[random.randint(0,len(headers)-1)]

"""异常处理"""
class FailException(Exception):#链接访问异常
	"""docstring for FailException"""
	def __init__(self,cls,info):
		super(Exception, self).__init__()
		cls.fail += 1
		self.info=info
		

if __name__ == '__main__':
	import threading
	from gevent import monkey; monkey.patch_all()
	import gevent
	job51=Strategy('51job',switch=True,path=r'E:\python\PTHL\0.3')
	# job51.core()
	lis=[]
	for x in xrange(0,10):
		lis.append(gevent.spawn(job51.core))
		# lis.append(gevent.spawn(zhaopin.core))
	# lis.append(gevent.spawn(yingcai.core))
	gevent.joinall(lis)
	# job51.core()


	# path='E:\python\PTHL\0.3'
	# # s=Strategy(k,path=path)
	# r=requests.get('http://search.51job.com/job/65687954,c.html')
	# s=deal('51job','job',r'E:\python\PTHL\0.3')
	# s.txt=r.content
	# # print s.get('description')
	# print s.assemble('update')