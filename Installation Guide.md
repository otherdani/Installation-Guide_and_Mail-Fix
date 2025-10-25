# Installation Guide
## Windows
1. You need to install python [here](https://www.python.org/downloads/)
2. Find your downloaded repository
3. Open cmd and Create a virtual environment `python -m venv venv`
4. Activate the virtual environment `venv\Scripts\activate`
5. Run command `pip install -r requirements.txt` to install the requirements
>[!NOTE] ### *Prerequisite for Compiled Packages*
>If you encounter an error like `Microsoft Visual C++ 14.0 or greater is required`, you must install the **Microsoft C++ Build Tools**.Download and install the **"Desktop development with C++"** workload from the [Visual Studio Build Tools website](https://visualstudio.microsoft.com/visual-cpp-build-tools/). then try to reinstall requirements see [Installation]
6. Set the flask app variable `set FLASK_APP=app.py`
7. Start the app `python app.py`(using this also enables debug mode).