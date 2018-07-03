import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
import argparse as ap

class Variable:
    def ConvertName(self, OriginalName):
        ConvertedName = OriginalName.replace('_', ' ').title().replace(' ', '')
        return ConvertedName

    def __init__(self):
        self._OriginalName = ''
        self._Name = ''
        self._Type = ''
        self._IsArray = False
        self._JsonType = ''
        self._HasDefault = False
        self._DefaultValue = ''

    def SetOriginalName(self, OriginalName):
        self._OriginalName = OriginalName.lower()
        if(OriginalName.count('_') >= 1):
            self._Name = self.ConvertName(OriginalName)
        else:
            self._Name = OriginalName
    def SetType(self, Type):
        self._Type = Type
    def SetIsArray(self, IsArray):
        self._IsArray = IsArray
    def SetJsonType(self, JsonType):
        self._JsonType = JsonType
    def SetHasDefault(self, HasDefault):
        self._HasDefault = HasDefault
    def SetDefaultValue(self, DefaultValue):
        self._DefaultValue = DefaultValue

    def GetName(self):
        return self._Name
    def GetOriginalName(self):
        return self._OriginalName
    def GetType(self):
        return self._Type
    def IsArray(self):
        return self._IsArray
    def GetJsonType(self):
        return self._JsonType
    def HasDefault(self):
        return self._HasDefault
    def GetDefaultValue(self):
        return self._DefaultValue

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
    IndentString = '\t'*Count
    
    for Index in Array:
        if(not type(Index) is list):
            IndentedArray.append(IndentString + Index)

    return IndentedArray  

bt = open("../config/BaseTypes.txt")
BaseTypes = bt.readline().split(' ')
bt.close()

cc = open("../config/ConversionChart.txt")
CleanedCC = RemoveParagraphs(cc.readlines())
ConversionChart = []
for Rule in CleanedCC:
    ConversionChart.append(Rule.split(' '))
ConversionChart = np.array(ConversionChart)
cc.close()

jt = open("../config/MatchJsonTypes.txt")
CleanedJT = RemoveParagraphs(jt.readlines())
JsonTypes = []
for Match in CleanedJT:
    JsonTypes.append(Match.split(' '))
JsonTypes = np.array(JsonTypes)
jt.close()



def MakeVariableArray(MsgContent):
    OutArray = []
    for i in range(0, len(MsgContent)):
        if(MsgContent[i].count('#') >= 1):  
            SplitLine = MsgContent[i].split('#')[0].rstrip().split(' ')
        else:
            SplitLine = MsgContent[i].rstrip().split(' ')
        NewVariable = Variable()
        
        if(SplitLine[1].count('=') >= 1): 
            NewVariable.SetHasDefault = True
            NewVariable.SetDefaultValue(SplitLine[1].split('=')[-1])
            NewVariable.SetOriginalName(SplitLine[1].split('=')[0])
        else:
            NewVariable.SetHasDefault(False)
            NewVariable.SetOriginalName(SplitLine[1])

        if(SplitLine[0][-2:] == '[]'):
            NewVariable.SetIsArray(True)
            if(SplitLine[0][:-2] in ConversionChart[:,0]):
                LocalCC = ConversionChart[:,0].tolist()
                NewVariable.SetType( ConversionChart[LocalCC.index(SplitLine[0][:-2])][1] )
            elif(SplitLine[0][:-2] not in BaseTypes):
                NewVariable.SetType( SplitLine[0][:-2].replace('/','::') )
            else:
                NewVariable.SetType( SplitLine[0][:-2] )
        else:
            NewVariable.SetIsArray(False)
            if(SplitLine[0] in ConversionChart[:,0]):
                LocalCC = ConversionChart[:,0].tolist()
                NewVariable.SetType( ConversionChart[LocalCC.index(SplitLine[0])][1] )
            elif(SplitLine[0] not in BaseTypes):
                NewVariable.SetType( SplitLine[0].replace('/','::') )
            else:
                NewVariable.SetType( SplitLine[0] )
        if(NewVariable.GetType() in JsonTypes[:,0]):
            LocalJT = JsonTypes[:,0].tolist()
            NewVariable.SetJsonType( JsonTypes[LocalJT.index(NewVariable.GetType())][1] )
        else:
            NewVariable.SetJsonType( 'ObjectField' )
        OutArray.append(NewVariable)
    return OutArray
        


def GenIncludes(Variables):
    IncludeList = ["#pragma once\n\n", "#include ROSBridgeMsg.h\n\n"]
    for Variable in Variables:
        if(not(Variable.GetType() in BaseTypes or Variable.GetType() in ConversionChart[:,1])):
            IncludeList.append('#include "' + Variable.GetType().replace('::', '/') + '.h"\n')       
    return IncludeList


def GenNameSpace(Name):
    
    NameSpace = ['\nnamespace ' + Name + '\n']
    
    NameSpace.append('{\n')
    return NameSpace


def GenClass(Name):
    Class = ['class ' + Name + ' : public FROSBridgeMsg\n']
    Class.append('{\n')
    Class = Indent(Class, 1)
    return Class

