# Bug Tracker App Py

This app is hosted at: https://bugtracker-app-py.herokuapp.com/

## What is Bug Tracker App Py

Writting down bugs and features that an application might need during its lifecycle can be cumbersome. This desktop web application allows users to create projects, add members to the project, and assing tickets (feature or bug) in order to keep track of their progress. Work individually or collaborate with a group of engineers in order to build applications.

![image](https://user-images.githubusercontent.com/30029618/171909042-8fd42697-ac28-46f7-9cb6-d5eff618d7c6.png)

![image](https://user-images.githubusercontent.com/30029618/171909107-232533b2-bbbe-473c-a891-39f08d5dc745.png)

![image](https://user-images.githubusercontent.com/30029618/171909212-d8287d6d-382e-44f1-a39f-cfeb7c40b93c.png)

![image](https://user-images.githubusercontent.com/30029618/171909527-d33552e6-8fa3-4030-845b-3aee0e09158d.png)

# How to use it

- Sign up for a free account
- Navigate to "Projects" on the sidebar
- Click on "Create Project"
  - Add a project name
  - Add a description for the project
  - Add members for the project. Multiple members can be selected by holding the CTRL key (COMMAND key on mac)
  - Click on "Create Project" button
- On the Projects page, click on "Details" nex to the newly created project
- Click on "Add Ticket"
  - Add a ticket name
  - Assign a developer for the ticket
  - Select ticket type, priority and status
  - Add a description
  - Click on "Create Ticket"
- All of your projects and tickets can be accessed from the sidebar
- Archived projects are projects that are closed
  - To close a project, the owner must edit the project and click on the "Close Project" button
- Archived tickets are tickets with a "Resolved" status
  - To close a ticket, the ticket must be edited and set to "Resolved" status

# For Developers

## Getting Started

### Prerequisites

You will need need Python3 (or latest version of Python installed) It is advised to use a virtual environment. Additionally, you will need a PostgreSQL database available locally.

After starting PostgreSQL, create a database from the command line

```
CREATE DATABASE bugtracker_db
```

### Environment Variables

This app uses environemnt variables to load keys from your environment.
These should be placed in a file in the root directory named ```.env```

```
SECRET_KEY=<Your flask secret key>
IS_DEV=<Set to TRUE if testing or FALSE if in production (deployed)>
DATABASE_URL=postgresql://YOUR_DATABASE_USER:YOUR_DATABASE_PASSWORD@localhost/bugtracker_db
```

### Setup & Installation

Browse to a folder where this project will be saved and open a command line.

Clone the repository

```
git clone <repo-url>
```

Install dependencies

```
pip install -r requirements.txt
```

### Run the app

```
python3 app.py
```

### Migration

This application utilizes flask-migrate to update the database. Please read more about how to run migrations and execute migrations in the flask-migrate website: https://flask-migrate.readthedocs.io/en/latest/


## Built With
- JavaScript
- Python
- Flask
- PostgreSQL
- HTML / CSS
- DataTables.js
- Bootstrap
- Font Awesome
