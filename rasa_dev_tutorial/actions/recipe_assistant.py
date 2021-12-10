



import re, json, os
from fractions import Fraction
import requests, spacy
from lxml import html

from all_ingredient_list import all_ingredient_list

spacy_nlp = spacy.load("en_core_web_sm")


def normalize_keyword(keyword_in):
    word_tokens = spacy_nlp(keyword_in)
    return ' '.join([i.text for i in word_tokens[:-1]]+[word_tokens[-1].lemma_]).replace(' - ','-')

def normalize_keyword_tokens(word_tokens):
        return ' '.join([i.text for i in word_tokens[:-1]]+[word_tokens[-1].lemma_]).replace(' - ','-')
    
def original_keyword_tokens(word_tokens):
    return ' '.join([i.text for i in word_tokens]).replace(' - ','-')

dict_vulgar_fraction_unicodes = {
    '\u00BC' : '1/4',
    '\u00BD' : '1/2',
    '\u00BE' : '3/4',
    '\u2150' : '1/7',
    '\u2151' : '1/9',
    '\u2152' : '1/10',
    '\u2153' : '1/3',
    '\u2154' : '2/3',
    '\u2155' : '1/5',
    '\u2156' : '2/5',
    '\u2157' : '3/5',
    '\u2158' : '4/5',
    '\u2159' : '1/6',
    '\u215A' : '5/6',
    '\u215B' : '1/8',
    '\u215C' : '3/8',
    '\u215D' : '5/8',
    '\u215E' : '7/8',
    '\u215F' : '1',
    '\u2189' : '0/3'
}

meta_keys = ['prep', 'cook', 'total', 'servings', 'yield', 'additional']

to_healthy_substitution = {
    "whole-grain brown rice":  ["rice", "brown rice", "white rice", "long grain white rice", "uncooked instant rice", "instant rice", "wild rice", "uncooked white rice", "uncooked brown rice"],
    "skim milk":               ["milk", "whole milk", "heavy cream", "half-and-half", "evaporated milk", "2% milk", "heavy whipping cream", "buttermilk", "warm milk", "cold milk"],
    "light margarine":         ["butter", "shortening", "margarine", "salted butter", "unsalted butter", "butter or margarine", "butter OR margarine"],
    "dark chocolate chips":    ["chocolate chips", "milk chocolate chips", "chocolate morsels", "bittersweet chocolate chips", "BAKER'S Semi-Sweet Baking Chocolate, melted", "chips"],
    "vegetable stock":         ["chicken broth", "chicken stock", "beef stock", "beef broth", "chicken base", "broth", "stock"],
    "ground turkey":           ["ground beef", "lean ground beef", "ground pork", "ground veal", "beef"],
    "whole-wheat flour":       ["all-purpose flour", "flour", "enriched flour"],
    "chicken sausage":         ["sausage", "pork sausage", "bulk pork sausage"],
    "extra-virgin olive oil:": ["olive oil", "canola oil", "vegetable oil", "canola", "oil"], 
    "dark chocolate":          ["chocolate", "milk chocolate", "semi-sweet chocolate"],
    "maple syrup":             ["corn syrup", "high fructose corn syrup", "light corn syrup", "syrup"],
}

to_unhealthy_substitution = {
    "whole milk":           ["milk", "skim milk", "2% milk", "1% milk"],
    "milk chocolate chips": ["dark chocolate chips", "chocolate chips", "chocolate morsels", "semi-sweet chocolate chips", "semisweet chocolate chips", "bittersweet chocolate chips"],
    "beef broth":           ["vegetable stock", "chicken stock", "stock"],
    "vegetable oil":        ["canola oil", "olive oil", "extra-virgin olive oil", "avocado oil", "sesame oil", "coconut oil", "oil"],
    "ground beef":          ["ground chicken", "ground turkey", "lean ground beef", "lean ground chicken", "lean ground turkey", "lean", "ground"],
    "pork sausage":         ["chicken sausage", "turkey sausage", "lean sausage"],
    "salted butter":        ["unsalted butter", "butter substitute", "margarine", "light margarine"]
}

