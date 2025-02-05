# 🐾 PetPal – Your Pet’s Digital Companion  

### 🎥 Video Demo: [Video URL Here]  

## 📌 About PetPal  
PetPal is a **web application** designed to make pet care easier by helping owners **organize and track** essential information about their furry friends. From **medical records and weight tracking** to **photo galleries and logs**, PetPal brings everything into **one convenient platform**.  

### 💡 Why PetPal?  
As a pet owner, I found it **challenging** to keep track of my pets' health and important details. **PetPal** was created to simplify this process—allowing users to store and manage pet information with an intuitive and user-friendly interface.  

---

## ⭐ Key Features  

### 📋 **Pet Information Management**  
- Record details like **species, breed, birthdate, adoption date**, and important health data such as **microchip numbers** and **insurance information**.  

### 📸 **Photo Gallery**  
- Upload and organize photos with **optional titles and dates**, displayed in **chronological order** for easy browsing.  

### 🏥 **Health Trackers**  
There are multiple trackers available, including:
- **📈 Weight Tracker** – Log weight updates and visualize progress with graphs.  
- **💉 Vaccination Tracker** – Track vaccine details, administration dates, and next doses.  
- **🦠 Deworming Tracker** – Keep records of internal and external deworming schedules.  
- **💊 Medication Tracker** – Manage medication schedules, including dosage, next dose, and any notes.  

### 📝 **Logs & Journals**  
- Keep a **personalized journal** for your pet, documenting special moments or medical visits.  

### 📱 **Responsive & User-Friendly Design**  
- Built with **mobile-friendly features**, ensuring smooth navigation on all devices.  

---

## 🎨 Design Choices  

- **🗄 Organized Database** – I opted to use SQLAlchemy as the ORM (Object-Relational Mapper) to interact with the database because of its flexibility and ease of use. Each piece of data (e.g., weight, vaccination) is stored in separate tables that are linked to the `Pet` model, ensuring that data remains organized and easy to query.
- **🌐 Clean UI** – Built with **Bootstrap** for a sleek and **intuitive experience**. I aimed to create a clean and user-friendly interface that would be simple for pet owners to navigate. PetPal features a responsive design, ensuring the app looks great on both desktop and mobile devices. The layout is straightforward, with tabs for the photo gallery, trackers, and logs, allowing users to easily access the information they need.
- **🔐 Security** – PetPal implements essential Flask security features, including user authentication and input validation with Flask-WTF forms. Passwords are securely hashed before being stored in the database, protecting user credentials. Additionally, the app utilizes secure_filename() to prevent unsafe file uploads, ensuring that only properly formatted photo files are accepted. 
- **📊 Interactive Graphs** – The weight tracker includes a graph generated using `matplotlib`, which visually presents a pet's weight progress over time. This was an essential feature to help pet owners monitor their pets’ health changes.

### 📊 **Graphing & Visuals**  
- Uses **matplotlib** to generate **weight progression graphs** for pets.  

### 🔒 **Security Features**  
- Secure **user authentication** and **password hashing** for data protection.  
- Input validation to prevent **malicious entries**.  

---

## 📂 Project Structure  

### 🏗 **Main Components**

#### ⚙️ Core Application Files  
1. **`app.py`** – Application Entry Point  
   This file **runs the Flask application** by calling the `init_app()` function from `app_factory.py`.  
   - **Imports and initializes the app** using the factory function.  
   - **Runs the app** in **debug mode** when executed directly (`python app.py`). 

