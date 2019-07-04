# -*- coding: utf-8 -*-

import maya.cmds as cmds

def cleanBakeAnim():
    originNode = cmds.ls(selection=True)[0]
    bakedNode = cmds.ls(selection=True)[1]
    
    targetAttr = ['.translateX', '.translateY', '.translateZ',
                  '.rotateX', '.rotateY', '.rotateZ']
    
    for attr in targetAttr:
    
        # キーの打ってあるフレームを取得
        nodeName = originNode + attr
        keyTimes = cmds.keyframe(nodeName, query=True)
    
        # 処理対象の全フレームの数値をリスト化
        timeList = range(int(min(keyTimes)), int(max(keyTimes)));
    
        # 全フレームからキーの打ってあるフレームを削除したリストを生成
        delList = list(set(timeList) - set(keyTimes));
    
        # キーを削除
        nodeName = bakedNode + attr
        for f in delList:
            cmds.cutKey(nodeName, time=(f, f), cl=1);

def curveOffset():
    indexA = 0  # 基準index
    indexB = 1  # オフセット開始index
    
    # 選択したノードが持つアニメカーブ名を取得
    curveNames = cmds.keyframe(query=True, name=True)
    
    # 基準フレーム（以下A）、オフセットを始めるフレーム（以下B）それぞれの値を取得
    valueA = cmds.keyframe(curveNames, query=True, valueChange=True,
                           index=(indexA, indexA))
    valueB = cmds.keyframe(curveNames, query=True, valueChange=True,
                           index=(indexB, indexB))
    
    # 各カーブのAの値からBの値を引き、オフセット値を求める
    offsetValue = []
    for i in xrange(len(valueA)):
        offsetValue.append(valueA[i] - valueB[i])
    
    # Bから最終フレームまで、オフセット値を足していく
    for i in xrange(len(curveNames)):
        keyCount = cmds.keyframe(curveNames[i], query=True, kc=True)
        cmds.keyframe(curveNames[i], edit=True, index=(indexB, keyCount),
                      valueChange=offsetValue[i], relative=True)
