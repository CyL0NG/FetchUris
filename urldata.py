#!/usr/bin/python3.3
# -*- coding: utf-8 -*-  
##
# @file url_data.py
# @brief
# @author cylong
# @version 1.0
# @date 2014-11-18


class UrlData():
    def __init__(self, site=""):
        self.data = {}
        self.site = site
            
    def url_init(self, url):
        if not self.data.get(url):
            self.data[url] = {"status": "", "params": [], "path": "", \
                "content_type": ""}

    def add_info(self, url, attrib, value):
        self.url_init(url)
        self.data[url][attrib] = value

    def export(self, output):
        line_feed = "\n"
        with open(output, "w") as o_file:
            result = "url,params,status,content_type,path,request_type,privilege,risk,level,comment" + line_feed
            o_file.write(result)
            for url in self.data.keys():
                param_str = "\n".join(self.data[url]["params"])
                result = url + ",\"" + param_str + "\"," + self.data[url].get("status") + "," + \
                    self.data[url].get("content_type") + "," + self.data[url].get("path") + ", , , , ," + line_feed
                o_file.write(result)

    def get_urls(self):
        return list(self.data.keys())

    def len(self):
        return len(self.data)
