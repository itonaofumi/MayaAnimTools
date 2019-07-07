# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.api.OpenMaya as om

import os
import csv

def exportMarkers():
    # 出力するマーカーを選択してから実行する

    # 出力するマーカーの取得
    selectedItems = cmds.ls( selection=True )

    # csvファイルを開く（なければ作る）
    csvPath = "C:/Users/0300091280/Desktop/testmarkers.csv"
    if not (cmds.file(csvPath, query=True, exists=True)):
        csvFile = open(csvPath, 'w', os.O_CREAT)
    else:
        csvFile = open(csvPath, 'w')
    writer = csv.writer(csvFile, lineterminator='\n')

    startFrame = int(cmds.playbackOptions(q=True, min=True))
    endFrame = int(cmds.playbackOptions(q=True, max=True))

    for i in range(startFrame, endFrame, 1):
        cmds.currentTime(i, edit=True )
        animList = []
        
        for item in selectedItems:
            transx = cmds.getAttr(item + '.tx')
            transy = cmds.getAttr(item + '.ty')
            transz = cmds.getAttr(item + '.tz')

            animList.append(transx)
            animList.append(transy)
            animList.append(transz)

        writer.writerow(animList)

    csvFile.close()

def exportMatrix(): 

    # select export joints
    sList = om.MSelectionList()
    sList.add('Hips')
    sList.add('Spine')
    sList.add('Spine1')
    sList.add('Spine2')
    sList.add('Spine3')
    sList.add('Neck')
    sList.add('Neck1')
    sList.add('Head')
    sList.add('RightShoulder')
    sList.add('RightArm')
    sList.add('RightForeArm')
    sList.add('RightHand')
    sList.add('LeftShoulder')
    sList.add('LeftArm')
    sList.add('LeftForeArm')
    sList.add('LeftHand')
    sList.add('RightUpLeg')
    sList.add('RightLeg')
    sList.add('RightForeFoot')
    sList.add('RightToeBase')
    sList.add('LeftUpLeg')
    sList.add('LeftLeg')
    sList.add('LeftForeFoot')
    sList.add('LeftToeBase')
     
    # csvファイルを開く（なければ作る）
    csvPath = "C:/Users/0300091280/Desktop/joints.csv"
    if not (cmds.file(csvPath, query=True, exists=True)):
        csvFile = open(csvPath, 'w', os.O_CREAT)
    else:
        csvFile = open(csvPath, 'w')
    writer = csv.writer(csvFile, lineterminator='\n')
     
    # 先に全ジョイントのMFnTransformをリスト化しとく
    lsFnTrs = list()
    iter = om.MItSelectionList(sList)
     
    while not iter.isDone():
        dagPath = iter.getDagPath()
        fnTrs = om.MFnTransform(dagPath)
        lsFnTrs.append(fnTrs)
        iter.next()
     
    # 描画停止
    cmds.refresh(suspend=True)
     
    # 各ジョイントのマトリクスを一行に並べ、csvにフレームぶん書き出す
    startFrame = int(cmds.playbackOptions(q=True, min=True))
    endFrame = int(cmds.playbackOptions(q=True, max=True))
     
    for i in range(startFrame, endFrame, 1):
        cmds.currentTime(i, edit=True)
        columns = []
         
        for c_fnTrs in lsFnTrs:
             
            # 各ジョイントのマトリクスを抜き出す
            dagMatrix = list(c_fnTrs.transformation().asMatrix().homogenize())
             
            # マトリクス内の不要な0001を消す
            del dagMatrix[-1]
            del dagMatrix[11]
            del dagMatrix[7]
            del dagMatrix[3]
             
            # 各ジョイントのマトリクスをつなげていく
            columns.extend(dagMatrix)
     
        writer.writerow(columns)
         
    csvFile.close()
     
    # 描画再開
    cmds.refresh(suspend=False)
    cmds.refresh(force=True)

def importMatrix():

    # autoKeyFrameが有効だと処理が重くなるため、autoKeyFrameをオフにする
    # あとで状態を復元するためにautoKeyFrameが有効かどうかを保存しておく
    isAutoKeyFrame =  cmds.autoKeyframe(query=True, state=True)
    cmds.autoKeyframe(state=False)
     
    # ジョイントを選択
    cmds.select(clear=True)
    cmds.select("|Hips1", add=True)
    cmds.select("|Spine", add=True)
    cmds.select("|Spine1", add=True)
    cmds.select("|Spine2", add=True)
    cmds.select("|Spine3", add=True)
    cmds.select("|Neck", add=True)
    cmds.select("|Neck1", add=True)
    cmds.select("|Head", add=True)
    cmds.select("|RightShoulder", add=True)
    cmds.select("|RightArm", add=True)
    cmds.select("|RightForeArm", add=True)
    cmds.select("|RightHand", add=True)
    cmds.select("|LeftShoulder", add=True)
    cmds.select("|LeftArm", add=True)
    cmds.select("|LeftForeArm", add=True)
    cmds.select("|LeftHand", add=True)
    cmds.select("|RightUpLeg", add=True)
    cmds.select("|RightLeg", add=True)
    cmds.select("|RightForeFoot", add=True)
    cmds.select("|RightToeBase", add=True)
    cmds.select("|LeftUpLeg", add=True)
    cmds.select("|LeftLeg", add=True)
    cmds.select("|LeftForeFoot", add=True)
    cmds.select("|LeftToeBase", add=True)

    selectedItem = cmds.ls(sl=1, long=1)
    sList = om.MGlobal.getActiveSelectionList()

    # 先に全ジョイントのMFnTransformをリスト化しとく
    lsFnTrs = list()
    iter = om.MItSelectionList(sList)
    while not iter.isDone():
        dagPath = iter.getDagPath()
        fnTrs = om.MFnTransform(dagPath)
        lsFnTrs.append(fnTrs)
        iter.next()

    # csvを読み込む
    o_file = open("C:/Users/0300091280/Desktop/predict.csv", 'r')
    reader = csv.reader(o_file)
    setFrame = int(cmds.playbackOptions(q=True, min=True))

    # scriptEditorへの出力を抑制
    cmds.scriptEditorInfo(suppressInfo=True, suppressResults=True) 

    for row in reader:
        offset = 0
        for i, c_fnTrs in enumerate(lsFnTrs):
            mat = om.MMatrix([float(row[offset+0]), float(row[offset+1]), float(row[offset+2]), 0.0,
                              float(row[offset+3]), float(row[offset+4]), float(row[offset+5]), 0.0,
                              float(row[offset+6]), float(row[offset+7]), float(row[offset+8]), 0.0,
                              float(row[offset+9]), float(row[offset+10]), float(row[offset+11]), 1.0])
            mat = om.MTransformationMatrix(mat)
            c_fnTrs.setTransformation(mat)
            cmds.setKeyframe(selectedItem[i], time=(setFrame, setFrame))
            offset += 12
        setFrame += 1
    o_file.close()

    if isAutoKeyFrame:
        cmds.autoKeyframe(state=True)