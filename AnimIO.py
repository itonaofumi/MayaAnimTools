# -*- coding: utf-8 -*-
import maya.mel as mm
import maya.cmds as mc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import json
import math

def copyClipboard():
    selectedItems = mc.ls(selection=True, long=True)

    # タイムスライダーで選択されている時間を取得
    aPlayBackSliderPython = mm.eval('$tmpVar=$gPlayBackSlider')
    rangeArray = mc.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)

    # 選択されているオブジェクトのアニメーションをクリップボードにコピー
    mc.copyKey(selectedItems, clipboard='api', animation='objects',
               includeUpperBound=True, forceIndependentEulerAngles=True,
               time=(int(rangeArray[0]), int(rangeArray[1])),
               option='keys', shape=False)

def exportAnimation():

    # クリップボードからアニメーションを取り出す
    clipboard = oma.MAnimCurveClipboard.theAPIClipboard
    clipboardArray = clipboard.clipboardItems()

    animData = dict()
    animData['animData'] = []

    # アニメカーブに１つずつアクセス
    for i in range(len(clipboardArray)):
        clipboardItem = clipboardArray[i]
        animCurveObj = clipboardItem.animCurve
        animCurve = oma.MFnAnimCurve(animCurveObj)

        # クリップボード再登録時に必要な情報と、アニメカーブ固有の情報
        addr = clipboardItem.getAddressingInfo()
        animData['animData'].append({'addrInfo':[addr[0], addr[1], addr[2]],
                                     'nodeName':clipboardItem.nodeName,
                                     'fullName':clipboardItem.fullAttributeName,
                                     'leafName':clipboardItem.leafAttributeName,
                                     'curveType':animCurve.animCurveType,
                                     'isWeight':animCurve.isWeighted,
                                     'preInf':animCurve.preInfinityType,
                                     'postInf':animCurve.postInfinityType,
                                     'keyData':[],
                                     'tangentData':[]})

        # キー情報を取り出し
        keyNum = animCurve.numKeys
        for j in range(keyNum):

            # タンジェントアングルとウエイトは戻り値が２つなので先に取り出す
            ret = animCurve.getTangentAngleWeight(j, True)
            inTangentAngle = ret[0].value
            inTangentWeight = ret[1]
            ret = animCurve.getTangentAngleWeight(j, False)
            outTangentAngle = ret[0].value
            outTangentWeight = ret[1]

            # MFnAnimCurve.addKey()に必要な情報
            keyData = [animCurve.input(j).value,
                       animCurve.value(j),
                       animCurve.inTangentType(j),
                       animCurve.outTangentType(j)]

            # それ以外のタンジェント等の情報
            tangentData = [inTangentAngle,
                           inTangentWeight,
                           outTangentAngle,
                           outTangentWeight,
                           animCurve.tangentsLocked(j),
                           animCurve.weightsLocked(j),
                           animCurve.isBreakdown(j)]

            animData['animData'][-1]['keyData'].append(keyData)
            animData['animData'][-1]['tangentData'].append(tangentData)

    # Jsonデータとして書き出し
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'
    if not (mc.file(jsonPath, query=True, exists=True)):
        jsonFile = open(jsonPath, 'w', os.O_CREAT)
    else:
        jsonFile = open(jsonPath, 'w')
    json.dump(animData, jsonFile)
    print animData

def exportAnimation2():

    # クリップボードからアニメーションを取り出す
    clipboard = oma.MAnimCurveClipboard.theAPIClipboard
    clipboardArray = clipboard.clipboardItems()

    animData = dict()
    animData['animData'] = []

    # アニメカーブに１つずつアクセス
    for i in range(len(clipboardArray)):
        clipboardItem = clipboardArray[i]
        animCurveObj = clipboardItem.animCurve
        animCurve = oma.MFnAnimCurve(animCurveObj)

        # クリップボード再登録時に必要な情報と、アニメカーブ固有の情報
        addr = clipboardItem.getAddressingInfo()
        animData['animData'].append({'addrInfo':[addr[0], addr[1], addr[2]],
                                     'nodeName':clipboardItem.nodeName,
                                     'fullName':clipboardItem.fullAttributeName,
                                     'leafName':clipboardItem.leafAttributeName,
                                     'curveType':animCurve.animCurveType,
                                     'isWeight':animCurve.isWeighted,
                                     'preInf':animCurve.preInfinityType,
                                     'postInf':animCurve.postInfinityType,
                                     'keyData':{}})

        # キー情報を取り出し
        d = {'times':[], 'values':[],
             'inTangentType':[], 'outTangentType':[],
             'inTangentX':[], 'inTangentY':[],
             'outTangentX':[],'outTangentY':[],
             'tangentLock':[], 'weightLock':[]}

        keyNum = animCurve.numKeys
        for j in range(keyNum):
            d['times'].append(animCurve.input(j).value)
            d['values'].append(animCurve.value(j))
            d['inTangentType'].append(animCurve.inTangentType(j))
            d['outTangentType'].append(animCurve.outTangentType(j))
            # animCurve.getTangentXY() is not working...
            ret = animCurve.getTangentAngleWeight(j, True)
            d['inTangentX'].append(3 * ret[1] * math.cos(ret[0].value))
            d['inTangentY'].append(3 * ret[1] * math.sin(ret[0].value))
            ret = animCurve.getTangentAngleWeight(j, False)
            d['outTangentX'].append(3 * ret[1] * math.cos(ret[0].value))
            d['outTangentY'].append(3 * ret[1] * math.sin(ret[0].value))
            d['tangentLock'].append(animCurve.tangentsLocked(j))
            d['weightLock'].append(animCurve.weightsLocked(j))

        animData['animData'][-1]['keyData'] = d

    # Jsonデータとして書き出し
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'
    if not (mc.file(jsonPath, query=True, exists=True)):
        jsonFile = open(jsonPath, 'w', os.O_CREAT)
    else:
        jsonFile = open(jsonPath, 'w')
    json.dump(animData, jsonFile)
    print animData

