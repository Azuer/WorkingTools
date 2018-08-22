#!/usr/bin/python
#-*- coding: UTF-8 -*-

import codecs #防止编码问题


def readData(path):
    with codecs.open(path, 'r')as f:
        data = f.read()
    return data

#传入参数为path、content和code，path和code和上述相同，content即为写入的内容，数据类型为字符串。
def writeData(path, mode, content):
    with codecs.open(path, mode) as f:
        f.write(content)
    return True
