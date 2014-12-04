#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
"""for deal with needed content"""
"""
common
      name: 标题
      address：地址
      description：描述|job：工作内容；company：公司介绍
      contact：联系方式
      homepage：公司主页
      category：标记job or company
      url：原始信息链接
      last_modified：最后修改（添加）时间|发布日期
      kind：类别|job：全职、兼职、实习等；company：国营、私营、外企等
      email：招聘 or 公司 电子邮箱
      welfare: 福利
for jobs
      require：职位需求
      payment：薪资
      location: 工作地点
      recruitment：招聘人数
      experience：工作经验
      degree：最低学历
      company: 招聘公司
for companies
      scale：公司规模
      industry：所属行业
      addcode: 邮政编码
"""
import requests,sys,re,json
from bs4 import BeautifulSoup
# reload(sys)
# sys.setdefaultencoding('gb18030')

_string=["name","address","description","contact","homepage","category",
"url","last_modified","kind","email","welfare","require","payment","location",
"recruitment","experience","degree","company","scale","industry"]

def deal(name,cat,path,solr):
	with open(path+'\schema.xml') as f:
		t=f.read()
	tab=BeautifulSoup(t).find('schema',project=name)
	table=tab.find(cat).findAll("field")
	return Content(table,cat,solr)

class Content(object):
	"""docstring for Content"""
	def __init__(self,tab,cat,solr):
		# if text.find('charset=gb2312'):
		# 	reload(sys)
		# 	sys.setdefaultencoding('gb18030')
		# self.text=text.encode('utf-8')
		reload(sys)
		sys.setdefaultencoding('utf-8')	
		self.url=''
		self.solr=solr
		self.cat=cat
		self.route={}
		for x in tab:
			self.route[x['name']]=x.__dict__['attrs']
			z=x.sub
			if z:
				self.route[x['name']]['sub']=z.__dict__['attrs']
	
	@property
	def txt(self):
		return self.text
	@txt.setter
	def txt(self,value):
		if value.find('charset=gb2312'):
			# reload(sys)
			# sys.setdefaultencoding('gb18030')
			value=value.decode('gb18030')
		self.text=value.encode('utf-8')
		# reload(sys)
		# sys.setdefaultencoding('utf-8')
		self.soup=BeautifulSoup(self.text,from_encoding='utf-8')		

	def getWelfare(self):
		lis = self.soup.findAll('span',"Welfare_label")
		x=''
		for w in lis:
			x+=w.string.encode('utf-8')+'+'
		return x[:-1]

	# def common(self,tagname,num=0,**kw):
	# 	try:
	# 		return self.soup.findAll(tagname,kw)[num].string.encode('utf-8')
	# 	except:
	# 		return None

	def get(self,name):
		route=self.route[name]
		if route.get('sub'):
			t=doGetText(self.text,route)
			r=doGetText(t,route['sub'])
		else:
			r=doGetText(self.text,route)
		if r:
			return reformat(r)

	def assemble(self,op):
		result=''
		if op=='update':
			result+='<add>\n<doc>\n'
			result+='<field name="url">'+self.url+'</field>\n'
			result+='<field name="category">'+self.cat+'</field>\n'
			for v in self.route:
				if self.get(v):
					result+='<field name="'+v+'">'+self.get(v)+'</field>\n'
			result+='</doc>\n</add>\n'
			return op,result.encode('utf-8')

	def send(self,op): 
		headers={'content-type': 'text/xml'}
		stri=self.assemble(op)
		r=requests.post(self.solr+'/'+stri[0],data=stri[1],headers=headers)
		r=requests.post(self.solr+'/'+stri[0],data='<commit />',headers=headers)
		return stri[1],r.content

def doGetText(text,route):
	if route.get('between'):
		return extract(text,route['between'])
	else:
		return common(text,route)

def common(text,kw):
	soup=BeautifulSoup(text)
	try:
		tag=kw['tagname']
		attr=json.loads(kw['attr'])
		if kw.get('num'):
			num=int(kw['num'])
		else:
			num=0
		return str(soup.findAll(tag,attr)[num])
	except:
		return None

def extract(text,between):	
	between=json.loads(between,encoding="utf-8")
	for k,v in between.iteritems():
		if isinstance(v,list):
			m=len(text)
			z=None
			for y in v:
				t=getContent(text,[k,y])
				if t:
					l=len(t)
					if m>l:
						m=l
						z=t
			return z
		else:
			t=getContent(text,[k,v])
		if t:
			return t

def reformat(text):
	if text==None:
		return None

	text=re.sub(r'<br><br>|<br>','\n',text)
	text=re.sub(r'<BR><BR>|<BR>','\n',text)
	
	start=[':','\n','：']
	end=['>',':']

	text=text.strip()
	text=soup=BeautifulSoup(text).text.strip()
	for x in text:
		if x in start:
			text=text.replace(x,'')
		else:
			break
	for x in xrange(1,len(text)+1):
		j=text[-x]
		if j in end:
			text=text.replace(j,'')
		else:
			break
	return text.strip()

def getContent(text,loc):
	start=loc[0]
	end=loc[1]
	n=0
	if start and end:
		pattern=r'([\s\S]*)'+start+r'([\s\S]*?)'+end+r'([\s\S]*)'
		n=2
	elif start=='':
		pattern=r'([\s\S]*?)'+end+r'([\s\S]*)'
		n=1
	elif end=='':
		pattern=r'([\s\S]*?)'+start+r'([\s\S]*)'
		n=2
	pattern=str(pattern)
	m=re.match(pattern,text)
	if m:
		return m.group(n).encode('utf-8')
	else:
		return None

if __name__ == '__main__':
	r=requests.get('http://search.51job.com/job/65878894,c.html')
	# x=requests.get('http://search.51job.com/list/co,c,3322339,000000,10,1.html')

	s=deal('51job','job',r'E:\python\PTHL\0.3','http://localhost:8080/solr/spider')
	s.txt=r.content
	# print s.assemble('update')
	# print 'hangye =',s.get('industry')
	print s.send('update')[0]
	# print 'miaoshu',s.get('description')
	