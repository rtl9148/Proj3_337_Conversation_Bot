# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .recipe_assistant import recipe_assistant

agent = recipe_assistant()

##RECIPE RETRIEVAL------------------------------------------------------------------------------------------
class ActionGetRecipeInfo(Action):

    def name(self) -> Text:
        return "action_get_recipe_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        recipe_url = tracker.get_slot('recipe_url')
        dispatcher.utter_message(text="recipe_url is %s" % recipe_url)
        return_message = agent.load_recipe(recipe_url)
        dispatcher.utter_message(text=return_message)
        return []
    
        ##code for setting a slot name to none
        #return [SlotSet(‘slot_name’, None)]
        
##NAVIGATION UTTERANCES-----------------------------------------------------------------------------------------

##This class will be used to print whatever step we are currently on. 
##IF CURRENT STEP HAS NOT BEEN INITIALIZED, THEN START IT AT STEP 1
class ActionPrintCurrentStep(Action):

    def name(self) -> Text:
        return "action_print_current_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        
#         if recipe URL is none:
#             dispatcher.utter_message(text="please enter url before navigating recipe")
#         else:
#           ##do something with list of steps for recipe based on step number and put it in step_text
#             dispatcher.utter_message(text="Step {current_step} is: {step_text}")
        
        return_message = agent.show_current_step()
        dispatcher.utter_message(text=return_message)
        return []

class ActionPrintNextStep(Action):

    def name(self) -> Text:
        return "action_print_next_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        
        return_message = agent.navigate_to_next()
        dispatcher.utter_message(text=return_message)
        return []

class ActionPrintPreviousStep(Action):

    def name(self) -> Text:
        return "action_print_previous_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        
        return_message = agent.navigate_to_previous()
        dispatcher.utter_message(text=return_message)
        return []

##This action will be used whenever a user explicitly wants to go to a nth step
class ActionGoToStep(Action):

    def name(self) -> Text:
        return "action_go_to_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        

        step_number = tracker.get_slot('step_no')
        return_message = agent.navigate_by_number(step_number)
        dispatcher.utter_message(text=return_message)
        return []
    
class ActionPrintIngredientList(Action):

    def name(self) -> Text:
        return "action_print_ingredient_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       #no slots needed here, just print this out
#         if recipe URL is none:
#             dispatcher.utter_message(text="please enter url before navigating recipe")
#         else:
#           ##do something with list of steps for recipe based on step number and put it in step_text
#             dispatcher.utter_message(text="Here are the ingredients for {recipe_title here!!!}: {ingredients_list here!!!}")
        
        return_message = agent.show_ingredients()
        dispatcher.utter_message(text=return_message)  
        return []
    
##HOWTO STUFF-------------------------------------------------------------------------------------
class ActionLookupQuestion(Action):

    def name(self) -> Text:
        return "action_lookup_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       #no slots needed here, just print this out
        user_question = tracker.get_slot('user_question')
        ##put + in between each word of user question, then return result url
        
        return_message = agent.search_answer(user_question)
        dispatcher.utter_message(text=return_message)
        return []
    
class ActionLookupQuestionVague(Action):

    def name(self) -> Text:
        return "action_lookup_question_vague"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       #lookup question based on current step we are on
       #if current step is none or url is not initialized then output do not understand message
        
        
        ##put + in between each word of user question, then return result url
        
        #dispatcher.utter_message(text="No worries. I found a reference for you:  https://www.youtube.com/results?search_query={user_question_plus}")
        
        dispatcher.utter_message(text="Found vague question")
        return []
    
class ActionRespondToGratitude(Action):

    def name(self) -> Text:
        return "action_respond_to_gratitude"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       #no slots needed here, just print this out
        user_question = tracker.get_slot('recipe_url')
        
#         if recipe URL is none:
#             ##if we have not started navigating the steps of the recipe, then just say that, otherwise ask them to go to next step.
#             if current step is None: 
#                 dispatcher.utter_message(text="No worries. Should I show you the 1st step?")
#             else:
#                 dispatcher.utter_message(text="No worries. Should I continue to the next step?")

        dispatcher.utter_message(text="Found respond to gratitude")
        return []
    
class ActionLookupIngredientAmount(Action):

    def name(self) -> Text:
        return "action_lookup_ingredient_amount"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       #no slots needed here, just print this out
        amount_item = tracker.get_slot('amount_item')
        
        #just printing out item right now, we need to find the amount
        dispatcher.utter_message(text="Found amt item %s" % amount_item)
        return []


class ActionLookupIngredientSubstitution(Action):

    def name(self) -> Text:
        return "action_lookup_ingredient_substitution"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
       #no slots needed here, just print this out
        ingred_subst = tracker.get_slot('ingred_subst')
        
        #just printing out the ingredient right now, we need to find substitution
        dispatcher.utter_message(text="Found ingredient substitution %s" % ingred_subst)
        return []
    
    