def GenPrivateVariables(Variables):
    PrivateVariables = []  
    for Variable in Variables: 
        Line = ''
        if(Variable.IsArray()):
            Line = Line + 'TArray<' + Variable.GetType() + '> '
        else:
            Line = Line + Variable.GetType() + ' '
        Line = Line + Variable.GetName()
        if(Variable.HasDefault()):
            Line = Line + ' = ' + Variable.GetDefaultValue()
        Line = Line + ';\n'
        PrivateVariables.append(Line)

    return Indent(PrivateVariables, 2)

def GenConstructors(Variables, ClassName, Namespace, MsgName):
    Constructors = []
    Constructors.append(ClassName + '()\n')
    Constructors.append('{\n')
    Constructors.append('\tMsgType = "' + Namespace + '/' + MsgName + '";\n')
    Constructors.append('}\n\n')

    Constructors.append(ClassName + '\n')
    Constructors.append('(\n')
    for Variable in Variables:
        if(Variable.IsArray()):
            Constructors.append('\tconst TArray<' + Variable.GetType() + '>& In' + Variable.GetName() + ',\n')
        else:
            Constructors.append('\t'+ Variable.GetType() + ' In' + Variable.GetName() + ',\n')
    Constructors[-1] = Constructors[-1].replace(',', '')
    Constructors.append('):\n')

    for Variable in Variables:
        if(Variable.HasDefault()):
            Constructors.append('\t' + Variable.GetName() + '(In' + Variable.GetName() + ' = ' + Variable.GetDefaultValue() +'),\n')
        else:
            Constructors.append('\t' + Variable.GetName() + '(In' + Variable.GetName() + '),\n')
    Constructors[-1] = Constructors[-1].replace(',', '')
    Constructors.append('{\n')
    Constructors.append('\tMsgType = "' + Namespace + '/' + MsgName + '";\n')
    Constructors.append('}\n\n')

    Constructors.append('~' + ClassName + '() override {}\n\n')

    return Indent(Constructors, 2)

def GenGettersAndSetters(Variables):
    GettersAndSetters = []
    # Getters
    for Variable in Variables:
        if(Variable.IsArray()):
            GettersAndSetters.append('TArray<' + Variable.GetType() + '> Get' + Variable.GetName() + '() const\n')
        else:
            GettersAndSetters.append(Variable.GetType() + ' Get' + Variable.GetName() + '() const\n')
        GettersAndSetters.append('}\n')
        GettersAndSetters.append('\treturn ' + Variable.GetName() + ';\n')
        GettersAndSetters.append('}\n\n')

    # Setters
    for Variable in Variables:
        if(Variable.IsArray()):
            GettersAndSetters.append('void Set' + Variable.GetName() + '(TArray<' + Variable.GetType() + '>& In' + Variable.GetName() + ')\n')
        else:
            GettersAndSetters.append('void Set' + Variable.GetName() + '(' + Variable.GetType() + ' In' + Variable.GetName() + ')\n')
        GettersAndSetters.append('}\n')
        GettersAndSetters.append('\t' + Variable.GetName() + ' = In' + Variable.GetName() + ';\n')
        GettersAndSetters.append('}\n\n')

    return Indent(GettersAndSetters,2)


