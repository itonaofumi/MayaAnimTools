from maya import cmds
from maya import OpenMayaUI as omui
 
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__
    from shiboken import wrapInstance
 
mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)
 
class CurveFitter(QWidget):
    def __init__(self, *args, **kwargs):
        super(CurveFitter, self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setObjectName('CurveFitter_uniqueId')
        self.setWindowTitle('Curve Fitter')
        self.setGeometry(50, 50, 250, 100)
        self.initUI()
         
    def initUI(self):
        mainLayout = QVBoxLayout()
         
        # radio
        self.radioButton1 = QRadioButton('Head')
        self.radioButton2 = QRadioButton('Tail')
        self.radioButton1.setChecked(True)
 
        self.radioLayout = QHBoxLayout()
        self.radioLayout.setSpacing(10)
        self.radioLayout.addWidget(self.radioButton1)
        self.radioLayout.addWidget(self.radioButton2)
 
        mainLayout.addLayout(self.radioLayout)
 
        # button
        self.button = QPushButton('Fit', self)
        self.button.clicked.connect(self.button_onClicked)
 
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.button)
 
        mainLayout.addLayout(self.buttonLayout)
        self.setLayout(mainLayout)
 
    # 選択したカーブのインデックス、時間、値を返す
    def getCurveInfo(self, curves):
        indexs = list()
        times = list()
        values = list()
        for i, c in enumerate(curves):
            indexs.append(cmds.keyframe(c, sl=True, q=True, iv=True))
            times.append(cmds.keyframe(c, sl=True, q=True, tc=True))
            values.append(cmds.keyframe(c, q=True, valueChange=True,
                                           index=(indexs[i][0], indexs[i][-1])))
        return indexs, times, values

    # ２点を通る直線の方程式を使って直線を求める。
    # mode: 0 最初と最後のキーをつないだ直線
    # mode: 1 ２番目と最後のキーをつないだ直線
    # mode: 2 最初と最後の１つ前のキーをつないだ直線
    def startEndLine(self, keyTimes, keyValues, mode):
        lineList = list()
 
        for i in xrange(len(keyValues)):
            if mode == 0:
                x1 = keyTimes[i][0]
                x2 = keyTimes[i][-1]
                y1 = keyValues[i][0]
                y2 = keyValues[i][-1]
            elif mode == 1:
                x1 = keyTimes[i][1]
                x2 = keyTimes[i][-1]
                y1 = keyValues[i][1]
                y2 = keyValues[i][-1]
            else:
                x1 = keyTimes[i][0]
                x2 = keyTimes[i][-2]
                y1 = keyValues[i][0]
                y2 = keyValues[i][-2]
              
            a = (y2 - y1) / (x2 - x1)
            b = (x2 * y1 - x1 * y2) / (x2 - x1)
              
            y = list()
 
            for x in keyTimes[i]:
                y.append(a * x + b)
 
            lineList.append(y)
      
        return lineList
 
    # 各キーの時間における、直線との差分を求める。
    def diffFromLine(self, lineList, keyValues):
        diffList = list()
 
        for i in xrange(len(keyValues)):
            x = list()
 
            for j in xrange(len(keyValues[i])):
                x.append(keyValues[i][j] - lineList[i][j])
 
            diffList.append(x)
             
        return diffList       
 
    # 差分と、最初と最後のキーをつないだ直線の値を足す
    def addDiff(self, diffList, lineList):
        for i in xrange(len(diffList)):
            for j in xrange(len(diffList[i])):
                diffList[i][j] += lineList[i][j]
 
    # カーブを変更
    def fitCurve(self, curves, diffList, keyTimes, mode):
        for i in xrange(len(diffList)):
            for j in xrange(len(diffList[i]) - 1):
                if mode == 0 and j == 0:  # 頭合わせの場合最初のキーはスキップ
                    continue
                cmds.keyframe(curves[i], edit=True,
                              time=(keyTimes[i][j], keyTimes[i][j]),
                              valueChange=diffList[i][j], absolute=True)

    def button_onClicked(self):
        if self.radioButton1.isChecked():
            mode = 0  # 頭合わせ
        else:
            mode = 1  # 尻合わせ
  
        # グラフエディタで選択されているカーブ名を取得
        curves = cmds.keyframe(query=True, name=True)
 
        # 選択されているキーのインデックス、時間、値を取得
        keyIds, keyTimes, keyValues = self.getCurveInfo(curves)
 
        # modeに応じて直線を求める
        if mode == 0:
            lineList = self.startEndLine(keyTimes, keyValues, 1)
        else:
            lineList = self.startEndLine(keyTimes, keyValues, 2)
 
        # 直線との差分を求める
        diffList = self.diffFromLine(lineList, keyValues)
         
        # 最初と最後のキーをつないだ直線を求める
        lineList = self.startEndLine(keyTimes, keyValues, 0)
 
        # 差分と直線を足す
        self.addDiff(diffList, lineList)
 
        # カーブを変更
        cmds.undoInfo(chunkName='CurveFitter', openChunk=True)
        self.fitCurve(curves, diffList, keyTimes, mode)
        cmds.undoInfo(closeChunk=True)
 
def main():
    ui = CurveFitter()
    ui.show()
    return ui
     
if __name__ == '__main__':
    main()
