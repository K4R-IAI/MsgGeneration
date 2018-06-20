# MsgGeneration
A python script to generate UROSBridge compatible message files from ROS-like templates.

## Introduction
You are tired of having to write every single message file for UROSBridge yourself? You want to stop having to bang your head against the wall in frustration at the thought of **even more** copypasta?

If you answered yes (or YEAH!!!) to any of those, today is your lucky day. I present to you: Generator.py! This script will take a simple ROS-msg formatted template and convert it into a finished UROSBridge message, completely automatic! Working with UROSBridge has never been so much fun before. What are you waiting for? Get on with it!

## Usage
Begin by cloning this repository to your local machine. Find bin/Generator.py and double click it.

On startup the script will present you with a pick-a-directory dialog. By default 'templates' is selected as the folder of choice, but feel free to select your own directory.

Once you've chosen a directory, the Generator will look through all subdirectories for files with a .txt extension. Assuming the file is properly formatted (see below) it will put a file with the same name and the extension .h into that directory. It contains the finished C++ code which can be used for happy message interchanging with a ROSBridge Server.

## Formatting
For formatting rules for the contents of the .txt file refer to [this](http://wiki.ros.org/msg).

The namespace of your message will be the file's relative path in the directory you select when you start up the Generator. (e.g. if you have a file in 'geometry_msgs' it's namespace will be 'geometry_msgs'.)

The name of the message will be the name of your file, excluding the .txt at the end.
