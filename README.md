# HelloApp

## 1. Simple Version : Within hello_app directory:

Modify hello_app/src/App.js to a simple Hello App framework.

Use

```bash
npm start
```

to run the react framwork

```bash
cntl-C
```

to end.

### Result:
<img width="1440" alt="Screenshot 2024-03-25 at 23 09 07" src="https://github.com/Mrkingggg/HelloApp/assets/105716817/979f84cb-0b08-4e6d-8f0c-6ef77b8ad0ca">


## 2. Combine frontend with backend app.py related to project2 ( For Add User Function ) 
### Within Directories: /backend and /frontend 

### Module Add-User with React and Flask_Restful:

source url: localhost:5000/api/users/add ( same in app.py)

#### App.js:

Designed to contain and connect to all api routes. 

#### AppUser.js:

- Form model: Receive from User's input on website including required fields from backend models and database tables.
- Axios: Async tool to wait for user's input and post formdata to api.

in directory /backend:

```bash
flask run
```

start the backend app.

in directory /frontend:

```bash
npm start
```

start frontend React.
