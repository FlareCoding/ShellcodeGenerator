# About
### ShellcodeGenerator is a Windows-specific tool for compiling C/C++ code into x86 (32-bit) base-independent shellcode.<br/>

<br/>
<br/>

# Process of Shellcode Generation

First the python script compiles the given C++ file using the local cl.exe msvc compiler.<br/>
During compilation the -S flag is passed in to generate an intermidiate assembly file.<br/>
<br/>
Next the python script parses the resulting x86 assembly extracting the necessary function's code and correcting global string literals to be initialized locally and pushed onto the stack.
<br/>
<br/>
After the corrected assembly code has been produced, it uses [defuse.ca](https://defuse.ca/online-x86-assembler.htm#disassembly) website to assemble the code and produce shellcode in a string format.<br/>
The script extracts that output and stores it in a text file _"shellcode.txt"_ ready to be pasted into your C/C++ program as a ```const char``` array.
<br/>
<br/>

# Requirements

## ```chromedriver.exe```<br/>
You must have the correct version of __chromedriver__ that is compatible with your *Google Chrome* version.
The one provided is compatible with __89.0.4389.114__ version of chrome.<br/>
Other versions can be downloaded from [here](https://chromedriver.chromium.org/downloads).
<br/>

## Python 3
You must have Python 3 installed and configured on your system in order to use the ```shellcode_generator.py``` script.
You can download the latest version of Python from [here](https://www.python.org/downloads/).
<br/>

## Microsoft Visual Studio (comes with VC++ toolset)
In order to use the cl.exe compiler, the script must locate the visual studio installation path to intialize the command-line environment.<br/>
The script currently uses the __2019__ version of Visual Studio, so if you have a later version, do the following:
* Locate ```vcvars32.bat``` in your Visual Studio installation directory.
* Open the ```shellcode_generator.py``` script and replace ```MSVC_VCVARS32_PATH``` with the path found in the previous step.
<br/>
Microsoft Visual Studio can be downloaded from [here](https://visualstudio.microsoft.com/downloads/).
<br/>

# Usage

Use the ```shellcode_main.cpp``` template to write your code that will be converted to shellcode.<br/>
*__*Important*__: You MUST write all your code inside the ```ShellcodeMain``` function and not use any functions included from external headers.*<br/>
<br/>
When you are done writing your C++ code, run the python generator script passing in your .cpp file as the first argument as follows:<br/>

* ```python shellcode_generator.py shellcode_main.cpp```<br/>

If you want to keep the corrected output assembly code, include ```1``` as the second argument as follows:<br/>

* ```python shellcode_generator.py shellcode_main.cpp 1```<br/>
<br/>

The resulting shellcode will be located in the ```shellcode.txt``` file. 
