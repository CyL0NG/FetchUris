# !/usr/bin/python3.3
# -*- coding: utf-8 -*-  

import os, re
import urllib.request
import http.client
import queue
import GetURLStatus
import threading
import time
#get all uri from target path
#if springSupport = true, get RequestMapping for spring mvc
def GetURIList(targetPath, appDir, website="", uriList=[], springSupport=True):
    if os.path.isdir(targetPath):
        for name in os.listdir(targetPath):
            GetURIList(targetPath + "\\" + name, appDir, website, uriList)
    else:
        fileType = targetPath.split(".")[-1]
        if fileType == "jsp" and targetPath[:8] != "\\WEB-INF":
            #get relative file path
            targetPath = targetPath[len(appDir):]
            #do not append jsp uri in WEB-INF directory
            if targetPath[:8] != "\\WEB-INF":
                #replace \ with /
                targetPath = targetPath.replace("\\", "/")
                #append to uri list
                uriList.append(website + targetPath)
        elif fileType == "java" and springSupport == True:
            #get RequestMapping uri list
            GetRequestMapping(targetPath, website, uriList)
    return uriList

#get RequestMapping annotation for spring mvc
def GetRequestMapping(targetFile, website="", uriList=[], suffix=".do"):
    #RequestMapping Regular Expression Pattern 
    requestMappingPattern = re.compile("^@RequestMapping\\((\\s*value\\s*=\\s*)?\"([^\"]+)\".*\\)")
    #find request mapping in target java code
    with open(targetFile, "r") as javaFile:
        for inlineCode in javaFile.readlines():
            inlineCode = inlineCode.strip()
            if "@RequestMapping" in inlineCode:
                m = requestMappingPattern.match(inlineCode)
                if m:
                    requestMappingUri = m.group(m.lastindex)
                    #remove .ajax, .do suffix
                    if requestMappingUri[-5:] == ".ajax":
                        requestMappingUri = requestMappingUri[:-5]
                    elif requestMappingUri[-3:] == ".do":
                        requestMappingUri = requestMappingUri[:-3]
                    #add /
                    if requestMappingUri[:1] != "/":
                        requestMappingUri = "/" + requestMappingUri
                    #add uri into list with same suffix
                    uriList.append(website + requestMappingUri + suffix)

#show progress
def ShowProgress(current=1, length=100, barWord="="):
    #get current percent
    percent = int(float(current) / float(length) * 100)
    #progress string
    progressStr = "[" + int(percent/2) * barWord + \
        (50-int(percent/2)) * " " + " {0:4d}%]".format(percent)
    #show it
    print("[INFO] " + progressStr, end="\r", flush=True)
    #end with new line
    if current == length:
        print()

#Console information
def Console(msg, msgType="INFO"):
    print("[" + msgType + "] " + msg)

def Main():
    #init parameter
    startTime = time.time()
    targetPath = r"E:\bbs7\trunk\src\Main"
    appDir = r"E:\bbs7\trunk\src\Main\webapp"
    website = "http://v15.pcauto.com.cn"
    threadNum = 20

    #fetch uris!
    Console("Start fetching uris in " + targetPath)
    uriList = GetURIList(targetPath, appDir, website)
    #get unique uri list and uri amount
    uriList = list(set(uriList))
    uriAmount = len(uriList)

    #fetch complete.
    Console("Fetched " + str(uriAmount) + " url(s).")
    #put uris into queque
    urlQueue = queue.Queue()
    for url in uriList:
        urlQueue.put(url)

    #test uris.
    Console("Start testing url status with " + str(threadNum) + " thread(s).")
    #thread init
    condition = threading.Condition()
    threadList = []
    #open file
    resultWriter = open("uri.csv", "w")
    for i in range(threadNum):
        threadList.append( GetURLStatus.GetURLStatus(urlQueue, condition, resultWriter) )
        threadList[i].start()

    while 1:
        #show progress
        currentNum = uriAmount - urlQueue.qsize() - threadNum
        ShowProgress(currentNum, uriAmount)
        #end
        if urlQueue.qsize() == 0:
            for i in range(threadNum):
                if threadList[i].is_alive():
                    time.sleep(3)
            finishTime = time.time()
            elapsedTime = int(finishTime - startTime)
            #100% percent
            ShowProgress(uriAmount, uriAmount)
            Console("Task finished in " + str(elapsedTime) + " seconds.")
            break

if __name__ == "__main__":
    Main()