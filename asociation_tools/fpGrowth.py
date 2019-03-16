#!/usr/bin/python
# encoding: utf-8


"""

@author: harbour
@contact: 315874482@qq.com
@file: fpGrowth.py
@time: 2019/3/4 0024 22:35
@environments:
"""


import numpy as np
import logging
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class treeNode:

    def __init__(
        self,nameValue, numOccur, parentNode
    ):

        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print(' ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


def createTree(dataSet, minSup=1):
    ''' 创建FP树 '''
    # 第一次遍历数据集，创建头指针表
    headerTable = {}
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    # 移除不满足最小支持度的元素项
    for k in list(headerTable.keys()):
        if headerTable[k] < minSup:
            del(headerTable[k])
    # 空元素集，返回空
    freqItemSet = set(headerTable.keys())
    # print('freqItemSet:{}\theaderTable:{}'.format(freqItemSet,headerTable))
    if len(freqItemSet) == 0:
        return None, None
    # 增加一个数据项，用于存放指向相似元素项指针
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]
    retTree = treeNode('Null Set', 1, None) # 根节点
    # print('headerTable:{}\tretTree:{}'.format(headerTable, retTree))
    # 第二次遍历数据集，创建FP树
    for tranSet, count in dataSet.items():
        localD = {} # 对一个项集tranSet，记录其中每个元素项的全局频率，用于排序
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0] # 注意这个[0]，因为之前加过一个数据项
        if len(localD) > 0:
            # print('localD:{}'.format(localD))
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)] # 排序
            # print('orderedItems:{}\t{}'.format(orderedItems,sorted(localD.items(), key=lambda p: p[1], reverse=True)))
            updateTree(orderedItems, retTree, headerTable, count) # 更新FP树
    return retTree, headerTable


def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        # 有该元素项时计数值+1
        inTree.children[items[0]].inc(count)
    else:
        # 没有这个元素项时创建一个新节点
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 更新头指针表或前一个相似元素项节点的指针指向新节点
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
            # print('是否改变:{}\t:{}\t:{}'.format(headerTable,items[0],headerTable[items[0]][1]))

    if len(items) > 1:
        # 对剩下的元素项迭代调用updateTree函数
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):
    #headerTable里定位的节点为第一节点，通过while语句将其更新到最新节点且该节点没有nodeLink
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode #更新到下一节点，该操作不会改变headerTable

#生成数据集
def loadSimpDat():
    simpDat = [['r', 'z', 'h', 'j', 'p'],
               ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
               ['z'],
               ['r', 'x', 'n', 'o', 's'],
               ['y', 'r', 'x', 'z', 'q', 't', 'p'],
               ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simpDat


def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict

#从一颗FP树种挖掘频繁项集
#########################################
#抽取条件模式基
def findPrefixPath(basePat, treeNode):
    ''' 创建前缀路径 '''
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
            #从1开始是因为条件模式基不包含该搜索的元素项本身
        treeNode = treeNode.nodeLink #跳到下一相似节点
    return condPats

def ascendTree(leafNode, prefixPath):
    #辅助函数，对当前节点不断迭代往前寻找父节点并加入prefixPath这个list中去，直到根节点停止
    if leafNode.parent != None:
        #该条件判断是在根节点终止，根节点没有父节点
        prefixPath.append(leafNode.name)
        print('prefixPath:{}\tleafNode:{}'.format(prefixPath, leafNode))
        ascendTree(leafNode.parent, prefixPath)


def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0])]
    for basePat in bigL:
        newFreqSet = preFix.copy()
        #preFix传入的就是一个空集合
        newFreqSet.add(basePat)
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        myCondTree, myHead = createTree(condPattBases, minSup)

        if myHead != None:
            # 用于测试
            print('conditional tree for:', newFreqSet)
            myCondTree.disp()
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)

def fpGrowth(dataSet, minSup=3):
    initSet = createInitSet(dataSet)
    myFPtree, myHeaderTab = createTree(initSet, minSup)
    print('myHeaderTab:{}'.format(myHeaderTab))
    freqItems = []
    mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItems)
    return freqItems