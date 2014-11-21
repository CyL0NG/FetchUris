#! /usr/bin/python
# -*- coding: utf-8 -*-
##
# support both python 2 and python 3
# @file console.py
# @author cylong
# @version 1.0
# @date 2014-11-18
from __future__ import print_function
import platform
import ctypes
import sys

class Console(object):

    def __init__(self):
        #init progress
        self._current = 0
        #windows or linux
        if platform.system() == "Windows":
            self._platform = "windows"
            self._color = {'danger': { 'color': 0x0c, 'symbol': '-'},  # red
                    'warning': { 'color': 0x0e, 'symbol': '-'},  # yellow
                    'success': { 'color': 0x0a, 'symbol': '+'},  # green
                    'info': {'color': 0x0f, 'symbol': '*'}   # white
                    }
            self._handler = ctypes.windll.kernel32.GetStdHandle(-11)
            self._process = self.__print_Windows
        else:
            self._color = {'danger': {'color': '\033[22;31m', 'symbol': '-'},  # red
                    'warning': {'color': '\033[01;33m', 'symbol': '-'},  # yellow
                    'success': {'color': '\033[22;32m', 'symbol': '+'},  # green
                    'info': {'color': '\033[01;37m', 'symbol': '*'},  # white
                    'default': {'color': '\033[0m', 'symbol': ''}  # default
                    }
            self._process = self.__print_Linux
            
    def __print_Windows(self, msg, type):
        # set console color
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._handler, \
                self._color[type]['color'])
        print('[%s] %s' % (self._color[type]['symbol'], msg))
        # reset color
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._handler, \
                self._color['info']['color'])

    def __print_Linux(self, msg, type):
        print('[%s] %s%s%s' % (self._color[type]['symbol'], \
                self._color[type]['color'], msg, \
                self._color['default']['color']))

    def show(self, msg):
        self._process(msg, 'info')
    
    def show_info(self, msg):
        self.show(msg)

    def show_warning(self, msg):
        self._process(msg, 'warning')

    def show_danger(self, msg):
        self._process(msg, 'danger')

    def show_success(self, msg):
        self._process(msg, 'success')

    def show_progress(self, currentNum, length=100):
        percent = int(float(currentNum) / float(length) * 100)
        if percent == self._current:
            return
        else:
            self._current = percent
            progress_str = '\r[*] [%s%s%4s%%]' % (int(percent / 2) * '=', \
                    (50 - int(percent / 2)) * ' ', \
                    percent)
            print(progress_str, end="")
            sys.stdout.flush()

        if currentNum == length:
            print()

