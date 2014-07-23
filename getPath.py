# !/usr/bin/python3.3
# -*- coding: utf-8 -*-  

import os, re
import urllib.request
import http.client
#get all uri from target path
#if springSupport = true, get RequestMapping for spring mvc
def getUriList(targetPath, appDir, website="", uriList=[], springSupport=True):
    if os.path.isdir(targetPath):
        for name in os.listdir(targetPath):
            getUriList(targetPath + "\\" + name, appDir, website, uriList)
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
            getRequestMapping(targetPath, website, uriList)
    return uriList

#get RequestMapping annotation for spring mvc
def getRequestMapping(targetFile, website="", uriList=[], suffix=".do"):
    #RequestMapping Regular Expression Pattern 
    requestMappingPattern = re.compile("^@RequestMapping\\((\\s*value\\s*=\\s*)?\"([^\"]+)\".*\\)")
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
                    if requestMappingUri[:1] != "/":
                        requestMappingUri = "/" + requestMappingUri
                    #add uri into list with suffix
                    uriList.append(website + requestMappingUri + suffix)

#get uri status, write result into result.csv
#it needs a lot of time to test every uri.
def getUriStatus(uriList):
    console("Start testing uri status...")
    console("There are " + str(len(uriList)) + " uri(s)!")
    resultList = []
    testNum = 1
    for uri in uriList:
        try:
            response = urllib.request.urlopen(uri)
            resultList.append({"uri" : uri, "status" : response.code})
            console("[" + str(testNum) + "] request: " + uri + ", status: " + str(response.code))
        #unknown status
        except http.client.BadStatusLine as e:
            resultList.append({"uri" : uri, "status" : "unknown"})
            console("[" + str(testNum) + "] request: " + uri + ", status: unknown")
        #other status
        except Exception as e:
            resultList.append({"uri" : uri, "status" : e.code})
            console("[" + str(testNum) + "] request: " + uri + ", status: " + str(e.code))
        #num + 1
        testNum += 1
    #finished!
    console("Test finished!")
    lineFeed = "\n"
    with open("result.csv", "w") as resultFile:
        for result in resultList:
            resultFile.write(result["uri"] + ", " + str(result["status"]) + lineFeed)

#console information
def console(info, infoType="INFO"):
    print(infoType + ": " + info)



if __name__ == "__main__":
    targetPath = r"E:\bbs7\trunk\src\main"
    appDir = r"E:\bbs7\trunk\src\main\webapp"
    website = "http://v15.pcauto.com.cn"

    uriList = getUriList(targetPath, appDir, website)
    getUriStatus(uriList)