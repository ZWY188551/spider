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
	return Content(table,solr)

class Content(object):
	"""docstring for Content"""
	def __init__(self,cat,solr):
		# if text.find('charset=gb2312'):
		# 	reload(sys)
		# 	sys.setdefaultencoding('gb18030')
		# self.text=text.encode('utf-8')
		reload(sys)
		sys.setdefaultencoding('utf-8')	
		self.url=''
		self.solr=solr
		self.route={}
		for x in cat:
			self.route[x['name']]=x.__dict__['attrs']
	
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

	def getDegree(self):
		pass

	def getScale(self):
		pass

	def getIndustry(self):
		pass

	def common(self,tagname,num=0,**kw):
		try:
			return self.soup.findAll(tagname,kw)[num].string.encode('utf-8')
		except:
			return None

	def extract(self,between):
		print between		
		between=json.loads(between,encoding="utf-8")
		for k,v in between.iteritems():
			if isinstance(v,list):
				m=0
				z=None
				for y in v:
					t=getContent(self.text,[k.encode('utf-8'),y.encode('utf-8')])
					if t:
						print t
						l=len(t)
						if m<l:
							m=l
							z=t
				return reformat(z)
			else:
				t=getContent(self.text,[k.encode('utf-8'),v.encode('utf-8')])
			if t:
				x=reformat(t)
				return x

	def get(self,name):
		route=self.route[name]
		if route.get('between'):
			return self.extract(route['between'])
		else:
			tagname=route['tagname']
			kw=json.loads(route['attr'])
			if route.get('num'):
				num=int(route['num'])
			else:
				num=0
			return self.common(tagname,num=num,**kw)

	def assemble(self,op):
		result=''
		if op=='update':
			result+='<add>\n<doc>\n'
			result+='<field name="url">'+self.url+'</field>\n'
			for v in self.route:
				if self.get(v):
					result+='<field name="'+v+'">'+self.get(v)+'</field>\n'
			result+='</doc>\n</add>\n'
			return result.encode('utf-8')

	def send(self,str): 
		headers={'content-type': 'text/xml'}
		# r=requests.post(self.solr+'/update',data=str,headers=headers)
		# return r.content
		return str

def reformat(text):
	
	text=text.replace('<br>','\n')
	text=text.replace('<BR>','\n')
	
	start=[':','\n']
	end=['>',':']

	text=text.strip()
	text=soup=BeautifulSoup(text).text
	for x in start:
		if text[0] == x:
			text=text[1:]
	if text[-1] in end:
		text=text[:-2]

	return text

def getContent(text,loc):
	start=loc[0]
	end=loc[1]
	print 'loc = ',loc
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
	m=re.match(pattern,text)
	if m:
		return m.group(n).encode('utf-8')
	else:
		return None

if __name__ == '__main__':
	r=requests.get('http://search.51job.com/job/62602169,c.html')
	x=requests.get('http://search.51job.com/list/co,c,3322339,000000,10,1.html')
	# c=Content('51job',x.content)
	# print 'name: ',c.getName()
	# print 'company: ',c.getCompany()
	# print 'location: ',c.getLoc()
	# print 'last_modified: ',c.getLM()
	# print 'pay: ',c.getPay()
	# print 'recruitment: ',c.getRecruit()
	# print 'welfare: ',c.getWelfare()
	# print 'exp: ',c.getExp()
	# print 'address: ',c.getAddress()
	# print 'require：',c.getRequire()
	# print 'description：',c.getDesciption()
	# d={'class':"sr_bt"}
	# print 'common test: ',c.common('td',**d)
	# print c.get('name')

	s=deal('51job','job',r'E:\python\PTHL\0.3','')
	s.txt=r.content
	# # print s.get('payment')
	# # print s.assemble('update')
	# t=BeautifulSoup(r.content.decode('gb18030'))
	# print t.findAll("td","txt_1")[-3].nextSibling.string
	# # print getContent(r.content.decode('gb18030'),['薪水范围：','</td>'])
	# print s.route['payment']

	print s.assemble('update')

	tt='''要求：</td><td class="txt_2 ">普通话</td><td class="txt_1" width="12%">学&nbsp;&nbsp;&nbsp;&nbsp;历：</td><td class="txt_2 ">大专</td><td class="txt_1" width="12%">薪水范围：</td><td class="txt_2 ">面议</td></tr><tr><td colspan="6" style="width:100%;height:1px;line-height:1px;" class="txt_1 job_detail">&nbsp;</td></tr>
						<tr>
							<td colspan="6" style="width:100%" class="job_detail">
							<strong>职位职能:</strong>&nbsp;&nbsp;收银主管/收银员&nbsp;&nbsp;
							</td>
						</tr>
				<tr>
					<td colspan="6" style="width:100%" class="txt_4 wordBreakNormal job_detail ">
					<strong>职位描述:</strong><br/>
					<div style="padding-bottom:30px;"><p>要求女，相貌端正，身高1.62以上，工作认真，有收银经验。</p><p><br></p><br></div></td>
				</tr>
				<tr>

'''
	# print getContent(tt,['要求','</div></td>'])