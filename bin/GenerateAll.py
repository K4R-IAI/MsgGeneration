import os
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import argparse as ap
from MsgGenerator import Main as MsgMain
from SrvGenerator import Main as SrvMain

parser = ap.ArgumentParser(description='Generates UROSBridge compatible C++ files from msg and srv files in a ROS Package.')
parser.add_argument('--path', '-p', help='Provide the path to the ROS Package you want to generate the C++ files for.')
parser.add_argument('--usegui', '-g', action='store_true', help='Use this if you want to open a filedialog to pick your path.')
parser.add_argument('--messages', '-msg', action='store_true', help='Add this argument if you want to convert only message files.')
parser.add_argument('--services', '-srv', action='store_true', help='Add this argument if you want to convert only services files.')


args = parser.parse_args()

if(args.path and not args.usegui):
    dirpath = args.path
elif(args.usegui and args.path):
    tk.Tk().withdraw()
    dirpath = filedialog.askdirectory(initialdir=args.path, title ='Please select a ROS Package.')
elif(args.usegui and not args.path):
    tk.Tk().withdraw()
    dirpath = filedialog.askdirectory(initialdir=os.path.join(os.path.dirname(__file__), '..'), title ='TEST.')
else:
    parser.error('A path needs to be specified. Use the -p option to specify a path or see --help for other options.')

dirpath = Path(dirpath)

if(args.messages and not args.services):
    MsgMain((dirpath / "msg"), dirpath.name)
elif(args.services and not args.messages):
    SrvMain((dirpath / "srv"), dirpath.name)
else:
    MsgMain((dirpath / "msg"), dirpath.name)
    SrvMain((dirpath / "srv"), dirpath.name)
