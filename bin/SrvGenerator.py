import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
import argparse as ap
from string import Template

class Variable:
    def ConvertName(self, OriginalName):
        ConvertedName = OriginalName.replace('_', ' ').title().replace(' ', '')
        return ConvertedName

    def __init__(self, OriginalName = '', Type = '', IsArray = False, JsonType = '', HasDefault = False, DefaultValue = '' ):
        self._HasDefault = HasDefault
        self._DefaultValue = DefaultValue
        self.SetOriginalName(OriginalName)
        self.SetType(Type)
        self._IsArray = IsArray
        self.SetJsonType(JsonType)
        self._ArrayJsonType = JsonType[:-5]

    def SetOriginalName(self, OriginalName):
        self._OriginalName = OriginalName.lower()

        self._Name = self.ConvertName(OriginalName)

        self._NameWithDefault = self._Name + ' = ' + self._DefaultValue
        
    def SetType(self, Type):
        self._Type = Type
        self._ArrayType = 'TArray<'+Type+'>'

    def SetIsArray(self, IsArray):
        self._IsArray = IsArray
        
    def SetJsonType(self, JsonType):
        self._JsonType = JsonType
        if(JsonType):
            self._ArrayJsonType = JsonType[:-5]
        
    def SetHasDefault(self, HasDefault):
        self._HasDefault = HasDefault
        
    def SetDefaultValue(self, DefaultValue):
        self._DefaultValue = DefaultValue

    def GetName(self):
        return self._Name
    
    def GetOriginalName(self):
        return self._OriginalName

    def GetNameWithDefault(self):
        return self._NameWithDefault
    
    def GetType(self):
        return self._Type
    
    def GetArrayType(self):
        return self._ArrayType
    
    def IsArray(self):
        return self._IsArray
    
    def GetJsonType(self):
        return self._JsonType
    
    def GetArrayJsonType(self):
        return self._ArrayJsonType
    
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

md = open('../Templates/SrvTemplate.txt')
MainDocument = Template(md.read())
md.close


def MakeVariableArray(MsgContent):
    OutArray = []
    for i in range(0, len(MsgContent)):
        if(MsgContent[i].count('#') >= 1):  
            SplitLine = MsgContent[i].split('#')[0].rstrip().split(' ')
        else:
            SplitLine = MsgContent[i].rstrip().split(' ')
        NewVariable = Variable()
        
        if(SplitLine[1].count('=') >= 1):
            NewVariable.SetHasDefault(True)
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


def GenPrivateVariables(Variables):
    Indent = 3
    PrivateVariables = ''
    for Variable in Variables: 
        if(Variable.IsArray()):
            PrivateVariables += Variable.GetArrayType()
        else:
            PrivateVariables += Variable.GetType()
        PrivateVariables += ' '
        if(Variable.HasDefault()):
            PrivateVariables += Variable.GetNameWithDefault()
        else:
            PrivateVariables += Variable.GetName()
        PrivateVariables += ';\n'
        PrivateVariables += '\t' * Indent
    PrivateVariables = PrivateVariables[:-(Indent+1)] # Remove paragraph and indent from last line
    return PrivateVariables

def GenConstructor(Variables):
    Indent = 4
    Constructor = 'Request('

    for Variable in Variables: 
        if(Variable.IsArray()):
            Constructor += Variable.GetArrayType()
        else:
            Constructor += Variable.GetType()
        Constructor += ' In'
        Constructor += Variable.GetName()
        Constructor += ',\n'
        Constructor += '\t' * Indent

    Constructor = Constructor[:-(Indent+2)] + ')'

    Constructor += '\n' # Paragraph
    Constructor += '\t' * Indent # Default Indentation
    Constructor += ':\n' # Constructor initialization starts here
    Constructor += '\t' * Indent

    for Variable in Variables:
        Constructor += Variable.GetName()
        Constructor += '(In' + Variable.GetName() + ')'
        Constructor += ',\n'
        Constructor += '\t' * Indent
    Constructor = Constructor[:-(Indent+2)] + ' { }'
    
    return Constructor

