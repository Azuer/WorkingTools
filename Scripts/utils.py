#!/usr/bin/python
#-*- coding: UTF-8 -*-

import codecs #防止编码问题


def fp2D(tb):#format print

    for i in range(len(tb)):
        for j in range(len(tb[i])):
            print tb[i][j],
            print '\t',
            if j == len(tb[i])-1:
                print '\n'

def fp1DAs2D(tb, m, n):
    for i in range(m):
        for j in range(n):
            idx = i*m+j
            print tb[idx],
            print '\t',
            if j == m-1:
                print '\n'

class TreeNode(object):
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def Tree(vals):
    nodes = []
    for i in range(1, len(vals)+1):
        val = vals[i-1]
        if val == None:
            continue
        node = TreeNode(val)
        if i > 1:
            father = nodes[i/2-1]
            if i%2==0:
                father.left = node
            else:
                father.right = node
        nodes.append(node)
    return nodes[0] if len(nodes) > 0 else None

def dfs(root):
    if root == None:
        return
    print root.val
    dfs(root.left)
    dfs(root.right)

def bfs(root):
    res = []
    queue = [root]
    while len(queue) > 0:
        node = queue.pop(0)
        print node.val
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)