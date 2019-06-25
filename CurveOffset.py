# -*- coding: utf-8 -*-

import maya.cmds as cmds

# 基準index
flameA = 0
 
# オフセット開始index
flameB = 1
 
# 選択したノードが持つアニメカーブ名を取得
curves = cmds.keyframe(query=True, name=True)
print(curves)
 
# 基準フレーム（以下A）、オフセットを始めるフレーム（以下B）それぞれの値を取得
valueA = cmds.keyframe(curves, query=True, valueChange=True, index=(flameA, flameA))
print(valueA)
valueB = cmds.keyframe(curves, query=True, valueChange=True, index=(flameB, flameB))
print(valueB)
 
# 各カーブのAの値からBの値を引き、オフセット値を求める
offsetValue = []
for i in xrange(len(valueA)):
    offsetValue.append(valueA[i] - valueB[i])
print(offsetValue)
 
# Bから最終フレームまで、オフセット値を足していく
for i in xrange(len(curves)):
    keyCount = cmds.keyframe(curves[i], query=True, kc=True)
    cmds.keyframe(curves[i], edit=True, index=(flameB, keyCount), valueChange=offsetValue[i], relative=True)
