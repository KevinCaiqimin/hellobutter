import random
from random import Random
from heapq import *
import hashlib
import uuid
import time

class utils:
    @staticmethod
    def selectContinus(ary):
        refVars = [0, len(ary) - 1]
        def select(num):
            endNdx = refVars[1]
            data = []
            for i in range(0, num):
                startNdx = refVars[0]
                if startNdx > endNdx:
                    break
                ndx = random.randint(startNdx, endNdx)
                item = ary[ndx]
                #swap
                ary[startNdx], ary[ndx] = ary[ndx], ary[startNdx]
                #update closure vars
                startNdx += 1
                refVars[0] = startNdx

                data.append(item)
            return data
        return select

    @staticmethod
    def sampleByWeight(weightsAry, n, rand = None):
        if n <= 0:
            return []
        if rand is None:
            rand = Random()
        selection = []
        heap = []
        for i, weight in enumerate(weightsAry):
            if weight <= 0:
                continue
            item = i
            key = rand.random() ** (1.0 / weight)
            if len(selection) < n:
                heap.append((key, len(selection)))
                selection.append(item)
                if len(selection) == n:
                    heapify(heap)
            elif key > heap[0][0]:
                index = heap[0][1]
                heapreplace(heap, (key, index))
                selection[index] = item
        return selection

    @staticmethod
    def convertToSignString(dicData, secretKey = None, secretValue = None):
        keys = sorted(dicData)
        params = []
        for k in keys:
            v = dicData.get(k)
            params.append(format("%s=%s" % (k, str(v))))
        if secretKey is not None and secretValue is not None:
            params.append(format("%s=%s" % (secretKey, str(secretValue))))
        return "&".join(params)

    @staticmethod
    def toMD5(strData):
        hashData = hashlib.md5(strData)
        result = hashData.hexdigest()
        return result

    @staticmethod
    def toSHA1(strData):
        hashData = hashlib.sha1(strData)
        result = hashData.hexdigest()
        return result

    @staticmethod
    def calcFileMD5(f):
        m = hashlib.md5()

        while True:
            data = f.read(10240)
            if not data:
                break

            m.update(data)
        return m.hexdigest()

    @staticmethod
    def getUUID():
        return uuid.uuid1()

    @staticmethod
    def getNowTime():
        return long(time.time())

    @staticmethod
    def randToken(len):
        rand = Random()
        token = []
        for i in range(0, len):
            token.append(rand.randint(0, 10))
        return "".join(token)