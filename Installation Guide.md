# Installation Guide
## Windows

1. **You need to install python** [here](https://www.python.org/downloads/)
2. **Find your downloaded repository**
3. **Open cmd and Create a virtual environment** `python -m venv venv`
4. **Activate the virtual environment** `venv\Scripts\activate`

### 5. Install Dependencies (The Compiler Fix)
5. **Run command** `pip install -r requirements.txt` to install the requirements

>[!NOTE]
>### *Prerequisite for Compiled Packages*
>If you encounter an *error* like `Microsoft Visual C++ 14.0 or greater is required`, you **must** install the **Microsoft C++ Build Tools**. Download and install the **"Desktop development with C++"** workload from the [Visual Studio Build Tools website](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Then try to reinstall requirements see [Installation]

### 6. Configure the `.env` File (The Configuration Fix)
6. **Modify the `.env` File:** The project includes a `.env` file for configuration. You must change the following critical lines:
   - **Database URI:** Ensure it points to the instance folder for the database to be found.
   - **SECRET_KEY:** Generate and paste a unique key.
   - **Flask-Mail:** Set MailHog's local server details.

   - To **create a secret key** you have to run this command `python -c "import secrets; print(secrets.token_hex(24))"` and the output **should look like something this**: _b5f48b0a9c7e0d3f2a1768c92d5e7f1034b6c1e57a8f09d2_ you have to paste the **_entire string_** in.

### 7. Set Flask Application Context
7. **Set the flask app variable** `set FLASK_APP=app.py`

### 8. Initialize the Database Tables (The "No Such Table" Fix)
8. **Import and build up the db** using the Flask shell. This step is mandatory to create the tables (like `users`).

    ```bash
    flask shell
    >>> from app_factory import db
    >>> from app import app
    >>> with app.app_context():
    ...     db.create_all()
    ...
    >>> exit()
    ```

### 9. Run the Application (and MailHog)
9. **Start the MailHog server** in a separate terminal window (if you haven't already).
10. **Run the app** `flask run` and hopefully everything will be working 🛠️
