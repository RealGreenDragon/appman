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
- Clone the repository where you want (preferably in "C:\\appman" or "C:\\ProgramData\\appman")
- Add the folder 'appman\\bin' to the system path
- Now you can reach the manager simply typing 'appman' on CMD/PowerShell from any location
- In the same way you can now reach 7-Zip typing '7z' (or '7zfm' if you want the GUI)

### Usage
```
usage: appman.py [-h] [-v] [-d]
                 {install,remove,update,list-available,list-installed}
                 [programs [programs ...]]

An application manager for Windows

positional arguments:
  {install,remove,update,list-available,list-installed}
                        Action to perform, one of: install, remove, update,
                        list-available, list-installed ("install" mode requires
                        admin privileges)
  programs              Space separated list of program names to
                        install/update/remove (if mode is "update", you can
                        use "all" to update all programs installed)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d, --debug           Enable debug mode
```
