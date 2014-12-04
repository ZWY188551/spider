#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests,sys,Route,re,strategy,time,gevent
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

# headers=[]
# headers.append('Mozilla/4.0 (compatible; MSIE 8.0; Windows NT6.0)')
# headers.append('Mozilla/4.0 (compatible; MSIE 7.0; Windows NT5.2)')
# headers.append('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT5.1)')
# headers.append('Mozilla/4.0 (compatible; MSIE 5.0; WindowsNT)')
# headers.append('Mozilla/5.0 (Windows; U; Windows NT 5.2)Gecko/2008070208 Firefox/3.0.1')
# headers.append('Mozilla/5.0 (Windows; U; Windows NT 5.1)Gecko/20070309 Firefox/2.0.0.3')
# headers.append('Mozilla/5.0 (Windows; U; Windows NT 5.1)Gecko/20070803 Firefox/1.5.0.12')
# headers.append('Opera/9.27 (Windows NT 5.2; U; zh-cn)')
# headers.append('Opera/8.0 (Macintosh; PPC Mac OS X; U; en)')
# headers.append('Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en)Opera 8.0')
# headers.append('Mozilla/5.0 (Windows; U; Windows NT 5.2)AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1Safari/525.13')
# headers.append('Mozilla/5.0 (iPhone; U; CPU like Mac OS X)AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93Safari/419.3')
# headers.append('Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML,like Gecko) Chrome/0.2.149.27 Safari/525.13')
# headers.append('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12)Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6')

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

u='http://search.51job.com/job/62602169,c.html'

# r=requests.get(u)

t='''<field name="name" tagname="td" attr={"class":"sr_bt"} />
	<field name="company" tagname="a" attr={"style":"font-size:14px;font-weight:bold;color:#000000;"} />
	<field name="location" tagname="td" attr={"class":"txt_2"} num=1 />
	<field name="last_modified" tagname="td" attr={"class":"txt_2"} num=0 />
	<field name="payment" tagname="td" attr={"class":"txt_2"} num=5 />
	<field name="recruitment" tagname="td" attr={"class":"txt_2"} num=2 />
	<field name="welfare" tagname="td" attr={"class":"sr_bt"} />
	<field name="experience" tagname="td" attr={"class":"txt_2"} num=3 />
	<field name="address" between={"址：":"&lt;"} />
	<field name="require" between={"要求":["&lt;/SPAN&gt;&lt;/SPAN&gt;&lt;/P&gt;","&lt;/div&gt;&lt;/td&gt;"],"资格&lt;br&gt;":"&lt;/div&gt;&lt;/td&gt;"} />
	<field name="description" between={"职责":"&lt;br&gt;&lt;br&gt;","岗位描述":"&lt;/SPAN&gt;&lt;/SPAN&gt;&lt;/P&gt;","描述:":"&lt;/div&gt;&lt;/td&gt;"}>
		<sub name="test" />
	</field>
'''
soup=BeautifulSoup(t)
table=soup.findAll("field")

		
# print 'child',table[0].findNext()

# route={}

# for x in table:
# 	# print x
# 	route[x['name']]=x.__dict__['attrs']
# 	z=x.sub
# 	if z:
# 		# route[x['name']]['sub']=z.__dict__['attrs']
# 		print z.__dict__['attrs']
# 	else:
# 		print  'no sub'

# print table[0]
# print str(table[0]).replace('field','myname')

# print route.get('require').get('sub')

def reformat(text):
	if text==None:
		return None
	text=text.replace('<br>','\n')
	text=text.replace('<BR>','\n')
	
	start=[':','\n','&nbsp;']
	end=['>',':','&nbsp;']

	text=text.strip()
	text=soup=BeautifulSoup(text).text.strip()
	for x in text:
		if x in start:
			text=text.replace(x,'')
	for x in start:
		if text[0] == x:
			text=text[1:]
	if text[-1] in end:
		text=text[:-2]

	return text

s=u'&nbsp;&nbsp;仪器仪表<br>工业<br><br>自动化'
s=s.encode('utf-8')
# print reformat(s)
# r=re.sub(r'[<br>]*','\n',s)
# print 'jieguo ',r.encode('utf-8')
r=re.sub(r'<br><br>|<br>','\n',s)
print 'jieguio',r