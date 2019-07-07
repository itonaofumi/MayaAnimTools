# -*- coding: utf-8 -*-

import maya.cmds as cmds

def cleanBakeAnim():
    originNode = cmds.ls(selection=True)[0]
    bakedNode = cmds.ls(selection=True)[1]
    
    targetAttr = ['.translateX', '.translateY', '.translateZ',
                  '.rotateX', '.rotateY', '.rotateZ']
    
    for attr in targetAttr:
    
        # キーの打ってあるフレームを取得
        nodeAttr = originNode + attr
        keyTimes = cmds.keyframe(nodeAttr, query=True)
    
        # 処理対象の全フレームの数値をリスト化
        timeList = range(int(min(keyTimes)), int(max(keyTimes)));
    
        # 全フレームからキーの打ってあるフレームを削除したリストを生成
        delList = list(set(timeList) - set(keyTimes));
    
        # キーを削除
        nodeAttr = bakedNode + attr
        for f in delList:
            cmds.cutKey(nodeAttr, time=(f, f), cl=1);

def curveOffset():
    
    # 選択したノードが持つアニメカーブ名を取得
    curveNames = cmds.keyframe(query=True, name=True)

    indexA = 0  # 基準index
    indexB = 1  # オフセット開始index
    
    # 基準フレーム、オフセットを始めるフレームそれぞれの値を取得
    valueA = cmds.keyframe(curveNames, query=True, valueChange=True,
                           index=(indexA, indexA))
    valueB = cmds.keyframe(curveNames, query=True, valueChange=True,
                           index=(indexB, indexB))
    
    # オフセット値を求める
    offsetValue = []
    for i in xrange(len(valueA)):
        offsetValue.append(valueA[i] - valueB[i])
    
    # Bから最終フレームまで、オフセット値を足していく
    for i in xrange(len(curveNames)):
        keyCount = cmds.keyframe(curveNames[i], query=True, kc=True)
        cmds.keyframe(curveNames[i], edit=True, index=(indexB, keyCount),
                      valueChange=offsetValue[i], relative=True)