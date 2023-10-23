# Miku
## Overview

A Discord bot using Discord.py that can play, pause, and shuffle through youtube music.

### Prerequisites

1. Recommended IDE: [Visual Studio Code](https://code.visualstudio.com/)
2. [Python](https://www.python.org/) - Latest version (Ensure environment variables are set up)


## Getting Setup

In order to run the program, you will need to install the necessary dependencies. To ensure that this is done correctly and doesn't interfere with other projects, you will need to create a virtual environment.

To setup your virtual environment (venv) open the command palette 
(Ctrl+Shift+P) and search for `Python: Create Environment` and select it. Use the "Venv" environment type. Once your virtual environment is running, ensure that you are using that environment's interpteter. To do so go to the command palette again and search for `Python: Select Interpreter`. You should have the python interpreter with .venv selected.

### Installing Dependencies

Once you are certain your virtual environment is up and running and you are using that environment's interpreter, you will need to install the dependencies. 

Use the command: `pip install -r requirements.txt`

###Adding AuthCode

Create an "authcode.txt" file in project directory and add your discord bot authentication code to the text file.

### Running the program

Use the command: `python miku.py`

Proceed to the link given in your console and you should be able to test the program.
