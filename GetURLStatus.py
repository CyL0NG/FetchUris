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

	def console(self, url, status, msgType="INFO"):
		self.condition.acquire()
		print("[" + msgType + "]" + " url: " + url + ", status: " + status)
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
			statusDict = {"url:": url, "status": "unknown"}
		except Exception as e:
			statusDict = {"url": url, "status": str(e.code)}
		self.console(statusDict["url"], statusDict["status"])
