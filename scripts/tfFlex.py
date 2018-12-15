"""
tfFlex

Automatically generates flexes for TF2 items using a wrap deformer

Created by @SediSocks, based off the original MEL script by NeoDement
"""

import maya.cmds as cmds
import maya.mel as mm

def createUI():

    version = cmds.about(v=True)
    mainWindow = 'mainWindowID'

    if cmds.window(mainWindow, exists=True):
        cmds.deleteUI(mainWindow)

    window = cmds.window(mainWindow, title="tfFlex", tlb=True, s=False)
    form = cmds.formLayout(numberOfDivisions=100)

    # createWrap
    object = cmds.checkBox('wrapButton', w=147, h=34, v=True, l="Create Wrap Deformer")
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 59), (object, 'left', 18)])

    # description
    object = cmds.text(label="Select the item to be flexed first, then the base head.", ww=True, w=137, h=40)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 14), (object, 'left', 18)])

    # createDeltaMush
    if float(version) < 2016.0:
        object = cmds.checkBox('deltaButton', w=147, h=34, v=False, ed=False, l="Create DeltaMush",
                               ann="Smooths out the resulting flexes, useful for beards etc. Requires Maya 2016 or higher")
        cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 79), (object, 'left', 18)])
    elif float(version) >= 2016.0:
        object = cmds.checkBox('deltaButton', w=147, h=34, v=False, l="Create DeltaMush",
                               ann="Smooths out the resulting flexes, useful for beards etc.")
        cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 79), (object, 'left', 18)])

    # flexButton
    object = cmds.button(label="Flex!", c=flex, w=113, h=34)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 120), (object, 'left', 31)])

    # addtoshelf
    object = cmds.button(label="Add to Shelf", c=tfFlexButton, w=75, h=24)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 160), (object, 'left', 50)])
    # =========================================

    cmds.setParent('..')
    cmds.showWindow(window)
    cmds.window(mainWindow, edit=True, widthHeight=(175.0, 202.0))


def flex(self):
    selection = cmds.ls(sl=True)

    # create errors
    if len(selection) == 0:
        cmds.error("Nothing selected, first select the item to be flexed, then hold shift and select the base head")
    elif len(selection) == 1:
        cmds.error("Only 1 object selected, first select the item to be flexed, then hold shift and select the base head")
    elif len(selection) > 2:
        cmds.error("More than 2 objects selected, first select the item to be flexed, then hold shift and select the base head")

    beard = selection[0]
    head = selection[1]

    # create wrap deformer if box ticked
    if cmds.checkBox('wrapButton', q=1, v=True):
        mm.eval('doWrapArgList "2" { "1","0","0.0" };')

    # group the beard mesh so its nice and tidy
    cmds.group(beard)

    # create deltamush deformer if box ticked
    if cmds.checkBox('deltaButton', q=1, v=True):
        cmds.deltaMush(smoothingIterations=20, smoothingStep=0.8)

    # get blendshape node from selection
    blndShape = cmds.ls(*cmds.listHistory(selection[1]) or {}, type='blendShape')

    # list blendshape targets
    shapes = cmds.listAttr(blndShape[0] + ".w", m=True)

    # set eyelids to ingame default
    if 'CloseLidLo' in shapes:
        cmds.setAttr(blndShape[0] + ".CloseLidLo", .25)
        cmds.setAttr(blndShape[0] + ".CloseLidUp", .25)

    i = 10

    # duplicate each target
    for item in shapes:
        cmds.select(selection)
        cmds.setAttr(blndShape[0] + "." + item, 1)
        cmds.duplicate(head, n=item + "_head", rr=True)
        cmds.duplicate(beard, n=item, rr=True)

        cmds.select(item)
        cmds.select(item + "_head", add=True)

        # move them off to the side
        cmds.move(i, 0, 0, r=True)

        previous = item
        cmds.setAttr(blndShape[0] + "." + previous, 0)

        i += 10

    # set last target to 0
    cmds.setAttr(blndShape[0] + "." + previous, 0)


def tfFlexButton(self):
    currentShelf = cmds.tabLayout("ShelfLayout", selectTab=True, query=True)
    cmds.shelfButton(annotation='TF2 Item Flex',
                     image1='tfFlex.png',
                     imageOverlayLabel='tfFlex',
                     command='import tfFlex; reload(tfFlex); tfFlex.createUI()',
                     parent=currentShelf,
                     label='tfFlex')
