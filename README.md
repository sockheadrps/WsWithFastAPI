
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

I have created a branch with the base structure of the project. This branch has the basic file structure and base class and function initialization (without implementation) as well as the required files to get started. Just fill in the functions and classes that have had their implementation removed and replaced with `pass`. These missing implementations exist in app.server.utilities.models.models, app.server.utilities.manager, and app.server.main.

The CSS, JS and HTML is provided, as well as the object that gets the sensor and hardware data from the PC.

Complete code is available on the main branch.

Clone the repository and checkout the `base-structure` branch.


```bash
git clone https://github.com/sockheadrps/WsWithFastAPI.git
cd WsWithFastAPI
git checkout base-structure
```


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



