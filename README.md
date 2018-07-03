# MsgGeneration
A python script to generate UROSBridge compatible message files from ROS-like templates.

## Introduction
You are tired of having to write every single message or service file for UROSBridge yourself? You want to stop having to bang your head against the wall in frustration at the thought of **even more** copypasta?

If you answered yes (or YEAH!!!) to any of those, today is your lucky day. I present to you: MsgGenerator.py and SrvGenerator.py! These scripts (which will at some point be merged into one) will take a simple ROS-msg or ROS-srv formatted template and convert it into a finished UROSBridge message, full automated! Working with UROSBridge has never been so much fun before. What are you waiting for? Get on with it!

## Usage
Begin by cloning this repository to your local machine. Call MsgGenerator.py or SrvGenerator.py from the commandline and specify a path. The -p option allows you to write a path directly. If you use -g a filedialog will open which allows you to pick a folder. 

The directory you choose should be a ROS-Package containing a msg and/or srv folder which holds your msg or srv files. (This is the same directory tree you will find in any normal ROS-Package). After running, the generated C++ files will be placed in the main folder of the package.

## Formatting
For formatting rules for the contents of the .txt file refer to [this](http://wiki.ros.org/msg).

The namespace of your message or service will be the packages name. (e.g. if you have a file in 'geometry_msgs' it's namespace will be 'geometry_msgs'.)

The name of the message will be the name of your file with a .h at the end.
