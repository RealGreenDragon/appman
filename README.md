## Windows Application Manager
Manager that automatically install/remove/update programs on Windows.

### Advantages
- Programs "profiles" easy to write
- Allow to update all installed programs with only one command
- Allow to launch all installed programs directly on CMD/PowerShell from any location

### Included Programs
- Python embed (see readme into bin/python_embed for detailed info)
- 7-Zip (see readme into bin/7zip_embed for detailed info)

### Requirements
- Windows Vista/Server 2008 or newer
- Can open CMD/PowerShell as Administrator

### Installation steps
- Install [Microsoft C Runtime 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145)
- Download the [last stable release](https://github.com/MagicGreenDragon/appman/releases/latest) (recommended) or clone the master branch
- Put the program where you want (preferably in "C:\\appman")
- Add the folder 'appman\\bin' to the system path
- Now you can reach the manager simply typing 'appman' on CMD/PowerShell from any location
- In the same way you can now reach 7-Zip typing '7z' (or '7zfm' if you want the GUI)

### Usage
```
An application manager for Windows

positional arguments:
  {install,remove,update,available,installed}
                        Action to perform, one of:
                        - install   -> install one/more not installed programs (requires admin privileges)
                        - remove    -> remove one/more installed programs (requires admin privileges)
                        - update    -> update one/more installed program
                        - available -> list all available program profiles
                        - installed -> list all installed programs
  programs              Space separated list of program names (usable only if "mode" is install/update/remove).
                        The keyword "all" can be used to update all programs installed.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show program's author, version number and exit
  -d, --debug           Enable debug mode
```
