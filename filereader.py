#!/usr/bin/python
# -*- coding: utf-8 -*-  
##
# @file filereader.py
# @brief
# @author cylong
# @version 1.0
# @date 2014-11-18

class FileReader():
    def __init__(self, file_path, encoding="gbk"):
        self.file_handler = open(file_path, "r")
        self.file_path = file_path
        self.encoding = encoding
        self.init_encoding = encoding
        self.error = 0

    def readline(self):
        return self.file_handler.readline()

    def close(self):
        self.file_handler.close()

