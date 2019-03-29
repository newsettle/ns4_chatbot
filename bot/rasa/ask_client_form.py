from rasa_core.actions.forms import FormAction
from rasa_core.actions.forms import EntityFormField
from rasa_core.actions.action import ActionRestart
from rasa_core.events import SlotSet
from rasa_core.actions import Action

# -*- coding: UTF-8 -*-
class AskClientInfoForm(FormAction):

    RANDOMIZE = False

    @staticmethod
    def required_fields():
        return [
            #EntityFormField(<Entity>,<Slot>),
            EntityFormField("phone", "phone"),
            EntityFormField("company", "company"),
            
        ]

    def name(self):
        return 'action_ask_client'

    def submit(self, dispatcher, tracker, domain):
        # send utter default template to user
        dispatcher.utter_template("utter_ask_morehelp")
        # ... other code
        return []