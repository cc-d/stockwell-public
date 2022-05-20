## Overview

This took quite a bit of work to complete, so there are many cases I didn't implement things in a certain way with the intentions of saving time.

This list includes: no input validation (usernames, words, json data), assuming the json data is structured in a certain way (included list has 3100 english words all lowercase without special characters, both the original wordlist I used and the processing script are included), extremely minimal css styling, etc.

## Install

install python3 ```apt install python3```

install pip ```apt install python3-pip```

create virtual environment ```python3 -m venv venv``` then ```source venv/bin/activate```

install pip packages ```pip3 install -r requirements.txt```

edit ```secret.txt``` with the correct google api values

(optional) ```python3 models.py``` if you do not want to use the included database, and want to start from zero records - this deletes the existing database

## Run

run the start script ```bash run.sh```

## Usage

navigate to http://127.0.0.1:5000