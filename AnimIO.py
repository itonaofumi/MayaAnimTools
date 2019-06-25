# -*- coding: utf-8 -*-
import maya.mel as mm
import maya.cmds as mc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import json
import math


def copyAnimation():
    '''選択されたオブジェクトのアニメーションをクリップボードにコピーし、
    一時ファイルに書き出す。
    時間の選択はタイムスライダーで行う。
    時間を選択していない場合はカレントフレームが対象。
    '''
    selectedItems = mc.ls(selection=True, long=True)

    # タイムスライダーで選択されている時間を取得
    aPlayBackSliderPython = mm.eval('$tmpVar=$gPlayBackSlider')
    rangeArray = mc.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)

    # 選択されているオブジェクトのアニメーションをクリップボードにコピー
    mc.copyKey(selectedItems, clipboard='api', animation='objects',
               includeUpperBound=True, forceIndependentEulerAngles=True,
               time=(int(rangeArray[0]), int(rangeArray[1])),
               option='keys', shape=False)


    # クリップボードからアニメーションを取り出す
    clipboard = oma.MAnimCurveClipboard.theAPIClipboard
    clipboardArray = clipboard.clipboardItems()

    animData = dict()
    animData['animData'] = []

    # progress bar
    gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
    mc.progressBar(gMainProgressBar, edit=True, beginProgress=True,
        isInterruptable=False, status='Export Animation Clipboard ...',
	    maxValue=len(clipboardArray))

    # アニメカーブに１つずつアクセス
    for clipboardItem in clipboardArray:
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

        # キー情報の取り出し
        d = {'times':[], 'values':[],
             'inTangentType':[], 'outTangentType':[],
             'inTangentX':[], 'inTangentY':[],
             'outTangentX':[],'outTangentY':[],
             'tangentLock':[], 'weightLock':[]}

        for j in range(animCurve.numKeys):
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

        # update progress bar
        mc.progressBar(gMainProgressBar, edit=True, step=1)

    # Jsonデータとして書き出し
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'

    with open(jsonPath, 'w') as jsonFile:
        json.dump(animData, jsonFile)

    # close progress bar
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)


def pasteAnimation():

    # Jsonデータの読み込み
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'

    with open(jsonPath, 'r') as jsonFile:
        animData =json.load(jsonFile)

    clipboard = oma.MAnimCurveClipboard.theAPIClipboard
    clipboard.clear()
    clipItems = list()

    # progress bar
    gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
    mc.progressBar(gMainProgressBar, edit=True, beginProgress=True,
        isInterruptable=False, status='Import Animation Clipboard ...',
	    maxValue=len(animData['animData']))

    # アニメ情報を読み込んでMFnAnimCurveを作り、クリップボードに格納する。
    for curveData in animData['animData']:

        # カーブタイプを取り出し、MFnAnimCurveを作る。
        curveType = curveData['curveType']
        animCurve = oma.MFnAnimCurve()
        animCurveObj = animCurve.create(curveType)

        # カーブ固有の情報をセット
        animCurve.setIsWeighted(curveData['isWeight'])
        animCurve.setPreInfinityType(curveData['preInf'])
        animCurve.setPostInfinityType(curveData['postInf'])

        # キー情報を一気に流し込む
        animCurve.addKeysWithTangents(curveData['keyData']['times'],
            curveData['keyData']['values'],
            oma.MFnAnimCurve.kTangentGlobal,
            oma.MFnAnimCurve.kTangentGlobal,
            curveData['keyData']['inTangentType'],
            curveData['keyData']['outTangentType'],
            curveData['keyData']['inTangentX'],
            curveData['keyData']['inTangentY'],
            curveData['keyData']['outTangentX'],
            curveData['keyData']['outTangentY'],
            curveData['keyData']['tangentLock'],
            curveData['keyData']['weightLock'])

        # クリップボードアイテムに登録する
        clipboardItem = oma.MAnimCurveClipboardItem()
        clipboardItem.setAddressingInfo(curveData['addrInfo'][0],
                                        curveData['addrInfo'][1],
                                        curveData['addrInfo'][2])
        clipboardItem.setNameInfo(curveData['nodeName'],
                                  curveData['fullName'],
                                  curveData['leafName'])
        clipboardItem.setAnimCurve(animCurveObj)
        clipItems.append(clipboardItem)

        # update progress bar
        mc.progressBar(gMainProgressBar, edit=True, step=1)

    # クリップボードに登録
    clipboard.set(clipItems)

    # タイムスライダーで選択されている時間を取得
    aPlayBackSliderPython = mm.eval('$tmpVar=$gPlayBackSlider')
    rangeArray = mc.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)

    mc.pasteKey(clipboard='api', time=(rangeArray[0], rangeArray[0]),
                option='insert')

    # close progress bar
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)