def GenFromJson(Variables):
    FromJson = []
    FromJson.append('virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override\n')
    FromJson.append('{\n')
    ArrayFlag = False

    for Variable in Variables:
        if(not Variable.IsArray()):
            if(Variable.GetJsonType() == 'ObjectField'):
                FromJson.append('\t' + Variable.GetName() + ' = ' + Variable.GetType() + '::GetFromJson(JsonObject->GetObjectField(TEXT("' + Variable.GetOriginalName() + '")));\n\n')
            else:
                FromJson.append('\t' + Variable.GetName() + ' = JsonObject->Get' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"));\n\n')
        else:
            if(not ArrayFlag):
                FromJson.append('\t' + 'TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;\n\n')
                ArrayFlag = True   
            FromJson.append('\t' + Variable.GetName() + '.Empty();\n')
            FromJson.append('\t' + 'ValuesPtrArr = JsonObject->GetArrayField(TEXT("' + Variable.GetOriginalName() + '"));\n')
            FromJson.append('\t' + 'for (auto &ptr : ValuesPtrArr)\n')
            if(Variable.GetJsonType() == 'ObjectField'):
                FromJson.append('\t' + '\t' + Variable.GetName() + '.Add(' + Variable.GetType() + '::GetFromJson(ptr->AsObject()));\n\n')
            else:
                FromJson.append('\t' + '\t' + Variable.GetName() + '.Add(ptr->As' + Variable.GetJsonType()[:-5] + '());\n\n')

    FromJson.append('}\n\n')
            
    return Indent(FromJson, 2)

def GenGetFromJson(ClassName):
    GetFromJson = []
    GetFromJson.append('static ' + ClassName + ' GetFromJson(TSharedPtr<FJsonObject> JsonObject)\n')
    GetFromJson.append('{\n')
    GetFromJson.append('\t'+ ClassName + ' Result;\n')
    GetFromJson.append('\t'+ 'Result.FromJson(JsonObject);\n')
    GetFromJson.append('\t'+ 'return Result;\n')
    GetFromJson.append('}\n\n')
    
    return Indent(GetFromJson, 2)

def GenToJsonObject(Variables):
    ToJsonObject = []
    ToJsonObject.append('virtual TSharedPtr<FJsonObject> ToJsonObject() const override\n')
    ToJsonObject.append('{\n')
    ToJsonObject.append('\tTSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());\n\n')

    for Variable in Variables:
        if(Variable.IsArray()):
            ToJsonObject.append('\tTArray<TSharedPtr<FJsonValue>> ' + Variable.GetName() + 'Array;\n')
            ToJsonObject.append('\tfor (auto &val : ' + Variable.GetName() + ')\n')
            ToJsonObject.append('\t\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FJsonValue' + Variable.GetJsonType()[:-5] + '(val)));\n')
            ToJsonObject.append('\tObject->SetArrayField(TEXT("' + Variable.GetName().lower() + '"), ' + Variable.GetName() + 'Array);\n' )
        else:
            if(Variable.GetJsonType() == 'ObjectField'):
                ToJsonObject.append('\tObject->SetObjectField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + '.ToJsonObject());\n')
            else:
                ToJsonObject.append('\tObject->Set' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + ');\n')

    ToJsonObject.append('\treturn Object;\n')
    ToJsonObject.append('}\n')
    return Indent(ToJsonObject, 2)

def GenToYamlString():
    ToYamlString = []
    ToYamlString.append('virtual FString ToYamlString() const override\n')
    ToYamlString.append('{\n')
    ToYamlString.append('\tFString OutputString;\n')
    ToYamlString.append('\tTSharedRef< TJsonWriter<> > Writer = TJsonWriterFactory<>::Create(&OutputString);\n')
    ToYamlString.append('\tFJsonSerializer::Serialize(ToJsonObject().ToSharedRef(), Writer);\n')
    ToYamlString.append('\treturn OutputString;\n')
    ToYamlString.append('}\n')
    return Indent(ToYamlString, 2)



parser = ap.ArgumentParser(description='Generates UROSBridge compatible C++ files from msg files in a ROS Package.')
parser.add_argument('--path', '-p', help='Provide the path to the ROS Package you want to generate the C++ files for.')
parser.add_argument('--usegui', '-g', action='store_true', help='Use this if you want to open a filedialog to pick your path.')
parser.add_argument('--msgfolder', '-mf', help='Use this if instead of a ROS Package you are selecting a folder directly containing the .msg files. Requires a namespace to be provided.')

args = parser.parse_args()


if(args.path and not args.usegui):
    dirname = args.path
elif(args.usegui and args.path):
    tk.Tk().withdraw()
    dirname = filedialog.askdirectory(initialdir=args.path, title ='Please select a ROS Package.')
elif(args.usegui and not args.path):
    tk.Tk().withdraw()
    dirname = filedialog.askdirectory(initialdir=os.path.join(os.path.dirname(__file__), '..'), title ='Please select a ROS Package.')
else:
    parser.error('A path needs to be specified. Use the -p option to specify a path or see --help for other options.')

if(not args.msgfolder):
    msgdir = os.path.join(dirname, 'msg').replace('/','\\')
else:
    msgdir = dirname

for file in os.listdir(msgdir):
    if(file[-3:] == 'msg'):
        FullPath = os.path.join(msgdir, file)
        FullPath = FullPath.replace('\\', '/')
        MsgFile = open(FullPath)
        MsgContent = MsgFile.readlines()
        MsgContent = RemoveParagraphs(MsgContent)
        MsgName = MsgFile.name.split('.')[0].split('/')[-1]
        if(args.msgfolder):
            PackageName = args.msgfolder
        else:
            PackageName = os.path.dirname(msgdir).replace(os.path.dirname(os.path.dirname(msgdir)) + '\\', '')
        MsgFile.close()
        Variables = MakeVariableArray(MsgContent)

        OutputArray = []

        OutputArray.append(GenIncludes(Variables))
        OutputArray.append(GenNameSpace(PackageName))
        OutputArray.append(GenClass(MsgName))
        OutputArray.append(GenPrivateVariables(Variables))
        OutputArray.append(Indent(['public:\n'], 1))
        OutputArray.append(GenConstructors(Variables, MsgName, PackageName, MsgName))
        OutputArray.append(GenGettersAndSetters(Variables))
        OutputArray.append(GenFromJson(Variables))
        OutputArray.append(GenGetFromJson(MsgName))
        OutputArray.append(GenToJsonObject(Variables))
        OutputArray.append(GenToYamlString())
        OutputArray.append(Indent(['};\n'], 1))
        OutputArray.append(['}'])

        if(not os.path.isdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/')):
            os.mkdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/')
        if(not os.path.isdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName)):
            os.mkdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName)
        if(not os.path.isdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName + '/msg')):
            os.mkdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName + '/msg/')
        Output = open(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName + '/msg/' + SrvName + '.h', 'w')

        for Block in OutputArray:
            Output.writelines(Block)
            
        Output.close()





