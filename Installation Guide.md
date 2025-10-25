# Installation Guide
## Windows
1. You need to install python [here](https://www.python.org/downloads/)
2. Find your downloaded repository
3. Open cmd and Create a virtual environment `python -m venv venv`
4. Activate the virtual environment `venv\Scripts\activate`
5. Run command `pip install -r requirements.txt` to install the requirements
6. Set the flask app variable `set FLASK_APP=app.py`
7. Start the app `python app.py`(using this also enables debug mode).