import numpy as np
import sys
import getopt
from pathlib import Path


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
        self._OriginalName = OriginalName.title()
        if(OriginalName.count('_') >= 1):
            self._Name = self.ConvertName(OriginalName)
        else:
            self._Name = self._OriginalName

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


class UAllMsgCodeGenerator:

    def __init__(self, MsgFolder):
        if not MsgFolder.exists() or not MsgFolder.is_dir():
            print(MsgFolder)
            print("Path does not exist or is not a folder")
            sys.exit(3)
        self.MsgFolder = MsgFolder.absolute()

    def GenMsgs(self):
        for file in list(self.MsgFolder.glob('*.msg')):
            UMsgCodeGenerator(file)


class UMsgCodeGenerator:

    def __init__(self, MsgFilePath):
        if not MsgFilePath.exists() or MsgFilePath.is_dir():
            print(MsgFilePath)
            print("Path does not exist or is folder")
            sys.exit(3)

        self.MsgFilePath = MsgFilePath.absolute()

        self.PackageName = self.MsgFilePath.parts[-3]

        self.MsgContent = []
        self.ClassName = ''
        self.Variables = []

        bt = open("../config/BaseTypes.txt")
        self.BaseTypes = bt.readline().split(' ')
        bt.close()

        cc = open("../config/ConversionChart.txt")
        CleanedCC = self.RemoveParagraphs(cc.readlines())
        self.ConversionChart = []
        for Rule in CleanedCC:
            self.ConversionChart.append(Rule.split(' '))
        self.ConversionChart = np.array(self.ConversionChart)
        cc.close()

        jt = open("../config/MatchJsonTypes.txt")
        CleanedJT = self.RemoveParagraphs(jt.readlines())
        self.JsonTypes = []
        for Match in CleanedJT:
            self.JsonTypes.append(Match.split(' '))
        self.JsonTypes = np.array(self.JsonTypes)
        jt.close()

        # Read the definition file
        self.ReadFile()
        # Generate the msg file
        self.GenMsg()

    def RemoveParagraphs(self, RawDocument):
        CleanedArray = []
        for Element in RawDocument:
            if(Element.endswith('\n')):
                CleanedArray.append(Element[:-1])
            else:
                CleanedArray.append(Element)
        return CleanedArray

    def Indent(self, Array, Count):
        IndentedArray = []
        IndentString = '\t'*Count

        for Index in Array:
            if(not type(Index) is list):
                IndentedArray.append(IndentString + Index)

        return IndentedArray

    def MakeVariableArray(self):
        OutArray = []
        for i in range(0, len(self.MsgContent)):
            if(self.MsgContent[i].count('#') == 0):
                SplitLine = self.MsgContent[i].rstrip().split(' ')
                print(SplitLine)
                NewVariable = Variable()

                if not (SplitLine[1].isupper()):
                    if(SplitLine[1].count('=') >= 1):
                        NewVariable.SetHasDefault = True
                        NewVariable.SetDefaultValue(SplitLine[1].split('=')[-1])
                        NewVariable.SetOriginalName(SplitLine[1].split('=')[0])
                    else:
                        NewVariable.SetHasDefault(False)
                        NewVariable.SetOriginalName(SplitLine[1])

                    if(SplitLine[0][-2:] == '[]'):
                        NewVariable.SetIsArray(True)
                        if(SplitLine[0][:-2] in self.ConversionChart[:, 0]):
                            LocalCC = self.ConversionChart[:, 0].tolist()
                            NewVariable.SetType(self.ConversionChart[LocalCC.index(SplitLine[0][:-2])][1])
                        elif(SplitLine[0][:-2] not in self.BaseTypes):
                            NewVariable.SetType(SplitLine[0][:-2].replace('/', '::'))
                        else:
                            NewVariable.SetType(SplitLine[0][:-2])
                    else:
                        NewVariable.SetIsArray(False)
                        if(SplitLine[0] in self.ConversionChart[:, 0]):
                            LocalCC = self.ConversionChart[:, 0].tolist()
                            NewVariable.SetType(self.ConversionChart[LocalCC.index(SplitLine[0])][1])
                        elif(SplitLine[0] not in self.BaseTypes):
                            NewVariable.SetType(SplitLine[0].replace('/', '::'))
                        else:
                            NewVariable.SetType(SplitLine[0])
                    if(NewVariable.GetType() in self.JsonTypes[:, 0]):
                        LocalJT = self.JsonTypes[:, 0].tolist()
                        NewVariable.SetJsonType(self.JsonTypes[LocalJT.index(NewVariable.GetType())][1])
                    else:
                        NewVariable.SetJsonType('ObjectField')
                    OutArray.append(NewVariable)
        self.Variables = OutArray

    def GenIncludes(self):
        IncludeList = ["#pragma once\n\n", "#include \"ROSBridgeMsg.h\"\n\n"]
        for Variable in self.Variables:
            print(Variable.GetType())
            if(not(Variable.GetType() in self.BaseTypes or
                   Variable.GetType() in self.ConversionChart[:, 1])):
                IncludeList.append('#include "' +
                            Variable.GetType().replace('::', '/') + '.h"\n')
        return IncludeList

    def GenNameSpace(self):

        NameSpace = ['\nnamespace ' + self.PackageName + '\n']

        NameSpace.append('{\n')
        return NameSpace

    def GenClass(self):
        Class = ['class ' + self.ClassName + ' : public FROSBridgeMsg\n']
        Class.append('{\n')
        Class = self.Indent(Class, 1)
        return Class

    def GenPrivateVariables(self):
        PrivateVariables = []
        for Variable in self.Variables:
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

        return self.Indent(PrivateVariables, 2)

    def GenConstructors(self):
        Constructors = []
        Constructors.append(self.ClassName + '()\n')
        Constructors.append('{\n')
        Constructors.append('\tMsgType = "' + self.PackageName + '/' + self.ClassName + '";\n')
        Constructors.append('}\n\n')

        Constructors.append(self.ClassName + '\n')
        Constructors.append('(\n')
        for Variable in self.Variables:
            if(Variable.IsArray()):
                Constructors.append('\tconst TArray<' + Variable.GetType() + '>& In' + Variable.GetName() + ',\n')
            else:
                Constructors.append('\t'+ Variable.GetType() + ' In' + Variable.GetName() + ',\n')
        Constructors[-1] = Constructors[-1].replace(',', '')
        Constructors.append('):\n')

        for Variable in self.Variables:
            if(Variable.HasDefault()):
                Constructors.append('\t' + Variable.GetName() + '(In' + Variable.GetName() + ' = ' + Variable.GetDefaultValue() +'),\n')
            else:
                Constructors.append('\t' + Variable.GetName() + '(In' + Variable.GetName() + '),\n')
        Constructors[-1] = Constructors[-1].replace(',', '')
        Constructors.append('{\n')
        Constructors.append('\tMsgType = "' + self.PackageName + '/' + self.ClassName + '";\n')
        Constructors.append('}\n\n')

        Constructors.append('~' + self.ClassName + '() override {}\n\n')

        return self.Indent(Constructors, 2)

    def GenGettersAndSetters(self):
        GettersAndSetters = []
        # Getters
        for Variable in self.Variables:
            if(Variable.IsArray()):
                GettersAndSetters.append('TArray<' + Variable.GetType() + '> Get' + Variable.GetName() + '() const\n')
            else:
                GettersAndSetters.append(Variable.GetType() + ' Get' + Variable.GetName() + '() const\n')
            GettersAndSetters.append('{\n')
            GettersAndSetters.append('\treturn ' + Variable.GetName() + ';\n')
            GettersAndSetters.append('}\n\n')

        # Setters
        for Variable in self.Variables:
            if(Variable.IsArray()):
                GettersAndSetters.append('void Set' + Variable.GetName() + '(TArray<' + Variable.GetType() + '>& In' + Variable.GetName() + ')\n')
            else:
                GettersAndSetters.append('void Set' + Variable.GetName() + '(' + Variable.GetType() + ' In' + Variable.GetName() + ')\n')
            GettersAndSetters.append('{\n')
            GettersAndSetters.append('\t' + Variable.GetName() + ' = In' + Variable.GetName() + ';\n')
            GettersAndSetters.append('}\n\n')

        return self.Indent(GettersAndSetters,2)


    def GenFromJson(self):
        FromJson = []
        FromJson.append('virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override\n')
        FromJson.append('{\n')
        ArrayFlag = False

        for Variable in self.Variables:
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

        return self.Indent(FromJson, 2)

    def GenGetFromJson(self):
        GetFromJson = []
        GetFromJson.append('static ' + self.ClassName + ' GetFromJson(TSharedPtr<FJsonObject> JsonObject)\n')
        GetFromJson.append('{\n')
        GetFromJson.append('\t'+ self.ClassName + ' Result;\n')
        GetFromJson.append('\t'+ 'Result.FromJson(JsonObject);\n')
        GetFromJson.append('\t'+ 'return Result;\n')
        GetFromJson.append('}\n\n')

        return self.Indent(GetFromJson, 2)

    def GenToJsonObject(self):
        ToJsonObject = []
        ToJsonObject.append('virtual TSharedPtr<FJsonObject> ToJsonObject() const override\n')
        ToJsonObject.append('{\n')
        ToJsonObject.append('\tTSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());\n\n')

        for Variable in self.Variables:
            if(Variable.IsArray()):
                ToJsonObject.append('\tTArray<TSharedPtr<FJsonValue>> ' + Variable.GetName() + 'Array;\n')
                ToJsonObject.append('\tfor (auto &val : ' + Variable.GetName() + ')\n')
                if(Variable.GetJsonType() == 'ObjectField'):
                    ToJsonObject.append('\t\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FJsonValue' + Variable.GetJsonType()[:-5] + '(val.ToJsonObject())));\n')
                else:
                    ToJsonObject.append('\t\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FJsonValue' + Variable.GetJsonType()[:-5] + '(val)));\n')
                ToJsonObject.append('\tObject->SetArrayField(TEXT("' + Variable.GetName().lower() + '"), ' + Variable.GetName() + 'Array);\n' )
            else:
                if(Variable.GetJsonType() == 'ObjectField'):
                    ToJsonObject.append('\tObject->SetObjectField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + '.ToJsonObject());\n')
                else:
                    ToJsonObject.append('\tObject->Set' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + ');\n')

        ToJsonObject.append('\treturn Object;\n')
        ToJsonObject.append('}\n')
        return self.Indent(ToJsonObject, 2)

    def GenToYamlString(self):
        ToYamlString = []
        ToYamlString.append('virtual FString ToYamlString() const override\n')
        ToYamlString.append('{\n')
        ToYamlString.append('\tFString OutputString;\n')
        ToYamlString.append('\tTSharedRef< TJsonWriter<> > Writer = TJsonWriterFactory<>::Create(&OutputString);\n')
        ToYamlString.append('\tFJsonSerializer::Serialize(ToJsonObject().ToSharedRef(), Writer);\n')
        ToYamlString.append('\treturn OutputString;\n')
        ToYamlString.append('}\n')
        return self.Indent(ToYamlString, 2)

    def GenMsg(self):
        self.MakeVariableArray()

        OutputArray = []

        # Write the Output
        OutputArray.append(self.GenIncludes())
        OutputArray.append(self.GenNameSpace())
        OutputArray.append(self.GenClass())
        OutputArray.append(self.GenPrivateVariables())
        OutputArray.append(self.Indent(['public:\n'], 1))
        OutputArray.append(self.GenConstructors())
        OutputArray.append(self.GenGettersAndSetters())
        OutputArray.append(self.GenFromJson())
        OutputArray.append(self.GenGetFromJson())
        OutputArray.append(self.GenToJsonObject())
        OutputArray.append(self.GenToYamlString())
        OutputArray.append(self.Indent(['};\n'], 1))
        OutputArray.append(['}'])

        OutputFile = self.MsgFilePath.parent / (self.ClassName + '.h')
        print(OutputFile)
        Output = open(str(OutputFile), 'w')
        for Block in OutputArray:
            Output.writelines(Block)
        Output.close()

    def ReadFile(self):
        with self.MsgFilePath.open() as MsgFile:
            self.MsgContent = MsgFile.readlines()
        self.MsgContent = self.RemoveParagraphs(self.MsgContent)
        self.ClassName = self.MsgFilePath.stem