def GenGetters(Variables):
    Indent = 3
    Getters = '// Getters \n' + '\t' * Indent

    for Variable in Variables:
        if(Variable.IsArray()):
            Type = Variable.GetArrayType()
        else:
            Type = Variable.GetType()
        Name = Variable.GetName() # For shorter lines
        Getters += Type + ' Get' + Name + '() const { return ' + Name + '; }\n'
        Getters += '\t' * Indent
    Getters = Getters[:-(Indent+1)]
    return Getters

def GenSetters(Variables):
    Indent = 3
    Setters = '// Setters \n' + '\t' * Indent

    for Variable in Variables:
        if(Variable.IsArray()):
            Type = Variable.GetArrayType()
        else:
            Type = Variable.GetType()
        Name = Variable.GetName() # For shorter lines
        Setters += 'void Set' + Name + '(' + Type + ' In' + Name + ') { ' + Name + ' = In' + Name + '; }\n'
        Setters += '\t' * Indent
    Setters = Setters[:-(Indent+1)]
    return Setters

def GenFromJson(Variables):
    Indent = 4
    FromJson = ''

    ArrayFlag = False
    for Variable in Variables:
        if(Variable.IsArray()):
            ArrayFlag = True

    if(ArrayFlag):
        FromJson += 'TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;\n\n'
        FromJson += '\t' * Indent
                
    for Variable in Variables:
        if(not Variable.IsArray()):
            if(Variable.GetJsonType() == 'ObjectField'):
                FromJson += Variable.GetName() + ' = ' + Variable.GetType() + '::GetFromJson(JsonObject->GetObjectField(TEXT("' + Variable.GetOriginalName() + '")));\n\n'
            else:
                FromJson += Variable.GetName() + ' = JsonObject->Get' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"));\n\n'
            FromJson += '\t' * Indent
        else:
            FromJson += Variable.GetName() + '.Empty();\n' + '\t' * Indent
            FromJson += 'ValuesPtrArr = JsonObject->GetArrayField(TEXT("' + Variable.GetOriginalName() + '"));\n' + '\t' * Indent
            FromJson += 'for (auto &ptr : ValuesPtrArr)\n' + '\t' * Indent
            if(Variable.GetJsonType() == 'ObjectField'):
                FromJson += '\t' + Variable.GetName() + '.Add(' + Variable.GetType() + '::GetFromJson(ptr->AsObject()));\n\n' + '\t' * Indent
            else:
                FromJson += '\t' + Variable.GetName() + '.Add(ptr->As' + Variable.GetJsonType()[:-5] + '());\n\n' + '\t' * Indent
    FromJson = FromJson[:-(Indent+1)]
    return FromJson

def GenToJsonObject(Variables):
    Indent = 4
    ToJsonObject = ''

    ToJsonObject += 'TSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());\n\n'
    ToJsonObject += '\t' * Indent

    for Variable in Variables:
        if(Variable.IsArray()):
            ToJsonObject += 'TArray<TSharedPtr<FJsonValue>> ' + Variable.GetName() + 'Array;\n' + '\t' * Indent
            ToJsonObject += 'for (auto &val : ' + Variable.GetName() + ')\n' + '\t' * Indent
            ToJsonObject += '\t' + Variable.GetName() + 'Array.Add(MakeShareable(new FJsonValue' + Variable.GetJsonType()[:-5] + '(val)));\n'+ '\t' * Indent
            ToJsonObject += 'Object->SetArrayField(TEXT("' + Variable.GetName().lower() + '"), ' + Variable.GetName() + 'Array);\n'

        else:
            if(Variable.GetJsonType() == 'ObjectField'):
                ToJsonObject += 'Object->SetObjectField(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + '.ToJsonObject());\n'
            else:
                ToJsonObject += 'Object->Set' + Variable.GetJsonType() + '(TEXT("' + Variable.GetOriginalName() + '"), ' + Variable.GetName() + ');\n'
        ToJsonObject += '\n' + '\t' * Indent
        
    ToJsonObject += 'return Object;\n'

    return ToJsonObject


