from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

from policy import EventPolicy
from rasa_core import utils
from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.memoization import MemoizationPolicy

logger = logging.getLogger(__name__)


class EventAPI(object):
    def search(self, artiste):
        print("Searching for events for " + artiste)
        return [{"artist": artiste, "review": 3, "albums": 21}]


class ActionSearchConcerts(Action):
    def name(self):
        return 'action_search_concerts'

    def run(self, dispatcher, tracker, domain):
        concert_artist = tracker.get_slot("artist")
        if concert_artist is None:
            dispatcher.utter_message("Could not find concerts")
            return []
        else:
            dispatcher.utter_message("looking for concerts by " + concert_artist)
            concerts = EventAPI().search(concert_artist)
            return [SlotSet("matches", concerts)]


class ActionSuggest(Action):
    def name(self):
        return 'action_suggest'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("here's what I found:")
        dispatcher.utter_message(str(tracker.get_slot("matches")))
        return []


def train_dialog(domain_file="domain.yml",
                   model_path="models/dialogue",
                   training_data_file="data/stories.md"):
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(), EventPolicy()])

    agent.train(
            training_data_file,
            max_history=3,
            epochs=400,
            batch_size=100,
            validation_split=0.2
    )

    agent.persist(model_path)
    return agent


def train_nlu():
    from rasa_nlu.converters import load_data
    from rasa_nlu.config import RasaNLUConfig
    from rasa_nlu.model import Trainer

    training_data = load_data('data/dialog_data.json')
    trainer = Trainer(RasaNLUConfig("nlu_model_config.json"))
    trainer.train(training_data)
    model_directory = trainer.persist('models/nlu/', fixed_model_name="current")

    return model_directory


def run(serve_forever=True):
    interpreter = RasaNLUInterpreter("models/nlu/default/current")
    agent = Agent.load("models/dialogue", interpreter=interpreter)

    if serve_forever:
        agent.handle_channel(ConsoleInputChannel())
    return agent


if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")

    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
            'task',
            choices=["train-nlu", "train-dialog", "run"],
            help="what the bot should do - e.g. run or train?")
    task = parser.parse_args().task

    # decide what to do based on first parameter of the script
    if task == "train-nlu":
        train_nlu()
    elif task == "train-dialog":
        train_dialog()
    elif task == "run":
        run()
    else:
        warnings.warn("Need to pass either 'train-nlu', 'train-dialog' or "
                      "'run' to use the script.")
        exit(1)