lactose_free_substitution = {
    "almond milk":              ["milk", "skim milk", "cream", "whole milk", "heavy cream", "half-and-half", "evaporated milk", "2% milk", "heavy whipping cream", \
                                "buttermilk", "warm milk", "cold milk", "creamer", "coffee creamer"],
    "non-dairy frozen dessert": ["ice cream", "frozen yogurt", "gelato"],
    "vegan butter":             ["butter", "salted butter", "unsalted butter", "margarine", "butter OR margarine", "butter or margarine"],
    "dark chocolate":           ["milk chocolate", "semi-sweet chocolate", "chocolate"]
}

vegetarian_substitutes = {
    "tofu" : ["chicken","chicken breast", "steak", "tenderloin", "sirloin", "filet mignon", "flank", "t-bone steak","beef",  "meatballs", "beef stew", "chorizo", "bison" \
                "buffalo wings", "chicken wings", "wings", "chicken thigh", "chicken thighs","thigh","thighs","chicken leg","chicken legs", "chicken drumstick","chicken drumsticks", "drumsticks", \
                "chicken nuggets", "nuggets", "pork", "bacon", "Bacon", "OSCAR MAYER Bacon", "hot dog", "italian sausage", "Italian Sausage", "sausage","brat","kielbasa","cutlet","duck","lamb","goat","falafel","liver","gyro","venison", \
                "bluefish","butter fish","cat fish","catfish","dogfish","salmon","cod", "atlantic cod","black cod","herring","mahi-mahi","perch","trout","sardine","bass", \
                "tuna", "albacore tuna", "bigeye tuna","bluefin tuna","dogtooth tuna","shrimp","crab", "crabmeat", "cray fish","lobster","clam","octopus","squid","eel", \
                "elk", "fish", "flounder", "fly-fish", "goose", "lingcod", "mackrel", "monkfish", "mussel", "ostrich", "emu", "oyster", "pacific cod", "pacific sanddab", 
                "pacific snapper", "parrotfish", "patagonian toothfish", "rock cod", "rockfish", "sablefish", "scallop", "sea bass", "sea cucumber", "sea urchin",\
                "sea scallop", "shark", "shellfish", "snail", "snapper", "sturgeon", "swordfish", "tilapia", "tuna fish", "yellowfin tuna", "whitefish", "white carp"],
    "seitan" : [ "ham", "turkey","hamburger", "hamburgers", "cheeseburger", "cheeseburgers", "burger", "prime rib", "ribs", "rib","brisket", "halibut" "fillets halibut"],
    "mushroom" : ["salami","pepperoni","bologna", "anchovy"],
    "vegetable broth" : ["chicken broth", "beef broth"],
    "vegetable stock" : ["chicken stock", "beef stock"],
    "vegetable shortening" : ["lard"],
    "soy sauce" : ["worcestershire sauce"]
}
    
vegetarian_substitutes_rev = {
    "chicken" : ["tofu"],
    "beef" : ["seitan"],
    "chicken broth" : ["vegetable broth", "vegetable stock"],
    "lard" : ["vegetable shortening", "shortening"]
}

mexican_substitute = {
    "oregano" : ["thyme", "marjoram"],
    "cilantro" : ["coriander", "curry powder", "garam masala","caraway", "parsley","basil"],
    "cumin" : ["caraway seeds", "black cumin"],
    "paprika" : ["cayenne pepper", "chili powder"],
    "pinto beans" : ["black beans", "black eyed peas", "black-eyed peas", "garbanzo beans", "kidney beans", "lima beans"],
    "brown rice" : ["white rice", "jasmine rice", "basmati rice" "wild rice", "rice"], 
    "lime" : ["lemon"]
}

trans_substitute_table = {'vegetarian':vegetarian_substitutes, 
                          'non-vegetarian': vegetarian_substitutes_rev,
                          'Mexican': mexican_substitute, 
                          'healthy': to_healthy_substitution,
                          'unhealthy': to_unhealthy_substitution,
                          'lactose-free':lactose_free_substitution,}

