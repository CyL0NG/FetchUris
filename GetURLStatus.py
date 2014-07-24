# !/usr/bin/python3.3
# -*- coding: utf-8 -*-  

import threading
import urllib.request
import http.client

class GetURLStatus(threading.Thread):
	
	def __init__(self, urlQueue, condition, resultWriter):
		threading.Thread.__init__(self)
		self.urlQueue = urlQueue
		self.condition = condition
		self.resultWriter = resultWriter

	def output(self, url, status):
		self.condition.acquire()
		self.resultWriter.write(url + ", " + status + "\n")
		self.condition.release()

	def run(self):
		while self.urlQueue.qsize() > 0:
			self.getStatus(self.urlQueue.get())

	def getStatus(self, url):
		try:
			response = urllib.request.urlopen(url)
			statusDict = {"url": url, "status": str(response.code)}
		except http.client.BadStatusLine as e:
			#this exception always means that your network connection has a problem.
			statusDict = {"url:": url, "status": "unknown"}
		except Exception as e:
			statusDict = {"url": url, "status": str(e.code)}
		self.output(statusDict["url"], statusDict["status"])
