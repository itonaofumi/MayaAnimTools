# -*- coding: utf-8 -*-

import maya.mel as mm
import maya.cmds as mc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import json
import math
import re

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

        try:
            animCurve.animCurveType  # アニメカーブがあるかチェック
        except:
            pass
            #print '{0} has no animation curve.'.format(clipboardItem.nodeName)
        else:
            # クリップボード再登録時に必要な情報と、アニメカーブ固有の情報を取得。
            addr = clipboardItem.getAddressingInfo()
            animData['animData'].append({
                'addrInfo':[addr[0], addr[1], addr[2]],
                'nodeName':clipboardItem.nodeName,
                'fullName':clipboardItem.fullAttributeName,
                'leafName':clipboardItem.leafAttributeName,
                'curveType':animCurve.animCurveType,
                'isWeight':animCurve.isWeighted,
                'preInf':animCurve.preInfinityType,
                'postInf':animCurve.postInfinityType,
                'keyData':{}
            })

            # キー情報の取り出し
            d = {'times':[], 'values':[],
                 'inTangentType':[], 'outTangentType':[],
                 'inTangentX':[], 'inTangentY':[],
                 'outTangentX':[],'outTangentY':[],
                 'tangentLock':[], 'weightLock':[],
                 'breakdown':[]}

            for j in range(animCurve.numKeys):
                d['times'].append(animCurve.input(j).asUnits(om.MTime.k30FPS))
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
                d['breakdown'].append(animCurve.isBreakdown(j))

            animData['animData'][-1]['keyData'] = d

        # update progress bar
        mc.progressBar(gMainProgressBar, edit=True, step=1)

    # jsonデータとして書き出し
    jsonPath = 'C:/Users/0300091280/Desktop/hoge.json'
    with open(jsonPath, 'w') as jsonFile:
        json.dump(animData, jsonFile)

    # close progress bar
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)

def pasteAnimation():
    '''一時ファイルからアニメーションデータを読み込み、クリップボードに再登録
    する。その後、選択されたオブジェクトにアニメーションのペーストを試みる。
    '''

    # jsonデータの読み込み
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

        # 先に時間情報を30FPS換算に変換しておく
        convTime = [om.MTime(x, om.MTime.k30FPS) for x in curveData['keyData']['times']]

        '''上でやってるのはこの処理
        convTime = list()
        for x in curveData['keyData']['times'] :
            mTime = om.MTime(x, om.MTime.k30FPS)
            convTime.append(mTime)
        
        速くするなら配列を作るときに先にサイズを確定させる
        convTime = [ None ] * len(curveData['keyData']['times'])
        for i in range(len(curveData['keyData']['times'])) :
            mTime = om.MTime(x, om.MTime.k30FPS)
            convTime[i] = mTime
        '''

        # キー情報を一気に流し込む
        animCurve.addKeysWithTangents(convTime, #curveData['keyData']['times'],
            curveData['keyData']['values'],
            oma.MFnAnimCurve.kTangentAuto,
            oma.MFnAnimCurve.kTangentAuto,
            curveData['keyData']['inTangentType'],
            curveData['keyData']['outTangentType'],
            curveData['keyData']['inTangentX'],
            curveData['keyData']['inTangentY'],
            curveData['keyData']['outTangentX'],
            curveData['keyData']['outTangentY'],
            curveData['keyData']['tangentLock'],
            curveData['keyData']['weightLock'])

        # addKeysWithTangents()では個別のタンジェントタイプが反映されないので、
        # キー毎にタンジェントを設定。ついでにisBreakdownもセットする。
        for i in range(len(curveData['keyData']['times'])):
            inT = curveData['keyData']['inTangentType'][i]
            outT = curveData['keyData']['outTangentType'][i]
            breakdown = curveData['keyData']['breakdown'][i]

            animCurve.setInTangentType(i, inT)
            animCurve.setOutTangentType(i, outT)
            animCurve.setIsBreakdown(i, breakdown)

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

    # ペースト時にクリップボードに格納されているノード名と選択されているノード名
    # との文字列比較を行うので、まずクリップボードのノード名を取り出す。
    clipboardArray = clipboard.clipboardItems()
    clipboardItemNames = []
    for clipboardItem in clipboardArray:
        clipboardItemNames.append(clipboardItem.nodeName)

    # 順番はそのままで、重複したノード名を削除する
    clipboardItemNames = sorted(set(clipboardItemNames),
                                key=clipboardItemNames.index)
    '''
    print '---clipboard item list---'
    for i in clipboardItemNames: print i
    '''

    # クリップボードに含まれたノード名と選択されたノード名で文字列比較を行い、
    # 同じノード名があったら新しい選択リストに登録する。
    # これでクリップボードと同じ順番で再選択できる。
    selectedItems = mc.ls(selection=True)
    newSelectionList = []
    isNameMatched = False

    for cItem in clipboardItemNames:
        cItemSplit = re.split('[:\|]', cItem)
        for sItem in selectedItems:
            sItemSplit = re.split('[:\|]', sItem)
            if cItemSplit[-1] == sItemSplit[-1]:
                newSelectionList.append(sItem)
                isNameMatched = True
                break
    '''
    print '---newSelecton item list---'
    for i in newSelectionList: print i
    '''

    # マッチしたノード名があった場合、クリップボード順になったリストで選択しなおす。
    # その後、再選択したノード名とクリップボード内のノード名をもう一度比較し、
    # クリップボードにだけ存在するノード名の要素を削除する。
    # これをしないと順番が完全に合わない。めんどくさい。
    if isNameMatched:
        mc.select(clear=True)
        mc.select(newSelectionList)

        # 再選択したノード名のリスト化
        selectedItems = mc.ls(selection=True)
        sItemSplit =[]
        for selectedItem in selectedItems:
            sItemSplit.append(re.split('[:\|]', selectedItem)[-1])

        # クリップボード内のノード名のリスト化
        cItemSplit = []
        for clipboardItem in clipboardArray:
            cNodeName = clipboardItem.nodeName
            cItemSplit.append(re.split('[:\|]', cNodeName)[-1])

        # 再選択したノード名がクリップボード内に存在するか調べ、
        # 存在している＝消さないインデックスのリストを作る
        keepIndex = []
        for s in sItemSplit:
            for i, c in enumerate(cItemSplit):
                if s == c:
                    keepIndex.append(i)
        # print 'keepIndex', keepIndex

        # keepIndexの要素数とクリップボードの要素数を比較し、
        # 異なった場合は消す対象が存在するということになる。
        delIndex = list(range(len(cItemSplit)))

        if len(keepIndex) != len(delIndex):
            delIndex = list(set(delIndex) - set(keepIndex))
            # print 'deleteIndex', delIndex

            for i in reversed(delIndex):
                clipboardArray.remove(i)

        # debug クリップボードの中を再確認
        '''
        for clipboardItem in clipboardArray:
            animCurveObj = clipboardItem.animCurve
            animCurve = oma.MFnAnimCurve(animCurveObj)
            print clipboardItem.nodeName, clipboardItem.leafAttributeName, animCurve.value(0)
        print mc.ls(selection=True)
        '''
        
        # いじったclipboardArrayを再度クリップボードにセット
        clipboard.set(clipboardArray)

    # タイムスライダーで選択されている時間を取得
    aPlayBackSliderPython = mm.eval('$tmpVar=$gPlayBackSlider')
    rangeArray = mc.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)

    # 選択されたノードに対してペーストを実行
    mc.pasteKey(clipboard='api', time=(rangeArray[0], rangeArray[0]),
                option='insert')

    # close progress bar
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)