### Changes for assistant
param_table = {
    'temperature': {
        'degree': ['degree'], 
        'C': ['C'], 
        'F': ['F'],
        },
    'duration': {
        'hour': ['hr', 'hour'], 
        'minute': ['min', 'minute'],
        'second': ['sec', 'second'],
        },
    'quantity': {
        'teaspoon': ['teaspoon', 'tsp.'],
        'tablespoon': ['tablespoon', 'tbl.', 'tbs.', 'tbsp.'],
        'fluid ounce': ['fluid ounce', 'fl oz'],
        'gill': ['gill'],
        'cup': ['cup'],
        'pint': ['pint', 'pt', 'fl pt'],
        'quart': ['quart', 'qt', 'fl qt'],
        'gallon': ['gallon', 'gal'],
        'ml': ['ml', 'milliliter', 'millilitre', 'cc', 'mL'],
        'l': ['l', 'liter', 'litre', 'L'],
        'dl': ['dl', 'deciliter', 'decilitre', 'dL'],
        'pound': ['pound', 'lb', '#'],
        'ounce': ['ounce', 'oz'],
        'mg': ['mg', 'milligram', 'milligramme'],
        'g': ['g', 'gram', 'gramme'],
        'kg': ['kg', 'kilogram', 'kilogramme'],
        'mm': ['mm', 'millimeter', 'millimetre'],
        'cm': ['cm', 'centimeter', 'centimetre'],
        'm': ['m', 'meter', 'metre'],
        'inch': ['inch', 'in', '"'],
        'pinch': ['pinch'],
        }
}

param_category_rev = {}
for category_i in param_table:
    for norm_unit_i in param_table[category_i]:
        for unit_var_i in param_table[category_i][norm_unit_i]:
            if not category_i in param_category_rev:
                param_category_rev[category_i] = {}
            assert not unit_var_i in param_category_rev[category_i]
            param_category_rev[category_i][unit_var_i] = norm_unit_i

param_rev_table = {}
for category_i in param_table:
    for norm_unit_i in param_table[category_i]:
        for unit_var_i in param_table[category_i][norm_unit_i]:
            assert not unit_var_i in param_rev_table
            param_rev_table[unit_var_i] = (category_i, norm_unit_i)

subs_table = {}
for trans_i in trans_substitute_table:
    for change_i in trans_substitute_table[trans_i]:
        for word_i in trans_substitute_table[trans_i][change_i]:
            if word_i in subs_table:
                assert all([trans_i != i[0] for i in subs_table[word_i]])
                subs_table[word_i].append((trans_i, change_i))
            else:
                subs_table[word_i] = [(trans_i, change_i)] 
            
start_pat = '(?:^|\s)'
end_pat = '(?:$|\s)'
number_pat = '([1-9]/[1-9][0-9]*|[1-9][0-9]*|[\u00BC\u00BD\u00BE\u2150-\u215F])'



# =============================================================================
# unit_list = [i for i in param_rev_table.keys()]
# unit_list.sort(reverse=True)
# unit_pat = number_pat+'\s*('+'|'.join(unit_list)+')'
# subs_list = [i for i in subs_table.keys()]
# subs_list.sort(reverse=True)
# subs_pat = '|'.join(subs_list)
# =============================================================================

def check_url(url_in):
    return re.search('https://www.allrecipes.com/recipe/[0-9]+/', url_in)

