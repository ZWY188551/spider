#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
"""读取配置文件并进行一定处理"""
import json,re,sys
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')
global path
import os
class Routor(object):
	"""Strategy参数路由"""
	def __init__(self, project,path):
		path=path+'\\xml.xml'
		self.path=path
		route=[]
		self.project=project
		try:
			setting=open(path,'r')
			self.text=setting.read()
		except Exception, e:
			raise IOError('No such setting file in path: %s'%path)
		finally:
			setting.close()
		soup=BeautifulSoup(self.text)
		for p in soup.find_all('project'):
 			if p.get('name')==project:
 				for x in p.find_all('urlpattern'):
 					if x.args.string:
 						arg=x.args.string
 						n=json.loads(arg)
 					else:
 						n=None
 	 				route.append(dict(pattern=x.pattern.string,model=x.model.string,args=n))
 	 			route.append(dict(sleeptime=float(p.get('sleeptime'))))
		self.route=route

	def match(self,url,remove=False,submodel=False):
		route=self.route
		tempR=route
		for x in route[1:-1]:
			r=re.match(x['pattern'],url)
			if r:
				mod=x['model']
				if submodel:
					x['model']=x['args']['submodel']
				else:
					x['model']=mod
				d=dict(model=x['model'],args=x['args'])
				if remove:
					tempR.remove(x)
				else:
					self.route=tempR
					return d
		else:
			return None

	def extractGen(self):
		newRoute=[]
		for x in self.route:
			if x['model'] != 'auto':
				newRoute.append(x)
			else:
				x['model']=x['args']['submodel']
				newRoute.append(x)
		return newRoute

	def setST(self,sleeptime):
		x='([\s\S]*)(<project name='+self.project+'(.*)>)([\s\S]*)'
		r=re.match(x,self.text)
		new='<project name='+self.project+' sleeptime='+str(sleeptime)+'>'
		self.text=self.text.replace(r.group(2),new)
		with open(self.path,'w') as f:
			f.write(self.text)


if __name__ == '__main__':
	r=Routor('yingcai',r'E:\python\PTHL\0.3')
	# r.setST(3)
	t=Routor('yingcai',r'E:\python\PTHL\0.3')
	print t.route[-1]