parser = ap.ArgumentParser(description='Generates UROSBridge compatible C++ files from srv files in a ROS Package.')
parser.add_argument('--path', '-p', help='Provide the path to the ROS Package you want to generate the C++ files for.')
parser.add_argument('--usegui', '-g', action='store_true', help='Use this if you want to open a filedialog to pick your path.')
parser.add_argument('--srvfolder', '-sf', help='Use this if instead of a ROS Package you are selecting a folder directly containing the .srv files. Requires a namespace to be provided.')

args = parser.parse_args()

if(args.path and not args.usegui):
    dirpath = args.path
elif(args.usegui and args.path):
    tk.Tk().withdraw()
    dirpath = filedialog.askdirectory(initialdir=args.path, title ='Please select a ROS Package.')
elif(args.usegui and not args.path):
    tk.Tk().withdraw()
    dirpath = filedialog.askdirectory(initialdir=os.path.join(os.path.dirname(__file__), '..'), title ='Please select a ROS Package.')
else:
    parser.error('A path needs to be specified. Use the -p option to specify a path or see --help for other options.')

if(not args.srvfolder):
    srvdir = os.path.join(dirpath, 'srv').replace('/','\\')
else:
    srvdir = dirpath

for file in os.listdir(srvdir):
    if(file[-3:] == 'srv'):
        # Open a file, save its name and content and close it
        SrvTemplate = open(os.path.join(srvdir, file).replace('\\', '/'))
        SrvTemplateContent = SrvTemplate.readlines()
        SrvName = SrvTemplate.name.split('.')[0].split('/')[-1]
        SrvTemplate.close()

        # Check whether a custom package name was provided
        if(args.srvfolder):
            PackageName = args.srvfolder
        else:
            PackageName = os.path.dirname(srvdir).replace(os.path.dirname(os.path.dirname(srvdir)) + '\\', '')

        # Remove all \n from the contents of the service template
        SrvTemplateContent = RemoveParagraphs(SrvTemplateContent)

        ReqVariables = MakeVariableArray(SrvTemplateContent[:SrvTemplateContent.index('---')])
        ResVariables = MakeVariableArray(SrvTemplateContent[SrvTemplateContent.index('---')+1:])

        # Write the content to the C++ Template provided in the Template folder
        MainDocument = Template(MainDocument.safe_substitute(packagename=PackageName, srvname=SrvName))
        MainDocument = Template(MainDocument.safe_substitute(reqprivatevariables=GenPrivateVariables(ReqVariables), reqconstructor=GenConstructor(ReqVariables), reqsetters=GenSetters(ReqVariables), reqgetters=GenGetters(ReqVariables),reqfromjson=GenFromJson(ReqVariables), reqtojsonobject=GenToJsonObject(ReqVariables)))
        MainDocument = MainDocument.safe_substitute(resprivatevariables=GenPrivateVariables(ResVariables), resconstructor=GenConstructor(ResVariables), ressetters=GenSetters(ResVariables), resgetters=GenGetters(ResVariables),resfromjson=GenFromJson(ResVariables), restojsonobject=GenToJsonObject(ResVariables))

        if(not os.path.isdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/')):
            os.mkdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/')
        if(not os.path.isdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName)):
            os.mkdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName)
        if(not os.path.isdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName + '/srv')):
            os.mkdir(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName + '/srv/')
        Output = open(os.path.dirname(os.path.dirname(__file__)) + '/UROSBridgeFiles/' + PackageName + '/srv/' + SrvName + '.h', 'w')

        Output.write(MainDocument)
            
        Output.close()


