#!/usr/bin/python
# encoding: utf-8


"""

@author: harbour
@contact: 315874482@qq.com
@file: Apriori_algorithm.py
@time: 2019/2/24 0024 22:35
@environments:
"""



import logging
import time



logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class apriori:

    def __init__(
        self,
        minsupport = 0.5,
        minConf = 0.7
    ):

        self.minsupport = minsupport
        self.minConf = minConf

    # private methods
    @staticmethod
    def __createC1(dataSet):
        #创造1个元素的项集列表;dataSet的格式为列表内嵌多个列表，内嵌列表为每一个物品的集合
        C1 = []
        for transaction in dataSet:
            for item in transaction:
                if not [item] in C1:
                    C1.append([item])
        C1.sort()
        return list(map(frozenset, C1))

    @staticmethod
    def __scanD(D, Ck, minSupport):
        #D和Ck格式都为集合，其中Ck为frozenset不变集合
        #对候选项集进行扫描，排除小于最小支持度的项集
        ssCnt = {}
        for tid in D:
            for can in Ck:
                if can.issubset(tid):
                    ssCnt[can] = ssCnt.get(can, 0) + 1 #返回指定键的值如果该键对应值不存在则返回参数指定值
        numItems = float(len(D))
        retList = [] #频繁项集
        supportData = {} #每个项集的key及对应的value，包括非频繁项集
        for key in ssCnt:
            support = ssCnt[key]/ numItems
            if support >= minSupport:
                retList.insert(0, key) #列表插入值在头部
            supportData[key] = support
        return retList, supportData

    @staticmethod
    def __aprioriGen(Lk, k):
        # 生成K+1项候选项集
        retList = []
        lenLk = len(Lk)
        for i in range(lenLk):
            for j in range(i + 1, lenLk):
                #前k-2项相同时，将两个集合合并
                L1 = list(Lk[i])[:k-2]; L2 = list(Lk[j])[:k-2]
                L1.sort(); L2.sort()
                if L1 == L2:
                    retList.append(Lk[i] | Lk[j]) #求两个集合内包含所有元素
        return retList

    @staticmethod
    def __calcConf(freqSet, H, supportData, brl, minConf):
        # 对候选规则集进行评估
        prunedH = []
        for conseq in H:
            conf = supportData[freqSet]/supportData[freqSet - conseq]
            if conf >= minConf:
                print(freqSet - conseq, '-->', conseq, 'conf:', conf)
                brl.append((freqSet-conseq, conseq, conf))
                prunedH.append(conseq)
        return prunedH


    def __rulesFromConseq(self, freqSet, H, supportData, brl, minConf):
        #生成候选规则集
        m = len(H[0])
        # print('len_freqSet:{}'.format(len(freqSet)), '\t', 'freqSet:{}'.format(freqSet))
        # if (len(freqSet) > (m+1)):
        #     Hmpl = self.__aprioriGen(H, m + 1) #将列表中单个元素项集两两合并
        #     print('Hmplss:{}'.format(Hmpl))
        #     Hmpl = self.__calcConf(freqSet, Hmpl, supportData, brl, minConf)
        #     print('Hmplss:{}'.format(Hmpl))
        #     if (len(Hmpl) > 1):
        #         self.__rulesFromConseq(freqSet, Hmpl, supportData, brl, minConf)
        #以下改进
        while (len(freqSet)>m): #判断长度大于m，这时既可以求H的可信度
            H = self.__calcConf(freqSet, H, supportData, brl, minConf)
            if (len(H)>1):
                H = self.__aprioriGen(H, m+1)
                m += 1
            else:
                break


    def freq(self, dataSet):
        """创建频繁项集"""

        log.info("生成元素数目1的候选项集...")
        self.t = time.time()
        self.C1 = self.__createC1(dataSet)
        self.D = list(map(set, dataSet))
        log.info("对元素数目1的候选项集进行扫描...")
        self.L1, self.supportData = self.__scanD(self.D, self.C1, self.minsupport)
        self.L = [self.L1]
        k = 2
        log.info("对元素数目大于1的候选项集进行迭代扫描...")

        while(len(self.L[k-2])>0):
            self.Ck = self.__aprioriGen(self.L[k-2], k)
            self.Lk, self.supk = self.__scanD(self.D, self.Ck, self.minsupport)
            self.supportData.update(self.supk)
            self.L.append(self.Lk)
            k += 1

        log.info("总运行时间{}".format(time.time() -self.t))
        return self.L, self.supportData

    def generateRules(self, L, supportData, minConf=0.7):

        self.bigRuleList = []
        log.info("开始生成关联规则...")
        # for i in range(1, len(L)):
        #     #从含两个元素的集合开始循环
        #     for freqSet in L[i]:
        #         self.H1 = [frozenset([item]) for item in freqSet]
        #         if (i > 1):
        #             # 三个及以上元素的集合
        #             self.__rulesFromConseq(freqSet, self.H1, supportData, self.bigRuleList, minConf)
        #         else:
        #             # 两个元素的集合
        #             self.__calcConf(freqSet, self.H1, supportData, self.bigRuleList, minConf)
        # return self.bigRuleList
        #以下改进
        for i in range(1, len(L)):
            for freqSet in L[i]:
                self.H1 = [frozenset([item]) for item in freqSet] #把集合里的元素拆开，每个集合一个元素
                self.__rulesFromConseq(freqSet, self.H1, supportData, self.bigRuleList, minConf)
        return self.bigRuleList

