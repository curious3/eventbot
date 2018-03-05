# Bot for finding live events

* Sample project to try out rasa-nlu and rasa-core
* Adapted from the restaurantbot and concertbot examples

## Usage

### Dev environment

Assumes a python3 environment

* virtualenv -p python3 venv
* source venv/bin/activate
* pip install -r requirements.txt

### Build

In the virtualenv,

* python eventbot.py train-nlu
* python eventbot.py train-dialog
* python eventbot.py run