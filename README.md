# Puzzle Hunt

A basic puzzle hunt server app, to be used in conjunction with an App Inventor client

## Download code and initial setup

Open a bash console in PythonAnywhere and run the following commands:

```
git clone https://github.com/chicktech/puzzle-hunt.git
cd puzzle-hunt
. setup.sh
```

## Create a new web app

In PythonAnywhere:

- Select the Web tab and click "Add a new web app".
- On the "Your web app's domain name" screen, click `Next`.
- On the "Select a Python Web framework" screen, choose `Manual Configuration`.
- On the "Select a Python version" screen, choose `Python 3.4`.
- On the "Manual Configuration" screen, click `Next` to finish the wizard.
- Open your WSGI configuration file, and set its contents to this:
  ```python
  import sys
  import os.path
  
  # add your project directory to the sys.path
  project_home = os.path.expanduser(u'~/puzzle-hunt')
  if project_home not in sys.path:
      sys.path = [project_home] + sys.path
  
  # import flask app but need to call it "application" for WSGI to work
  from flask_app import app as application
  application.secret_key = 'super secret key'
  application.config['SESSION_TYPE'] = 'filesystem'
  ```
- Select "Enter path to a virtualenv, if desired", and enter `/home/your-username/.virtualenvs/puzzle-hunt/`
- Under "Static files", add the entry:
  - URL: `/static/`
  - Directory: `/home/your-username/puzzle-hunt/static`
- Click the big green Reload button at the top.
