# CST_Linker
Python script to automate the process of making antennas. Using CST Studio Suite 2025.

>[!important]
> - Needs CST Studio Suite 2025, I am working with this version not sure if it is compatible with other versions
> - **Python 3.11 required** the cst studio suite python library packages require python *'<3.12,>=3.7'*


### Steps to Run
- *Create python virtual environment by downloading python 3.11 and assigning it a name (cst_env)*
- `py install 3.11`
- `py -3.11 -m venv cst_env`
- *Set it may be required to enable the Activate.ps1 script by setting the execution policy for the user*
- `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- `cst_env\Scripts\activate`
- *Install CST library*
- `pip install --no-index --find-links "C:/Program Files (x86)/CST Studio Suite 2025/Library/Python/repo/simple" cst-studio-suite-link`
- *run the external script*
- `py "*<Path\to\external\script>*`