2. **`app_factory.py`** – Application Factory  
   This file is responsible for **initializing and configuring** the Flask application. Instead of defining the app in a single file, `app_factory.py` follows the **Factory Pattern**, which makes the app modular and scalable.  

   Key functionalities:  
   - **Loads environment variables** using `dotenv`, ensuring sensitive data is kept secure.  
   - **Configures Flask settings**, including secret keys, database connections, and session management.  
   - **Sets up an upload folder** (`static/uploads`) for storing user-uploaded images, with a file size limit of **6MB**.  
   - **Initializes Flask extensions**, such as:  
   - `SQLAlchemy` for database management.  
   - `Migrate` for handling database migrations.  
   - `Flask-Session` for user session management.  
   - `Flask-WTF` with CSRF protection.  
   - **Configures Flask-Mail** to allow email notifications (credentials stored in `.env`).  
   - **Registers all routes** from the `routes/` directory.  
   - **Prevents browser caching** by modifying response headers.  

This modular setup is based on the **App Factory Pattern** and ensures that the app remains **organized, secure, and easy to maintain**. Also, this separation of concerns makes the project **more scalable** by keeping the initialization logic (`app_factory.py`) independent from the execution logic (`app.py`).


#### 🗂 Complementary Files
1. **`helpers.py`**  – Utility Functions for PetPal
   This file contains **helper functions and decorators** that simplify various tasks across the application, enhancing **code organization and reusability**, such as:
   - **`login_required(f)`** – A decorator that ensures users are logged in before accessing certain routes. If not authenticated, the user is redirected to the welcome page.  
   - **`inject_pets(f)`** – A decorator that retrieves the user's pets from the database and makes them available globally (`g.pets`) for templates and views. 
   - **`error_message(message, code)`** – Renders an error page using a custom template (`error.html`), displaying an `http.cat` image based on the error code.  
   - **`allowed_photo_file(filename)`** – Validates if an uploaded file has an allowed image extension (`png`, `jpg`, `jpeg`, `gif`).  
   - **`delete_pet_from_db(pet, db)`** – Deletes a pet and all its associated data, including:  
      - Profile and gallery photos.  
      - Logs, weight records, vaccines, medications, and deworming records.  
   - **`create_weight_graph(dates, weights, title, xlabel, ylabel, color, show_days_only=False)`**  
      - Generates a **weight tracking graph** for pets using `matplotlib`.  
      - Filters out missing data points, formats the x-axis for better readability, and **returns the graph as an SVG** for responsive rendering.  

    ##### 🎯 Purpose  
   `helpers.py` enhances the application's **security**, **data management**, and **visualization capabilities**, avoiding code repetition and making `PetPal` more **efficient and user-friendly**. 

2. **`models.py`**  – Database models for the project
   Defines the structure of tables using SQLAlchemy, including the `User`, `Species`, `Breed`, `Pet`, `Photo`, `Log`, and `Tracker` models (weight, vaccine, internal/external deworming, and medication). It provides structured relationships between users and their pets while allowing tracking of various health metrics and activities related to pet care. Each model includes methods for converting data into dictionary format for easy serialization, which is useful for data manipulation within the application.

3. **`forms.py`**  – Flask-WTF forms for PetPal
   Includes forms utilizing the Flask-WTF extension for streamlined form handling. Flask-WTF forms are extensively used throughout the project to securely and effectively manage user input information. They are employed in various processes, including user registration and authentication.
   Each pet, log, and tracker (covering weight, vaccinations, deworming, and medication) has its own dedicated form to facilitate the creation and submission of new entries. Additionally, the `PhotoForm` is responsible for handling the upload of new photos for pets.

4. **`extensions.py`** – Flask Extensions Initialization  
   This file is dedicated to **initializing and managing Flask extensions** used throughout the application. By defining extensions in a separate file, we avoid **circular imports** that could occur when multiple files depend on the same extensions.  

   The following Flask extensions are initialized here:  
   - **`SQLAlchemy` (`db`)** – Provides an Object-Relational Mapper (ORM) for database interactions. This allows for defining models in Python instead of writing raw SQL queries.  
   - **`Flask-Migrate` (`migrate`)** – Handles database migrations, making it easy to apply and track changes to the database schema over time.  
   - **`Flask-WTF CSRFProtect` (`csrf`)** – Adds CSRF protection to forms, preventing cross-site request forgery attacks and enhancing security.  
   - **`Flask-Session` (`session`)** – Manages user sessions, allowing for persistent data storage across requests. The app is configured to use the filesystem for session storage.  

   By centralizing these extensions in `extensions.py`, the project maintains **better organization, avoids import errors, and improves maintainability**. Each extension is later initialized within `app_factory.py`, ensuring proper integration with the Flask app.  

