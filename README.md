# MsgGeneration
A python script to generate UROSBridge compatible message files from ROS-like templates.

## Introduction
Once finished this script will search through all folders in the same directory as itself and convert all therein located .txt files into UROSBridge compatible message.h files.

## Usage
The script will use the relative path to the .txt file to determine it's type. The name of the .txt file should be the desired name of the message. The template works by the same rules as the official message generation from ROS. TODO:Add link
