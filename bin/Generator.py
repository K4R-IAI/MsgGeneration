import numpy as np
import os
import tkinter as tk
from tkinter import filedialog

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



def MakeReadableArray(MsgContent):
    # Layout for readable array: VariableName, VariableType, Variable IsArray, JsonType, VariableHasDefault, VariableDefault
    OutArray = []
    for i in range(0, len(MsgContent)):
        SplitLine = MsgContent[i].split(' ')
        NewVariable = [0,0,0,0,0]
        if(SplitLine[1].count('=') >= 1):
            NewVariable[4] = True
            NewVariable.append(SplitLine[1].split('=')[-1])
            NewVariable[0] = SplitLine[1].split('=')[0]
        else:
            NewVariable[4] = False
            NewVariable[0] = SplitLine[1]

        if(SplitLine[0][-2:] == '[]'):
            NewVariable[2] = True
            if(SplitLine[0][:-2] in ConversionChart[:,0]):
                LocalCC = ConversionChart[:,0].tolist()
                NewVariable[1] = ConversionChart[LocalCC.index(SplitLine[0][:-2])][1]
            elif(SplitLine[0][:-2] not in BaseTypes):
                NewVariable[1] = SplitLine[0][:-2].replace('/','::')
            else:
                NewVariable[1] = SplitLine[0][:-2]
        else:
            NewVariable[2] = False
            if(SplitLine[0] in ConversionChart[:,0]):
                LocalCC = ConversionChart[:,0].tolist()
                NewVariable[1] = ConversionChart[LocalCC.index(SplitLine[0])][1]
            elif(SplitLine[0] not in BaseTypes):
                NewVariable[1] = SplitLine[0].replace('/','::')
            else:
                NewVariable[1] = SplitLine[0]
        if(NewVariable[1] in JsonTypes[:,0]):
            LocalJT = JsonTypes[:,0].tolist()
            NewVariable[3] = JsonTypes[LocalJT.index(NewVariable[1])][1]
        else:
            NewVariable[3] = 'ObjectField'
        OutArray.append(NewVariable)
    return OutArray
        


def GenIncludes(Variables):
    IncludeList = ["#pragma once\n\n", "#include ROSBridgeMsg.h\n\n"]
    for Variable in Variables:
        if(not(Variable[1] in BaseTypes or Variable[1] in ConversionChart[:,1])):
            IncludeList.append('#include "' + Variable[1].replace('::', '/') + '.h"\n')       
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

def GenPrivateVariables(Variables):
    PrivateVariables = []  
    for Variable in Variables: 
        Line = ''
        if(Variable[2] == True):
            Line = Line + 'TArray<' + Variable[1] + '> '
        else:
            Line = Line + Variable[1] + ' '
        Line = Line + Variable[0]
        if(Variable[4] == True):
            Line = Line + ' = ' + Variable[5]
        Line = Line + ';\n'
        PrivateVariables.append(Line)

    return Indent(PrivateVariables, 2)

def GenConstructors(Variables, ClassName, FullPath):
    Constructors = []
    Constructors.append(ClassName + '()\n')
    Constructors.append('{\n')
    Constructors.append('\tMsgType = "' + FullPath.split('.')[0] + '";\n')
    Constructors.append('}\n\n')

    Constructors.append(ClassName + '\n')
    Constructors.append('(\n')
    for Variable in Variables:
        if(Variable[2] == True):
            Constructors.append('\tconst TArray<' + Variable[1] + '>& In' + Variable[0] + ',\n')
        else:
            Constructors.append('\t'+ Variable[1] + ' In' + Variable[0] + ',\n')
    Constructors[-1] = Constructors[-1].replace(',', '')
    Constructors.append('):\n')

    for Variable in Variables:
        if(Variable[4] == True):
            Constructors.append('\t' + Variable[0] + '(In' + Variable[0] + ' = ' + Variable[5] +'),\n')
        else:
            Constructors.append('\t' + Variable[0] + '(In' + Variable[0] + '),\n')
    Constructors[-1] = Constructors[-1].replace(',', '')
    Constructors.append('{\n')
    Constructors.append('\tMsgType = "' + FullPath.split('.')[0] + '";\n')
    Constructors.append('}\n\n')

    Constructors.append('~' + ClassName + '() override {}\n\n')

    return Indent(Constructors, 2)

