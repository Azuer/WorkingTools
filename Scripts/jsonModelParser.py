#!/usr/bin/python
#-*- coding: UTF-8 -*-
import os
import sys
import json
import time
import Queue
import string
import getopt
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class JsonModelParser(object):
    """docstring for JsonModelParser"""
    def __init__(self, filePath, prefix_format):
        super(JsonModelParser, self).__init__()
        self.filePath = filePath
        self.queue = Queue.Queue()
        self.bodyList = []
        self.prefix_format = prefix_format
        self.suffix = 'VO'
    def parseJson(self):
        if os.path.isfile(self.filePath):
            input = open(self.filePath, 'r')
        try:
            res = json.loads(input.read(), encoding='utf-8')#eval(input.read())
            data = res['data']
            if len(self.prefix_format) == 0:
                self.queue.put(('data', data))
                self.traverseJsonModel()
            else:
                rootKey = self.capitalize(self.prefix_format)
                self.queue.put((rootKey, data))
                self.test()
        finally:
            input.close()

    def traverseJsonModel(self):
        while not self.queue.empty():
            name, data = self.queue.get()
            if isinstance(data, dict) and len(data) > 0: 
                group = []
                for (key, value) in data.items():
                    # self.printType(key, value)
                    group.append(self.getOCProperty(key, value))
                    prefix = name + " -> " + key if len(name) > 0 else key
                    if isinstance(value, dict):
                        self.queue.put((prefix ,value))
                    elif isinstance(value, list) and len(value) > 0:
                        self.queue.put((prefix, value[0]))
                    elif isinstance(value, unicode):
                        pass
                self.bodyList.append((name, group))
            elif isinstance(data, list) and len(data) > 0:
                self.queue.put((name, data[0]))

        self.genereteFiles()

    def test(self):
        while not self.queue.empty():
            name, data = self.queue.get()
            if isinstance(data, dict) and len(data) > 0: 
                group = []
                refs = []
                for (key, value) in data.items():
                    prop = self.getOCProperty(key, value)
                    subVal = value 
                    if isinstance(value, dict):
                        prop = self.getSubVOProperty(name, key, value)
                        refs.append(self.getSubVOName(name, key))
                        self.queue.put((name+self.capitalize(key) ,subVal))
                    elif isinstance(value, list) and len(value) > 0:
                        prop = self.getSubVOProperty(name, key, value)
                        refs.append(self.getSubVOName(name, key))
                        subVal = value[0]
                        self.queue.put((name+self.capitalize(key), subVal))
                    elif isinstance(value, unicode):
                        pass
                    group.append(prop)
                self.bodyList.append((name, group, refs))
            elif isinstance(data, list) and len(data) > 0:
                self.queue.put((name, data[0]))

        self.genereteVOs()

    def getSubVOProperty(self, key, subKey, value):
        voName = self.getSubVOName(key, subKey)
        if isinstance(value, list):
            voName =  'NSArray<' + voName + ' *>'
        return (subKey, voName)
            
    def getSubVOName(self, key, subKey):
        return self.capitalize(key) + self.capitalize(subKey) + self.suffix
    def printType(self, key, value):
        if isinstance(value, str):
            if self.isNumber(value):
                print key + " : NSNumber"
            else :
                print key + " : NSString"
        elif isinstance(value, (int, float)):
            print key + " : NSNumber"
        elif isinstance(value, list):
            print key + " : NSArray"
        elif isinstance(value, dict):
            print key + " : NSDictionary"
        else:
            print key + " : NSString"

    def getOCProperty(self, key, value):
        key = 'number' if self.isNumber(key) else key
        key = 'Id' if key == 'id' else key

        if isinstance(value, str):
            if self.isNumber(value):
                return (key, 'NSNumber')
            else :
                return (key, 'NSString')
        elif isinstance(value, (int, float)):
            return (key, 'NSNumber')
        elif isinstance(value, list):
            return (key, 'NSArray')
        elif isinstance(value, dict):
            return (key, 'NSDictionary')
        else:
            return (key, "NSString")
    def capitalize(self, str):        
        return str[0].upper() + str[1:]
    def isNumber(self,str):
        isNumber = False
        try:
            string.atoi(str)
            isNumber = True
        except Exception as e:
            try:
                string.atof(str)
                isNumber = True
            except Exception as e:
                isNumber = False
            else:
                isNumber = True
        else:
            isNumber = True
        return isNumber
    def reducer(self):
        #将 array 长度规约为1
        pass
    def sortByLength(self):
        _list = []
        for key, item in self.bodyList:
            group = sorted(item, key=lambda x:len(x[0]+x[1]))
            _list.append((key, group))
        self.bodyList = _list

    def sortBylength2(self):
        _list = []
        for name, propList, subObjList in self.bodyList:
            _propList = sorted(propList, key=lambda x:len(x[0]+x[1]))
            _subObjList = sorted(subObjList, key=lambda x:len(x))
            _list.append((name, _propList, _subObjList))
        self.bodyList = _list
    def groupByName():

        pass
    def culLenForProperty(self, (key, value)):
        prefix = "@property(nonatomic, strong) "
        prop = prefix + value + "* " + key + ";"
        return len(prop)

    def genereteVOs(self):
        self.sortBylength2()
        for name, props, subObjs in self.bodyList:
            self.generateHFile(name, props, subObjs)
            self.generateMFile(name)
            
    def generateHFile(self, name, props, subObjs):
        _head = self.getHHeaderAnnotation(name, subObjs)
        _body = ""
        _prefix = "@property(nonatomic, strong) "
        _tail = "@end"
        maxLen = self.culLenForProperty(props[-1])
        for (key, oc_type) in props:
            _prop = _prefix + oc_type + "* " + key + ";"
            _format_prop = _prop.ljust(maxLen) + " "*4 + "//\n\n"
            _body = _body + _format_prop
        content = _head + "\n" + _body + _tail

        self.createDirIfNeeded()
        path = os.path.expanduser(r"~/Desktop/VO/" + name + self.suffix + ".h")
        output = open(path, 'w')
        try:
            output.write(content)
        finally:
            output.close

    def generateMFile(self, name):
        _name = self.capitalize(name) + self.suffix
        _time = time.strftime('%d/%m/%Y',time.localtime(time.time()))

        _content = '//\n//  ' + _name + '.m' + """
//  OTSVO
//
//  Created by Azuer on """ + _time + "." + """
//  Copyright © 2017 com.yihaodian. All rights reserved.
//

#import \"""" + _name + '.h\"' + '\n\n' + '@implementation ' + _name + '\n\n@end'
        self.createDirIfNeeded()
        path = os.path.expanduser(r"~/Desktop/VO/" + _name + ".m")
        output = open(path, 'w')
        try:
            output.write(_content)
        finally:
            output.close

    def createDirIfNeeded(self):
        path = os.path.expanduser(r"~/Desktop/VO")
        if not os.path.exists(path):
            os.makedirs(path)
    def getHHeaderAnnotation(self, name, subObjs):
        _name = self.capitalize(name) + self.suffix
        _time = time.strftime('%d/%m/%Y',time.localtime(time.time()))
        _subClass = ""
        for sub in subObjs:
            item = '@class ' + sub + ";"
            _subClass = _subClass + item + "\n"
        head = '//\n//  ' + _name + '.h' + """
//  OTSVO
//
//  Created by Azuer on """ + _time + "." + """ 
//  Copyright © 2017 com.yhd. All rights reserved.
//

#import <OTSBase/OTSBase.h> 

""" + _subClass + '\n@interface ' + _name + ': OTSValueObject\n'
        return head

    def genereteFiles(self):
        self.sortByLength()
        _time = time.strftime('%d/%m/%Y',time.localtime(time.time()))
        head = self.getHHeaderAnnotation('ServerInterfaceVO',[])
        body = ""
        prefix = "@property(nonatomic, strong) "
        tail = "@end"

        for (key, item) in self.bodyList:
            title = " " + key + " " if len(key) > 0 else '' 
            splitLine = "//" + "*"*34 + title + "*"*34 + "\n\n"
            body = body + splitLine
            maxLen = self.culLenForProperty(item[-1])
            for (name, oc_type) in item:
                prop = prefix + oc_type + "* " + name + ";"
                format_prop = prop.ljust(maxLen) + " "*4 + "//\n\n"
                body = body + format_prop

        content = head + "\n" + body + tail
        path = os.path.expanduser(r"~/Desktop/ServerInterfaceVO.h")
        output = open(path, 'w')
        try:
            output.write(content)
        finally:
            output.close

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hp:f:")
    path = ''
    prefix_format = ''
    if len(args) == 1:
        path = args[0]
    elif len(opts) == 1:
        for opt, value in opts:
            if opt == "-f":
                path = value
            else:
                print "Auguments Invalid"
                sys.exit(0)
    elif len(opts) == 2:
        for opt, value in opts:
            if opt == "-f":
                path = value
            elif opt == "-p":
                prefix_format = value
            else:
                print "Arguments Invalid"
                sys.exit(0)
    else:
        print "Arguments Invalid"
        sys.exit(0)
    instance = JsonModelParser(path, prefix_format)
    instance.parseJson()
    print "Complete"