def copyAnimation():
    '''選択されたオブジェクトのアニメーションをクリップボードにコピーし、
    一時ファイルに書き出す。
    時間の選択はタイムスライダーで行う。
    時間を選択していない場合はカレントフレームが対象。
    '''
    copyClipboard()
    exportAnimation()

def copyAnimation2():
    '''選択されたオブジェクトのアニメーションをクリップボードにコピーし、
    一時ファイルに書き出す。
    時間の選択はタイムスライダーで行う。
    時間を選択していない場合はカレントフレームが対象。
    '''
    copyClipboard()
    exportAnimation2()

def pasteAnimation():

    # Jsonデータの読み込み
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'
    jsonData = open(jsonPath, 'r')
    animData =json.load(jsonData)

    clipboard = oma.MAnimCurveClipboard.theAPIClipboard
    clipboard.clear()
    clipItems = list()

    # アニメ情報を読み込んでMFnAnimCurveを作り、クリップボードに格納していく。
    for curveData in animData['animData']:

        # カーブタイプを取り出し、MFnAnimCurveを作る。
        curveType = curveData['curveType']
        animCurve = oma.MFnAnimCurve()
        animCurveObj = animCurve.create(curveType)

        # カーブ固有の情報をセット
        animCurve.setIsWeighted(curveData['isWeight'])
        animCurve.setPreInfinityType(curveData['preInf'])
        animCurve.setPostInfinityType(curveData['postInf'])

        for keyData in curveData['keyData']:
            #print keyData
            animCurve.addKey(om.MTime(keyData[0]), om.MTime(keyData[1]),
                             keyData[2], keyData[3])
        for i, tangentData in enumerate(curveData['tangentData']):
            #print i, tangentData
            animCurve.setAngle(i, om.MAngle(tangentData[0]), True)
            animCurve.setWeight(i, tangentData[1], True)
            animCurve.setAngle(i, om.MAngle(tangentData[2]), False)
            animCurve.setWeight(i, tangentData[3], False)
            animCurve.setTangentsLocked(i, tangentData[4])
            animCurve.setWeightsLocked(i, tangentData[5])
            animCurve.setIsBreakdown(i, tangentData[6])
        
        clipboardItem = oma.MAnimCurveClipboardItem()
        clipboardItem.setAddressingInfo(curveData['addrInfo'][0],
                                        curveData['addrInfo'][1],
                                        curveData['addrInfo'][2])
        clipboardItem.setNameInfo(curveData['nodeName'],
                                  curveData['fullName'],
                                  curveData['leafName'])
        clipboardItem.setAnimCurve(animCurveObj)
        clipItems.append(clipboardItem)

    clipboard.set(clipItems)
    mc.pasteKey(clipboard='api')
    '''
    mc.pasteKey('locator2', clipboard='api', animation='objects', connect=False,
                option='replace')
    '''

def pasteAnimation2():

    # Jsonデータの読み込み
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'
    jsonData = open(jsonPath, 'r')
    animData =json.load(jsonData)

    clipboard = oma.MAnimCurveClipboard.theAPIClipboard
    clipboard.clear()
    clipItems = list()

    # アニメ情報を読み込んでMFnAnimCurveを作り、クリップボードに格納していく。
    for curveData in animData['animData']:

        # カーブタイプを取り出し、MFnAnimCurveを作る。
        curveType = curveData['curveType']
        animCurve = oma.MFnAnimCurve()
        animCurveObj = animCurve.create(curveType)

        # カーブ固有の情報をセット
        animCurve.setIsWeighted(curveData['isWeight'])
        animCurve.setPreInfinityType(curveData['preInf'])
        animCurve.setPostInfinityType(curveData['postInf'])

        for keyData in curveData['keyData']:
            #print keyData
            animCurve.addKey(om.MTime(keyData[0]), om.MTime(keyData[1]),
                             keyData[2], keyData[3])
        for i, tangentData in enumerate(curveData['tangentData']):
            #print i, tangentData
            animCurve.setAngle(i, om.MAngle(tangentData[0]), True)
            animCurve.setWeight(i, tangentData[1], True)
            animCurve.setAngle(i, om.MAngle(tangentData[2]), False)
            animCurve.setWeight(i, tangentData[3], False)
            animCurve.setTangentsLocked(i, tangentData[4])
            animCurve.setWeightsLocked(i, tangentData[5])
            animCurve.setIsBreakdown(i, tangentData[6])
        
        clipboardItem = oma.MAnimCurveClipboardItem()
        clipboardItem.setAddressingInfo(curveData['addrInfo'][0],
                                        curveData['addrInfo'][1],
                                        curveData['addrInfo'][2])
        clipboardItem.setNameInfo(curveData['nodeName'],
                                  curveData['fullName'],
                                  curveData['leafName'])
        clipboardItem.setAnimCurve(animCurveObj)
        clipItems.append(clipboardItem)

    clipboard.set(clipItems)
    mc.pasteKey(clipboard='api')
    '''
    mc.pasteKey('locator2', clipboard='api', animation='objects', connect=False,
                option='replace')
    '''