def GenGettersAndSetters(Variables):
    GettersAndSetters = []
    # Getters
    for Variable in Variables:
        if(Variable[2] == True):
            GettersAndSetters.append('TArray<' + Variable[1] + '> Get' + Variable[0] + '() const\n')
        else:
            GettersAndSetters.append(Variable[1] + ' Get' + Variable[0] + '() const\n')
        GettersAndSetters.append('}\n')
        GettersAndSetters.append('\treturn ' + Variable[0] + ';\n')
        GettersAndSetters.append('}\n\n')

    # Setters
    for Variable in Variables:
        if(Variable[2] == True):
            GettersAndSetters.append('void Set' + Variable[0] + '(TArray<' + Variable[1] + '>& In' + Variable[0] + ')\n')
        else:
            GettersAndSetters.append('void Set' + Variable[0] + '(' + Variable[1] + ' In' + Variable[0] + ')\n')
        GettersAndSetters.append('}\n')
        GettersAndSetters.append('\t' + Variable[0] + ' = In' + Variable[0] + ';\n')
        GettersAndSetters.append('}\n\n')

    return Indent(GettersAndSetters,2)


def GenFromJson(Variables):
    FromJson = []
    FromJson.append('virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override\n')
    FromJson.append('{\n')
    ArrayFlag = False

    for Variable in Variables:
        if(Variable[2] == False):
            if(Variable[3] == 'ObjectField'):
                FromJson.append('\t' + Variable[0] + ' = ' + Variable[1] + '::GetFromJson(JsonObject->GetObjectField(TEXT("' + Variable[0].lower() + '")));\n\n')
            else:
                FromJson.append('\t' + Variable[0] + ' = JsonObject->Get' + Variable[3] + '(TEXT("' + Variable[0].lower() + '"));\n\n')
        else:
            if(not ArrayFlag):
                FromJson.append('\t' + 'TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;\n\n')
                ArrayFlag = True   
            FromJson.append('\t' + Variable[0] + '.Empty();\n')
            FromJson.append('\t' + 'ValuesPtrArr = JsonObject->GetArrayField(TEXT("' + Variable[0].lower() + '"));\n')
            FromJson.append('\t' + 'for (auto &ptr : ValuesPtrArr)\n')
            if(Variable[3] == 'ObjectField'):
                FromJson.append('\t' + '\t' + Variable[0] + '.Add(' + Variable[1] + '::GetFromJson(ptr->AsObject()));\n\n')
            else:
                FromJson.append('\t' + '\t' + Variable[0] + '.Add(ptr->As' + Variable[3][:-5] + '());\n\n')

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
        if(Variable[2] == True):
            ToJsonObject.append('\tTArray<TSharedPtr<FJsonValue>> ' + Variable[0] + 'Array;\n')
            ToJsonObject.append('\tfor (auto &val : ' + Variable[0] + ')\n')
            ToJsonObject.append('\t\t' + Variable[0] + 'Array.Add(MakeShareable(new FJsonValue' + Variable[3][:-5] + '(val)));\n')
            ToJsonObject.append('\tObject->SetArrayField(TEXT("' + Variable[0].lower() + '"), ' + Variable[0] + 'Array);\n' )
        else:
            if(Variable[3] == 'ObjectField'):
                ToJsonObject.append('\tObject->SetObjectField(TEXT("' + Variable[0].lower() + '"), ' + Variable[0] + '.ToJsonObject());\n')
            else:
                ToJsonObject.append('\tObject->Set' + Variable[3] + '(TEXT("' + Variable[0].lower() + '"), ' + Variable[0] + ');\n')

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

root = tk.Tk()
root.withdraw()
dirname = filedialog.askdirectory(initialdir='../templates/', title ='Please select where your templates are located.')

for root, dirs, files in os.walk(dirname):
    for filename in files:
        if(filename[-3:] == 'txt'):
            FullPath = os.path.join(root, filename)
            FullPath = FullPath.replace('\\', '/')
            MsgFile = open(FullPath)
            MsgContent = MsgFile.readlines()
            MsgContent = RemoveParagraphs(MsgContent)
            MsgName = MsgFile.name.split('.')[0].split('/')[-1]
            print(MsgName)
            MsgFileName = MsgFile.name
            MsgFileName = MsgFileName.replace(dirname + '/', '')
            print(MsgFileName)
            MsgFile.close()
            Variables = MakeReadableArray(MsgContent)

            OutputArray = []

            OutputArray.append(GenIncludes(Variables))
            OutputArray.append(GenNameSpace(MsgFileName))
            OutputArray.append(GenClass(MsgName))
            OutputArray.append(GenPrivateVariables(Variables))
            OutputArray.append(Indent(['public:\n'], 1))
            OutputArray.append(GenConstructors(Variables, MsgName, MsgFileName))
            OutputArray.append(GenGettersAndSetters(Variables))
            OutputArray.append(GenFromJson(Variables))
            OutputArray.append(GenGetFromJson(MsgName))
            OutputArray.append(GenToJsonObject(Variables))
            OutputArray.append(GenToYamlString())
            OutputArray.append(Indent(['};\n'], 1))
            OutputArray.append(['}'])

            Output = open(dirname + '/' + MsgFileName.split('.')[0] + '.h', 'w')

            for Block in OutputArray:
                Output.writelines(Block)
            
            Output.close()





