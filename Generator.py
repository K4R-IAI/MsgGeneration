import numpy as np

def RemoveParagraphs(RawDocument):
    CleanedArray = []
    for Element in RawDocument:
        if(Element.endswith('\n')):
            CleanedArray.append(Element[:-1])
        else:
            CleanedArray.append(Element)
    return CleanedArray


def Indent(Array, Count):
    IndentedArray = []
    Indent = '\t'*Count
    
    for Index in Array:
        IndentedArray.append(Indent + Index)

    return IndentedArray


bt = open("BaseTypes.txt")
BaseTypes = bt.readline().split(' ')
bt.close()

cc = open("ConversionChart.txt")
CleanedCC = RemoveParagraphs(cc.readlines())
ConversionChart = []
for Rule in CleanedCC:
    ConversionChart.append(Rule.split(' '))
ConversionChart = np.array(ConversionChart)
cc.close()



def GenIncludes(MsgContent):
    IncludeList = ["#pragma once\n\n", "#include ROSBridgeMsg.h\n\n"]
    SplitLine = []
    for Line in MsgContent:
        SplitLine = Line.split(' ')
        if(not(SplitLine[0] in BaseTypes)):
            IncludeList.append('#include "' + SplitLine[0] + '.h"\n')       
    return IncludeList


def GenNameSpace(Name):
    NameSpace = ['\nnamespace ' + Name.split('/')[0] + '\n']
    NameSpace.append('{\n')
    return NameSpace


def GenClass(Name):
    Class = ['class ' + Name + ' : public FROSBridgeMsg\n']
    Class.append('{\n')
    Class = Indent(Class, 1)
    return Class

def GenPrivateVariables(MsgContent):
    PrivateVariables = []
    for Line in MsgContent: 
        Split = Line.split(' ')
        LocalCC = ConversionChart[:,0].tolist()
        if(Split[0] in BaseTypes):
            PrivateVariables.append(Split[0] + ' ' + Split[1].split('=')[0] + ';\n')
        elif(Split[0] in ConversionChart[:,0]):
            PrivateVariables.append(ConversionChart[LocalCC.index(Split[0])][1] + ' ' + Split[1].split('=')[0] + '\n')
        else:
            PrivateVariables.append(Split[0].replace('/', '::') + ' ' + Split[1].split('=')[0] + '\n')

    return Indent(PrivateVariables, 2)


MsgFile = open("geometry_msgs/MyCreativeMessage.txt")
MsgContent = MsgFile.readlines()
MsgContent = RemoveParagraphs(MsgContent)
MsgName = MsgFile.name.split('/')[1].split('.')[0]
MsgFileName = MsgFile.name
MsgFile.close()

OutputArray = []

OutputArray.append(GenIncludes(MsgContent))
OutputArray.append(GenNameSpace(MsgFileName))
OutputArray.append(GenClass(MsgName))
OutputArray.append(GenPrivateVariables(MsgContent))
OutputArray.append(Indent(['};\n'], 1))
OutputArray.append(['}'])

Output = open(MsgFileName.split('.')[0] + '.h', 'w')

for Block in OutputArray:
    Output.writelines(Block)
    
Output.close()