class recipe_assistant():
    def __init__(self):
        self.webpage = None
        self.webxml = None
        
        self.ingredient_token_list = []
        self.direction_token_list = []
        self.ingredient_list = []
        self.recipe_instructions = []
        
        self.has_loaded_recipe = False
        self.started_navigation = False
        self.cur_step_ind = 0
        self.cur_ingredients = []
        self.cur_tools = []
        self.cur_verbs = []
        self.cur_methods = []
    
    def load_recipe(self,recipe_url):
        response_text = ''
        try :
            self.webpage = requests.get(recipe_url)
            self.webxml = html.fromstring(self.webpage.content)
            
            ingredient_list = self.read_ingredients()
            direction_list = self.read_directions()
            
            if ingredient_list or direction_list:
                self.ingredient_token_list = [spacy_nlp(i) for i in self.read_ingredients()]
                self.direction_token_list = [spacy_nlp(i) for i in self.read_directions()]
                self.recipe_instructions = []
                if ingredient_list:
                    self.ingredient_list = '\n'.join(self.read_ingredients())
                else:
                    self.ingredient_list = 'You need no ingredients for this recipe!'
                if direction_list:
                    self.recipe_instructions = ['\n'.join([str(j) for j in i.sents]) for i in self.direction_token_list]
                else:
                    self.recipe_instructions = ['This recipe need no cooking!']
                self.has_loaded_recipe = True
                self.started_navigation = False
                self.set_cur_step(0)
                response_text = 'We have found the recipe!'
            else:
                response_text = 'It looks like the recipe is empty!\nPlease try another recipe!'
        except :
            response_text = 'We failed to read the recipe!\nPlease try again or try another recipe!'
        return response_text
    
    def show_ingredients(self):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = self.ingredient_list
        return response_text
    
    def show_current_step(self):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        self.started_navigation = True
        response_text = self.recipe_instructions[self.cur_step_ind]
        return response_text
    
    def navigate_by_number(self, next_step):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        next_ind = int(next_step) - 1 if next_step.isdigit() else None
        if next_ind != None and next_ind < len(self.recipe_instructions) and next_ind >= 0:
            self.started_navigation = True
            response_text = self.recipe_instructions[next_ind]
            self.set_cur_step(next_ind)
        else:
            response_text = 'There is no step {} in the recipe!'.format(next_step)
        return response_text
            
    def navigate_to_next(self):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        next_ind = self.cur_step_ind + 1 if self.started_navigation else self.cur_step_ind
        self.started_navigation = True
        if next_ind < len(self.recipe_instructions):
            response_text = self.recipe_instructions[next_ind]
            self.set_cur_step(next_ind)
        else:
            response_text = 'There is no more steps in the recipe!'
        return response_text
            
    def navigate_to_previous(self):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        next_ind = self.cur_step_ind - 1
        if next_ind >= 0:
            response_text = self.recipe_instructions[next_ind]
            self.set_cur_step(next_ind)
        else:
            response_text = 'We are already at the beginning of the recipe!'
        return response_text
    
    def search_answer(self, query_text = ''):
        response_text = 'No worries. I found some references for you:\n'
        response_text += 'Webpages: https://www.google.com/search?q={}\n'.format(query_text.replace(' ','+'))
        response_text += 'Videos: https://www.youtube.com/results?search_query={}\n'.format(query_text.replace(' ','+'))
        return response_text
    
    def search_reference_answer(self, category = 'obj'):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        #to do
        if category == 'act':
            pass
        else:
            pass
        response_text = ''
        return response_text
            
    def search_parameter(self, q_obj = '', category = 'quant'):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        #to do
        response_text = ''
        if category in param_category_rev:
            found_param = ''
            sub_param_rev = param_category_rev[category]
            unit_list = [i for i in sub_param_rev.keys()]
            unit_list.sort(reverse=True)
            quant_pat = start_pat+number_pat+'\s?('+'|'.join(unit_list)+')?'+end_pat
            
        return response_text
    
    def set_cur_step(self, step_ind):
        self.cur_step_ind = step_ind
        assert self.cur_step_ind >= 0 and self.cur_step_ind < len(self.recipe_instructions)
        #to do
        
        
    def match_ingredient(self, ingredient_str):
        #to do
        pass
            
    def check_has_recipe(self):
        return '' if self.has_loaded_recipe else 'Please enter a URL for navigating the recipe!'
    
    def read_ingredients(self):
        ingredient_items = [str(i) for i in self.webxml.xpath('//div[@class="recipe-shopper-wrapper"]//span[@class="ingredients-item-name"]/text()')]
        return ingredient_items
    
    def read_directions(self):
        direction_list = [str(i) for i in self.webxml.xpath('//section[@class="component recipe-instructions recipeInstructions container"]//li[@class="subcontainer instructions-section-item"]//div[@class="paragraph"]//p/text()')]
        return direction_list

def testing_ui():
    testing = recipe_assistant()
    next_input = False
    while next_input != 'quit':
        next_input = input('\'quit\' to quit:\n')
        if next_input.isdigit():
            print(testing.navigate_by_number(next_input))
        elif next_input == 'cur':
            print(testing.show_current_step())
        elif next_input == 'next':
            print(testing.navigate_to_next())
        elif next_input == 'prev':
            print(testing.navigate_to_previous())
        elif next_input == 'ingred':
            print(testing.show_ingredients())
        else:
            q_url = check_url(next_input)
            if q_url:
                print(testing.load_recipe(next_input))
            else:
                q_obj = re.search('^what is\s*(.+)',next_input)
                if not q_obj:
                    q_obj = re.search('^how to\s*(.+)',next_input)
                if q_obj:
                    print(testing.search_answer(q_obj[1]))
                elif next_input == 'quit':
                    print('Terminated')
                else:
                    print('Invalid command')

if __name__ == '__main__':
    
    testing_ui()
                
# =============================================================================
#     testing = recipe_assistant()
#     print(testing.load_recipe('https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/'))
# =============================================================================
    
        