5. **`requirements.txt`** – Dependencies
   `.txt` file to easily install all the dependencies required for PetPal.

6. **`breeds.py`**
   Contains a dictionary of all allowed dog and cat breeds for the app. This data is used to populate the database via migrations, ensuring that only valid breeds are available for selection when adding pets to the system.

-

#### 🛣 Routes

1. `__init__.py`
   - Initializes the route directory for better organization and access to the app’s routes.

2. `auth_routes.py`
   - Handles user authentication tasks and settings. It includes:
      - `login()` - Displays the login form and validates user credentials.
      - `logout()` - Logs the user out and redirects them to the welcome page.
      - `register()` - Displays the user registration form and handles new user creation. Upon successful submission, the route creates a new user in the database and generates an email confirmation token that expires in 5 minutes. The user is then sent a confirmation email with a link containing the token, which they must click to verify their email address and complete the registration process. 
      - **Password Recovery** - Allows users to reset their passwords using email.
      - `delete_user()` - Allows to delete current user from database.

3. `home_routes.py`
   - Manages the landing page and general home navigation. Key routes include:
      - `home()` - The user’s dashboard, showcasing their pets and options for adding or editing profiles.
      - `welcome()` - Displays information about the app and provides links for registration or login if no users are logged in.

4. `pet_routes.py`
   - Manages all pet-related routes. These routes allow users to **add, edit, or delete pets**. 
      - `add_new_pet()` - A form for users to add a new pet, collecting both general and medical information.
      - `edit_pet()` - Allows users to modify details of an existing pet.
      - `general_data()` - Displays the detailed profile of a pet, including personal and health information.
      - `delete_pet()` - Deletes a pet from the system, along with associated data (photos, logs, trackers).
      - `get_breeds()` - Displays breeds list according to species.

5. `gallery_routes.py`
   - Handles photo gallery operations, including uploading and viewing pet photos.
      - `gallery()` - Displays a gallery of all photos associated with a specific pet.
      - `upload_photo()` - Allows the user to upload a new photo for their pet, including an optional title and date.
      - `delete_photo()` - Deletes a selected photo from a pet's gallery.

6. `logs_routes.py`
   - Manages logging of important notes or events related to pets.
      - `pet_logs()` - Displays the list of logs for a specific pet, sorted by date.
      - `new_entry()` - Adds a new log entry for a pet.
      - `edit_entry()` - Allows users to edit existing log entries.
      - `read_entry()` - Displays an existing log entry to read.
      - `delete_entry()` - Deletes a specific log from the database.

7. `trackers_routes.py`
   - Manages the various trackers for pet health.
      - `trackers_home()` - Displays the trackers for a specific pet (weight, vaccinations, deworming, and medication).
      - `add_tracker()` - Allows users to add a new entry to any of the trackers (weight, vaccinations, deworming, or medication).
      - `weight_graph()` - Displays a monthly graph that shows pet weight over time.

##### Reasons for Choosing Modular Route Organization
Organizing routes into separate files helps keep the code organized, easy to manage, and scalable. It makes adding new features simpler, without overloading the main file. This setup also makes the project more readable, easier to debug, and efficient for teamwork. Testing becomes more straightforward, and code can be reused across different parts of the project. Sensitive features can be easily secured, and the folder structure remains clean and organized as the project grows, making it ready for future development.


