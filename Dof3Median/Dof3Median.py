import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# Dof3Median
#

class Dof3Median(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Dof3Median" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Tracking Analysis"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = ""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = ""
    self.logic = None

#
# Dof3MedianWidget
#

class Dof3MedianWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # parameters area
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # transform of interest selector
    self.transformOfInterestSelectorLabel = qt.QLabel()
    self.transformOfInterestSelectorLabel.setText( "Transform of Interest: " )
    self.transformOfInterestSelector = slicer.qMRMLNodeComboBox()
    self.transformOfInterestSelector.nodeTypes = ( ["vtkMRMLTransformNode"] )
    self.transformOfInterestSelector.noneEnabled = False
    self.transformOfInterestSelector.addEnabled = False
    self.transformOfInterestSelector.removeEnabled = True
    self.transformOfInterestSelector.setMRMLScene( slicer.mrmlScene )
    self.transformOfInterestSelector.setToolTip( "Pick transform of interest (e.g., optical tracker)" )
    parametersFormLayout.addRow(self.transformOfInterestSelectorLabel, self.transformOfInterestSelector)

    # num points selector
    self.numPointsSliderWidget = ctk.ctkSliderWidget()
    self.numPointsSliderWidget.singleStep = 1
    self.numPointsSliderWidget.minimum = 10
    self.numPointsSliderWidget.maximum = 300
    self.numPointsSliderWidget.value = 5
    self.numPointsSliderWidget.setToolTip("Set the number of points to monitor the transform for.")
    parametersFormLayout.addRow("Num Points:", self.numPointsSliderWidget)

    # results form
    resultsCollapsibleButton = ctk.ctkCollapsibleButton()
    resultsCollapsibleButton.text = "Median 3DOF positions of most recent trial"
    self.layout.addWidget(resultsCollapsibleButton)
    resultsFormLayout = qt.QFormLayout(resultsCollapsibleButton)

    self.medianPosXLabel = qt.QLabel("Pos x (mm): ")
    self.medianPosXValueLabel = qt.QLabel()

    self.medianPosYLabel = qt.QLabel("Pos y (mm): ")
    self.medianPosYValueLabel = qt.QLabel()

    self.medianPosZLabel = qt.QLabel("Pos z (mm): ")
    self.medianPosZValueLabel = qt.QLabel()

    resultsFormLayout.addRow(self.medianPosXLabel, self.medianPosXValueLabel)
    resultsFormLayout.addRow(self.medianPosYLabel, self.medianPosYValueLabel)
    resultsFormLayout.addRow(self.medianPosZLabel, self.medianPosZValueLabel)

    # write data and results form
    writeDataCollapsibleButton = ctk.ctkCollapsibleButton()
    writeDataCollapsibleButton.text = "Write data from most recent trial to csv"
    self.layout.addWidget(writeDataCollapsibleButton)
    writeDataFormLayout = qt.QFormLayout(writeDataCollapsibleButton)

    # field of view and positions text boxes
    self.fileDirLabel = "Output Dir:"
    self.fileDirTextBox = qt.QLineEdit()
    self.trackerLabel = "Tracker:"
    self.trackerTextBox = qt.QLineEdit()
    self.fovLabel = "FOV Region:"
    self.fovTextBox = qt.QLineEdit()
    self.posLabel = "Position (#):"
    self.posTextBox = qt.QLineEdit()

    writeDataFormLayout.addRow(self.fileDirLabel, self.fileDirTextBox)
    writeDataFormLayout.addRow(self.trackerLabel, self.trackerTextBox)
    writeDataFormLayout.addRow(self.fovLabel, self.fovTextBox)
    writeDataFormLayout.addRow(self.posLabel, self.posTextBox)

    # start button
    self.startButton = qt.QPushButton("Start Sample Collection")
    self.startButton.toolTip = "Collect a sample."
    self.startButton.enabled = True
    self.layout.addWidget(self.startButton)

    # stop button
    self.stopButton = qt.QPushButton("Stop Sample Collection")
    self.stopButton.toolTip = "Collect a sample."
    self.stopButton.enabled = True
    self.layout.addWidget(self.stopButton)

    # start endless button
    self.startEndlessButton = qt.QPushButton("Start Endless Sample Collection")
    self.startEndlessButton.toolTip = "Collect samples until stop button is pressed (or 20,000 samples is reached)."
    self.startEndlessButton.enabled = True
    self.layout.addWidget(self.startEndlessButton)

    # stop endless button
    self.stopEndlessButton = qt.QPushButton("Stop Endless Sample Collection")
    self.stopEndlessButton.toolTip = "Stop collecting endless samples."
    self.stopEndlessButton.enabled = True
    self.layout.addWidget(self.stopEndlessButton)

    # connections
    self.startButton.connect('clicked(bool)', self.onStart)
    self.stopButton.connect('clicked(bool)', self.onStop)
    self.startEndlessButton.connect('clicked(bool)', self.onStartEndless)
    self.stopEndlessButton.connect('clicked(bool)', self.onStopEndless)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def updateResultsGUI(self, medianX, medianY, medianZ):
    self.medianPosXValueLabel.setText("{0:.3f}".format(medianX))
    self.medianPosYValueLabel.setText("{0:.3f}".format(medianY))
    self.medianPosZValueLabel.setText("{0:.3f}".format(medianZ))

  def onStart(self):
    self.logic = Dof3MedianLogic()
    transformOfInterest = self.transformOfInterestSelector.currentNode()
    numPoints = self.numPointsSliderWidget.value
    dirPath = str(self.fileDirTextBox.text)
    tracker = str(self.trackerTextBox.text)
    fov = str(self.fovTextBox.text)
    position = str(self.posTextBox.text)
    filestring = dirPath + tracker + "_" + fov + position + ".csv"
    self.logic.run(transformOfInterest, numPoints, filestring, self.updateResultsGUI)

  def onStop(self):
    self.logic.stop()

  def onStartEndless(self):
    self.logic = Dof3MedianLogic()
    transformOfInterest = self.transformOfInterestSelector.currentNode()
    numPoints = 20000
    dirPath = str(self.fileDirTextBox.text)
    tracker = str(self.trackerTextBox.text)
    fov = str(self.fovTextBox.text)
    position = str(self.posTextBox.text)
    filestring = dirPath + tracker + "_" + fov + position + ".csv"
    self.logic.run(transformOfInterest, numPoints, filestring, self.updateResultsGUI)

  
  def onStopEndless(self):
    self.logic.stopEndless()


#
# Dof3MedianLogic
#

class Dof3MedianLogic(ScriptedLoadableModuleLogic):
  def __init__(self, parent = None):
    ScriptedLoadableModuleLogic.__init__(self, parent)
    self.transformNodeObserverTags = []
    self.transformOfInterestNode = None
    self.numPoints = 0
    self.counter = 0
    self.xPosList = []
    self.yPosList = []
    self.zPosList = []

  def addObservers(self):
    transformModifiedEvent = 15000
    transformNode = self.transformOfInterestNode
    while transformNode:
      print "Add observer to {0}".format(transformNode.GetName())
      self.transformNodeObserverTags.append([transformNode, transformNode.AddObserver(transformModifiedEvent, self.onTransformOfInterestNodeModified)])
      transformNode = transformNode.GetParentTransformNode()

  def removeObservers(self):
    print "Remove observers"
    for nodeTagPair in self.transformNodeObserverTags:
      nodeTagPair[0].RemoveObserver(nodeTagPair[1])

  def outputResults(self):
    import numpy
    import csv
    # compute medians and show in GUI
    medianX = numpy.median(numpy.array(self.xPosList))
    medianY = numpy.median(numpy.array(self.yPosList))
    medianZ = numpy.median(numpy.array(self.zPosList))
    self.updateResultsGUI(medianX, medianY, medianZ)
    # write data and medians to csv file
    csv = open(self.filestring, "w")
    csv.write("DATA MEDIANS:\n")
    csv.write("Med X,{:f}\n".format(medianX))
    csv.write("Med Y,{:f}\n".format(medianY))
    csv.write("Med Z,{:f}\n".format(medianZ))
    csv.write("\nRAW DATA:\n")
    csv.write("Point Index, X Pos, Y Pos, Z Pos\n")
    for index in range(0, len(self.xPosList)):
      x = self.xPosList[index]
      y = self.yPosList[index]
      z = self.zPosList[index]
      row = "{:d},{:f},{:f},{:f}\n".format(index, x ,y, z)
      csv.write(row)
    csv.close()

  def onTransformOfInterestNodeModified(self, observer, eventId):
    if (self.counter == self.numPoints):
      print("end of points")
      self.stop()
      self.outputResults()
    else:
      transformOfInterest = vtk.vtkMatrix4x4()
      self.transformOfInterestNode.GetMatrixTransformToWorld(transformOfInterest)
      self.xPosList.append(transformOfInterest.GetElement(0,3))
      self.yPosList.append(transformOfInterest.GetElement(1,3))
      self.zPosList.append(transformOfInterest.GetElement(2,3))
      self.counter += 1

  def run(self, transformOfInterest, numPoints, filestring, updateResultsGUI):
    self.transformNodeObserverTags = []
    self.updateResultsGUI = updateResultsGUI
    self.filestring = filestring
    self.transformOfInterestNode = transformOfInterest
    self.numPoints = numPoints
    self.counter = 0
    self.xPosList = []
    self.yPosList = []
    self.zPosList = []
    # start the updates
    self.addObservers()
    self.onTransformOfInterestNodeModified(0,0)
    return True

  def stop(self):
    self.removeObservers()

  def stopEndless(self):
      print("end of points")
      self.stop()
      self.outputResults()


class Dof3MedianTest(ScriptedLoadableModuleTest):
  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Dof3Median1()

  def test_Dof3Median1(self):
    self.delayDisplay('Test passed!')
