# -*- coding: utf-8 -*-

import maya.cmds as cmds

def cleanBakeAnim():
    origin = cmds.ls(selection=True)[0]
    baked = cmds.ls(selection=True)[1]
    
    # 処理対象のアトリビュート
    attrList = ['.translateX', '.translateY', '.translateZ', '.rotateX', '.rotateY', '.rotateZ']
    
    for attr in attrList:
    
        # キーの打ってあるフレームを取得
        nodeName = origin + attr
        keyTimes = cmds.keyframe(nodeName, query=True)
    
        # 処理対象の全フレームの数値をリスト化
        timeList = range(int(min(keyTimes)), int(max(keyTimes)));
    
        # 全フレームからキーの打ってあるフレームを削除したリストを生成
        delList = list(set(timeList) - set(keyTimes));
    
        # キーを削除
        nodeName = baked + attr
        for f in delList:
            cmds.cutKey(nodeName, time=(f, f), cl=1);

def curveOffset():
    flameA = 0  # 基準index
    flameB = 1  # オフセット開始index
    
    # 選択したノードが持つアニメカーブ名を取得
    curves = cmds.keyframe(query=True, name=True)
    
    # 基準フレーム（以下A）、オフセットを始めるフレーム（以下B）それぞれの値を取得
    valueA = cmds.keyframe(curves, query=True, valueChange=True,
                           index=(flameA, flameA))
    valueB = cmds.keyframe(curves, query=True, valueChange=True,
                           index=(flameB, flameB))
    
    # 各カーブのAの値からBの値を引き、オフセット値を求める
    offsetValue = []
    for i in xrange(len(valueA)):
        offsetValue.append(valueA[i] - valueB[i])
    
    # Bから最終フレームまで、オフセット値を足していく
    for i in xrange(len(curves)):
        keyCount = cmds.keyframe(curves[i], query=True, kc=True)
        cmds.keyframe(curves[i], edit=True, index=(flameB, keyCount),
                      valueChange=offsetValue[i], relative=True)