#### 🖥 **Frontend (Templates & Static Files)**  
1. **HTML Templates** – Includes pages for user authentication, pet profiles, trackers, logs, and galleries.
   **`templates/`**  
   Contains the HTML files for rendering different pages in the app. The templates include:
   - **`welcome.html`**: The landing page for the app, showing basic info about PetPal and links to log in or register new users.
   - **`register.html`**:  Presents a registration form for new users to sign up by providing their username, email, password, and password confirmation, with a validation check to ensure the passwords match before submission and valid email address.
   - **`login.html`**: Provides a login interface for users to sign in with their email and password, along with links for password recovery and account registration. The frontend implementation checks for valid email address and password at least 8 characters long.
   - **`layout.html`**: Defines the main structure for the app, with a flexible layout to use across all pages that includes a top navigation bar, custom alerts, dynamic content insertion through Jinja blocks, and a footer, all styled with Bootstrap, custom CSS, and interactive elements such as theme toggling and session-based user features.
   - **`delete_confirmation_modal.html`**, **`pet_card`** and **`pet_dropdown_menu.html`**: Templates to reuse bootstrap components across the pages avoiding code repetition.
   - **`error.html`**: Displays a custom error following the code from the backend.
   - **`index.html`**: Displays a grid of pet profiles, showcasing their photos and details such as name, breed, species, age, and sterilization status, with options to edit or delete each pet, along with a prompt to add new pets if none are present. Also offers a button to navigate to each pet associated tab.
   - **`new_pet`**: Used to register a new pet in the system. It utilizes a multi-step form to gather the pet's information in two distinct sections: Basic Information and Health Data.
   - **`edit_pet.html`**: Used to edit existing pets.
   - **`general_data.html`**: Displays detailed information about a specific pet, including its name, sex, species, breed, age, birth date, adoption date, sterilization status, microchip number, and insurance details, along with options to edit or delete the pet's profile.
   - **`gallery.html`**: Displays a gallery of photos for a particular pet in chronological order, allowing users to view and upload new photos.
   - **`upload_photo.html`**: Provides a form to upload a pet photo, with optional title and date.
   - **`trackers.html`**: Lists all available trackers for a pet (weight, vaccination, deworming, medication) and provides options to add new data.
   - **`tracker_add`**: Provides a form to add new data to a specific tracker.
   - **`weight_graph.html`**: Displays a graph of the pet's weight over time, generated using `matplotlib`. 
   - **`logs.html`**: Displays the logs written by users for a particular pet in chronological order.
   - **`new_entry.html`**: Provide a form to write a new log entry.
   - **`entry.html`**: Displays a log entry for the user to read.
   - **`edit_entry.html`**: Used to edit existing entries in the logs.
   - **`reset_password.html`** and **`restore_password.html`**: Presents forms that allows password recovery using email address.
   - **`email_confirmation.html`** and **`password_reset_email`**: Provide two distinct email templates: one for confirming user registration during sign-up, and the other for initiating a password reset when the user requests a change.

2.  **Static Files** – Ensures a **responsive design** and enhances **user interactivity**. 
   **static/**  
      Holds images, CSS, and JavaScript that are used to style and enhance the user interface.  
      - **CSS**: Includes the `style.css` file that ensures the design of the app is visually pleasing and responsive. This file is responsible for styling all the pages.
      - **JavaScript**: Used for some interactivity, particularly the theme selection, modals and alert messages.
      - **Images**: Contains static images used in the UI.
      - **uploads/**: Folder to save uploaded pet images.
---

## 🏁 Conclusion  
**PetPal** is more than just a project—it's a **practical solution** for pet owners. It has not only helped me improve my web development skills but also has the potential to be a useful tool for someone looking to keep track of their pet’s health and milestones. By combining features like trackers, photo galleries, and logs, PetPal brings together **everything a pet owner needs** to stay organized in one convenient platform.

**🔍Explore the code, check out the video demo, and perhaps even try running the app yourself!**

🐾 Thank you for checking out PetPal! I hope it becomes a valuable tool for pet lovers everywhere. 🚀  
