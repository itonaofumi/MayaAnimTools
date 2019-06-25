# -*- coding: utf-8 -*-

import maya.cmds as cmds
 
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
