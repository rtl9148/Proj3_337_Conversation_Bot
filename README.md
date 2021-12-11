# Proj3_337_Conversation_Bot
https://github.com/rtl9148/Proj3_337_Conversation_Bot

## SETUP

Install from the requirement.txt 

or 

Run the following command: 
(Only the following libraries are used, but setting up a new environment with these commands is not tested)

python -m pip install requests

pip install lxml

pip install -U spacy

python -m spacy download en_core_web_sm

pip3 install rasa


## RUNNING Rasa

To run Rasa, first run the following command to start actions server:

rasa run actions

(We had an issue runing it from the top level folder once, i.e. Rasa_demo, but it works now. When encountering that issue, run this command from Rasa_demo/actions)

On a different window, run the following command to start Rasa shell:

rasa shell

The model is trained and included, but to train the model again, run the following command:

rasa train

Please follow the examples in the nlu.yml for utterences

## RUNNING Python code

Since Rasa is working, there is only a very simple ui, testing_ui(), for the python backend code. Run recipe_assistant.py will call the UI by default. The commands are as followings in the format of "command - what it does", since no prompt is included for UI.
ingred - show ingredient list
cur - show current step
next - go to next step
prev - go to previous step
parameter (temperature|duration|quantity) (object) - get parameter for temperature or duration or quantity for an object
substitute (object) - find substitution for an object
what is it - for vague question
how to do it - for vague question
what is (object) - for direct question 
how to (action) - for direct question

## Potential issue

Try different importing path if the it complains about no module found in recipe_assistant.py and actions.py

from .recipe_assistant import recipe_assistant

or

from recipe_assistant import recipe_assistant

from .all_ingredient_list import all_ingredient_list

or

from all_ingredient_list import all_ingredient_list





