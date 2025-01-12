
# Project Setup
Create a python virtual environment.
```bash
python -m venv .venv
```

Activate the virtual environment.
linux:
```bash
source .venv/bin/activate
``` 
windows:
```bash
.venv\Scripts\activate
```

After activating the virtual enviornment, install the required packages from the requirements.txt file.
```bash
pip install -r requirements.txt
```

# Git provided project setup:

I have created a branch with the base structure of the project. This branch has the basic file structure and base class and function initialization (without implementation) as well as the required files to get started.

Clone the repository and checkout the `base-structure` branch.


```bash
git clone https://github.com/sockheadrps/WsWithFastAPI.git
cd WsWithFastAPI
git checkout base-structure
```

# Manual project setup
<details><summary> If you prefer to set up the project on your own: </summary>
<br>


From the root directory, create a directory, `app` with an `__init__.py` file in it.  Then, three more directories: `client`, `server`, and `models`.
Each of these directories will have a `__init__.py` file. In both the `client` and `server` directories, create a `main.py`. The models directory will get a `models.py`, and also the server directory will get `templates` and `static` directories.  

Inside app/server/templates, create an `index.html` file.  
Inside app/server/static, create a `styles.css` file and a `scripts.js`.  

The file structure should look like this:
```
app/
    __init__.py
    client/
        __init__.py
        main.py
    server/
        templates/
            index.html
        static/ 
            styles.css
            scripts.js
        __init__.py
        main.py
    models/
        __init__.py
        models.py
```

 </details>

## To run the server:
**From the app directory, run the following command:**

```bash
python -m server.main
```

## To run the client:
**From the app directory, run the following command:**

```bash
python -m client.main
```



