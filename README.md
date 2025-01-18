
<!-- readme gif -->
![readme gif](./readme-assets/example.gif)

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


## To run the server:
**From the app directory, run the following command:**

```bash
python -m server.main
```