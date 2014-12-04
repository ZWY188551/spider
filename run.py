#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='Alexis Zhang'
"""程序入口"""
import os
from src.strategy import Strategy
from gevent import monkey
from bs4 import BeautifulSoup
monkey.patch_all()
import gevent
path=os.path.abspath('.')

def run():
	with open('settings.xml') as f:
		t=f.read()
	lst=[]
	soup=BeautifulSoup(t)
	lis=soup.list.findAll('project')

	solr_path = soup.find('solr').__dict__['attrs']['path']

	for x in lis:
		atr=x.__dict__['attrs']
		if atr['test']=="false" or atr['test']=="False":
			i=False
		else:
			i=True
		s=Strategy(atr['name'],path=path,switch=i,solr=solr_path)
		for x in xrange(0,int(atr['thread'])):
			lst.append(gevent.spawn(s.core))
	
	gevent.joinall(lst)

if __name__ == '__main__':
	run()