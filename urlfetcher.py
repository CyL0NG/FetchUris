#!/usr/bin/python3.3
# -*- coding: utf-8 -*-  
##
# @file urlfetcher.py
# @brief
# @author cylong
# @version 1.0
# @date 2014-11-18

import sys
import os
import re
import time
import argparse
from urldata import UrlData
from javaanalyser import JavaAnalyser
from console import Console
from threadpool import ThreadPool
import requests
#get all url from target path
#if springSupport = true, get RequestMapping for spring mvc
def get_url_list(target_path, app_dir, website=""):
    if os.path.isdir(target_path):
        for name in os.listdir(target_path):
            get_url_list(target_path + "\\" + name, app_dir, website)
    else:
        file_type = target_path.split(".")[-1]
        if file_type == "jsp" and "WEB-INF" not in target_path:

            url_path = target_path
            #get request parameters
            url_params = get_jsp_params(target_path)
            #get relative file path and replace \ with /
            target_path = target_path[len(app_dir):].replace("\\", "/")
            #get real url in test environment
            current_url = website + target_path
            #add into data dict
            url_data.add_info(current_url, "path", url_path)
            url_data.add_info(current_url, "params", url_params)
        elif file_type == "java":
            #get RequestMapping url list
            get_request_mapping(target_path, website)

#analysis parameter in jsp file
#this function is not reliable, it may get parameter from comments.
def get_jsp_params(jsp_file):
    param_list = []
    param_pattern = re.compile(".*(getParameter|param(Long|Int|Double)?)\\(\\s*\"([^\"]+)\".*\\).*")
    source_file = open(jsp_file, 'r')
    inline_code = source_file.readline()
    while inline_code:
        m = param_pattern.match(inline_code)
        if m:
            param_list.append(m.group(m.lastindex))
        inline_code = source_file.readline()
    source_file.close()
    #remove the same parameter
    param_list = list(set(param_list))
    return param_list

#get RequestMapping annotation for spring mvc
def get_request_mapping(target_file, website=""):
    java_analyser = JavaAnalyser(target_file)
    rm_data = java_analyser.get_request_mapping_info()

    for data in rm_data:
        url_data.add_info(website + data["url"], "params", data["params"])
        url_data.add_info(website + data["url"], "path", target_file)
    #release java analyser
    java_analyser.distroy()

def add_parser():
    description = "This script is used for fetch urls from target projecet " \
        + "coded in Java with spring mvc."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-a", dest="app_dir", default="webapp", help="webapp dir, default=webapp")
    parser.add_argument("-p", dest="path", required=True, \
        help="the target java project path")
    parser.add_argument("-w", dest="website", default="", \
        help="the test website of target project, default is \"\"")
    parser.add_argument("-o", dest="output", default="url.csv", \
        help="the file you want to output, default: url.csv")
    parser.add_argument("-e", dest="encoding", default="gbk", \
        help="the file encoding, default: gbk, if error, try utf-8 or others.")
    parser.add_argument("-g", dest="get_status", default=1, \
        help="try to get status and content-type of fetched urls or not, default is 1.")
    parser.add_argument("-t", dest="thread_num", default=20, \
        help="the thead No., default is 20.")
    return parser

def url_request(url):
    #write to global var: url_data
    try:
        response = requests.get(url, timeout=20)
        url_data.add_info(url, "status", str(response.status_code))
        url_data.add_info(url, "content_type", response.headers.get('content-type', ''))
    except requests.exceptions.Timeout:
        url_data.add_info(url, 'status', 'timeout')
        url_data.add_info(url, 'content_type', '')

def main():
    start_time = time.time()
    parser = add_parser()
    args = parser.parse_args()
    app_dir = args.path + "\\" + args.app_dir
    global encoding
    encoding = args.encoding
    #line feed
    line_feed = "\n"
    # use console to show information
    global console
    console = Console()

    console.show("Target Path:      " + args.path)
    console.show("Webapp Directory: " + app_dir)
    console.show("Testing Website:  " + args.website)
    console.show("Output File:      " + args.output)

    # start fetching
    console.show("Start fetching url and its parameters in " + args.path)

    global url_data
    url_data = UrlData()
    get_url_list(args.path, app_dir, args.website)
    url_amount = url_data.len()

    #fetch complete
    console.show("Fetched " + str(url_amount) + " url(s).")
    if args.get_status != 1 or args.website == "":
        url_data.export(args.output)
        #exit
        sys.exit()

    console.show("Start testing url status with " \
            + str(args.thread_num) + " thread(s).")
    #init thread pool
    pool = ThreadPool(args.thread_num)
    
    #init counter
    counter = 0
    for url in url_data.get_urls():
        pool.add_task(url_request, url)
        counter += 1
        console.show_progress(counter, url_amount)
    
    pool.destroy()
    finish_time = time.time()
    elapsed_time = int(finish_time - start_time)
    #export
    url_data.export(args.output)
    console.show("Task finished in " + str(elapsed_time) + " seconds.")

if __name__ == "__main__":
    main()