def Main(Package, Name):
    CG = UAllMsgCodeGenerator(Package)
    CG.GenMsgs()
    # if(Package.exists()):
    #     for file in list(Package.glob('*.msg')):
    #         with file.open() as MsgFile:
    #             MsgContent = MsgFile.readlines()
    #             MsgContent = RemoveParagraphs(MsgContent)
    #             MsgName = file.stem
    #
    #             CG = UMsgCodeGenerator()
    #             Variables = CG.MakeVariableArray(MsgContent)
    #
    #             OutputArray = []
    #
    #             # Write the Output
    #             OutputArray.append(CG.GenIncludes(Variables))
    #             OutputArray.append(CG.GenNameSpace(Name))
    #             OutputArray.append(CG.GenClass(MsgName))
    #             OutputArray.append(CG.GenPrivateVariables(Variables))
    #             OutputArray.append(Indent(['public:\n'], 1))
    #             OutputArray.append(CG.GenConstructors(Variables, MsgName, Name, MsgName))
    #             OutputArray.append(CG.GenGettersAndSetters(Variables))
    #             OutputArray.append(CG.GenFromJson(Variables))
    #             OutputArray.append(CG.GenGetFromJson(MsgName))
    #             OutputArray.append(CG.GenToJsonObject(Variables))
    #             OutputArray.append(CG.GenToYamlString())
    #             OutputArray.append(Indent(['};\n'], 1))
    #             OutputArray.append(['}'])
    #
    #             if(Package.parent.name == Name):
    #                 OutputPath = Package / '..' / Name
    #             else:
    #                 OutputPath = Package / Name
    #             OutputPath.mkdir(exist_ok=True)
    #
    #             OutputFile = OutputPath / (MsgName + '.h')
    #             Output = open(str(OutputFile), 'w')
    #             for Block in OutputArray:
    #                 Output.writelines(Block)
    #             Output.close()

    # else:
    #     print("Folder %s does not exist", Name)

if(__name__ == '__main__'):
    try:
        opts, args = getopt.getopt(sys.argv, "hi:", ["ifile="])
    except getopt.GetoptError:
        sys.exit(2)

    if len(args) > 1:
        FolderPath = args[1]
    else:
        print("not path provided")
        sys.exit(2)

    dirpath = Path(FolderPath)

    PackageName = ''
    msgdir = dirpath / "msg"
    PackageName = dirpath.name
    Main(msgdir, PackageName)
