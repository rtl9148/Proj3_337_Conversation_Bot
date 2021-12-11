



import re, json, os
from fractions import Fraction
import requests, spacy
from lxml import html

from .all_ingredient_list import all_ingredient_list

spacy_nlp = spacy.load("en_core_web_sm")


def normalize_keyword(keyword_in, full_words = False):
    if keyword_in:
        word_tokens = spacy_nlp(keyword_in)
        if full_words:
            return ' '.join([i.text for i in word_tokens]).replace(' - ','-')
        else:
            return ' '.join([i.text for i in word_tokens[:-1]]+[word_tokens[-1].lemma_]).replace(' - ','-')
    else:
        return ''

def normalize_keyword_tokens(word_tokens):
    return ' '.join([i.text for i in word_tokens[:-1]]+[word_tokens[-1].lemma_]).replace(' - ','-')
    
def normalize_sentence_tokens(sent_tokens):
    return ' '.join([i.lemma_ for i in sent_tokens]).replace(' - ','-')
    
def original_keyword_tokens(word_tokens):
    return ' '.join([i.text for i in word_tokens]).replace(' - ','-')

vowel_list = {'a': True, 'e': True, 'i': True, 'o': True, 'u': True}

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

all_ingredient_table = {i : True for i in all_ingredient_list}


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

trans_word_table = {}
cur_trans_table = trans_substitute_table
for trans_i in cur_trans_table:
    for change_i in cur_trans_table[trans_i]:
        for word_i in cur_trans_table[trans_i][change_i]:
            if word_i in trans_word_table:
                assert not trans_i in trans_word_table[word_i], str(trans_i)+' '+str(word_i)
                trans_word_table[word_i][trans_i] = change_i
            else:
                trans_word_table[word_i] = {trans_i: change_i}

cooking_tools = ['knife', 'oven', 'pan', 'skillet', 'spoon', 'scale', 'blender', 'bowl', 'whisk', 'grater', 
                 'shear', 'tong', 'towel', 'sponge', 'pot', 'stockpot', 'spatula', 'saucepan', 
                 'colander', 'peeler', 'ladle', 'scoop', 'sieve', 'scissor', 'funnel', 'food mill', 
                 'wooden spoon', 'pepper mill', 'slat shaker', 'oven glove', 'paper towel', 'chef\'s knife', 
                 'cutting board', 'can opener', 'measuring cup', 'measuring spoon', 'mixing bowl', 
                 'vegetable peeler', 'potato masher', 'salad spinner', 'citrus juicer', 'garlic press', 
                 'paring knife', 'bread knife', 'honing rod', 'sharpening rod', 'knife sharpener', 
                 'non-stick skillet', 'stainless steel skillet', 'sauté pan', 'small saucepan', 
                 'medium saucepan', 'large saucepan', 'cast iron skillet', 'cast-iron skillet', 
                 'grill pan', 'sheet pan', 'muffin pan', 'casserole dish', 'broiler pan', 'stirring spoon', 
                 'slotted spoon', 'oven mitt', 'trivet', 'splatter guard', 'thermometer', 'immersion blender', 
                 'kitchen scale', 'food storage containers', 'aluminum foil', 'parchment paper', 'ice cube tray', 'Dutch oven']

cooking_tool_table = {i:True for i in cooking_tools}

cooking_methods = ['roasting', 'baking', 'broiling', 'frying', 'steaming', 'boiling', 'simmering', 'braising', 
                   'poaching', 'blanching', 'grilling', 'sauteing', 'searing', 'pressure cooking', 'slow cooking', 
                   'stewing', 'barbecuing', 'barding', 'broasting', 'microwaving',
                   
                    'basting', 'chopping', 'coddling', 'creaming', 'curdling', 'curing', 'deglazing',
                    'degreasing', 'dredging', 'canning', 'frosting', 'glazing', 'larding', 'low-temperature cooking', 
                    'mincing', 'pickling', 'proofing', 'rendering', 'ricing', 'seasoning', 'shrivelling', 'skimming', 'smoking', 
                    'smothering', 'souring', 'steeping', 'stir frying', 'stuffing', 'sugar panning', 'sweating', 
                    'Swissing', 'thickening', 'velveting']

cooking_method_table_normalized = {normalize_keyword(i):i for i in cooking_methods}
cooking_method_table = {cooking_method_table_normalized[i]:i for i in cooking_method_table_normalized}

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
        
        self.keyword_limit = 3
        
        self.ingredient_token_list = []
        self.direction_token_list = []
        self.ingredient_list = []
        self.recipe_instructions = []
        
        self.has_loaded_recipe = False
        self.started_navigation = False
        self.cur_step_ind = 0
        self.cur_ingredients = []
        self.cur_substitutions = []
        self.cur_tools = []
        self.cur_methods = []
    
    def load_recipe(self,recipe_url):
        response_text = ''
        try :
            if check_url(recipe_url):
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
                        self.recipe_instructions = ['This recipe needs no cooking!']
                    self.has_loaded_recipe = True
                    self.started_navigation = False
                    self.set_cur_step(0)
                    response_text = 'We have found the recipe!'
                else:
                    response_text = 'It looks like the recipe is empty!\nPlease try another recipe!'
            else:
                response_text = 'It looks like an invalid URL! Please try again!'
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
    
    def search_answer(self, query_text, category = 'obj'):
        response_text = 'No worries. I found some references for you:\n'
        if category == 'act':
            response_text += 'Webpages: https://www.google.com/search?q=how+to+{}\n'.format(query_text.replace(' ','+'))
            response_text += 'Videos: https://www.youtube.com/results?search_query=how+to+{}\n'.format(query_text.replace(' ','+'))
        else:
            response_text += 'Webpages: https://www.google.com/search?q=what+is+{}\n'.format(query_text.replace(' ','+'))
            response_text += 'Videos: https://www.youtube.com/results?search_query=what+is+{}\n'.format(query_text.replace(' ','+'))
        return response_text
    
    def search_reference_answer(self, category = 'obj'):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        if category == 'act':
            if self.cur_methods:
                response_text = 'Here is how you do it!\n\n'
                for method_i in self.cur_methods:
                    response_text += 'How to {}:\n'.format(method_i)
                    response_text += 'https://www.google.com/search?q=how+to+{}\n'.format(method_i.replace(' ','+'))
                    response_text += 'https://www.youtube.com/results?search_query=how+to+{}\n\n'.format(method_i.replace(' ','+'))
            else:
                response_text = 'We find no relevant reference in the current step.\n'
                response_text += 'Could you please elaborate on your question?\n'
        else:
            cur_obj_list = self.cur_ingredients + self.cur_tools
            if cur_obj_list:
                if len(cur_obj_list) > 1:
                    response_text = 'You may want to learn about these!\n\n'
                    response_text += 'What is '
                    for obj_i in cur_obj_list:
                        obj_query = 'what is {}'.format(obj_i)
                        response_text += '{}: https://www.google.com/search?q={}\n'.format(obj_i, obj_query.replace(' ','+'))
                else:
                    cur_obj = cur_obj_list[0]
                    obj_query = 'what is {}'.format(cur_obj)
                    response_text = 'You can learn about what is {} here: https://www.google.com/search?q={}\n'.format(cur_obj, obj_query.replace(' ','+'))
            else:
                response_text = 'We find no relevant reference in the current step.\n'
                response_text += 'Could you please elaborate on your question?\n'
        return response_text
            
    def search_parameter(self, q_obj = '', category = 'quantity'):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        cur_unit_list = []
        if category in param_category_rev:
            sub_param_rev = param_category_rev[category]
            cur_unit_list = [i for i in sub_param_rev.keys()]
            cur_unit_list.sort(reverse=True)
            cur_unit_pat = '|'.join(cur_unit_list)
            cur_sentences = self.direction_token_list[self.cur_step_ind].sents if self.cur_step_ind < len(self.direction_token_list) else []
            
            found_group_by_sent = []
            found_obj_by_sent = []
            found_part_by_sent = []
            found_root_by_sent = []
            norm_obj = normalize_keyword(q_obj, full_words = True)
            for sent_i in cur_sentences:
                norm_sent_str = normalize_sentence_tokens(sent_i)
                found_group_by_sent.append(self.match_number_unit_group(norm_sent_str, cur_unit_pat, norm_obj))
                found_obj_by_sent.append(re.search(norm_obj, norm_sent_str))
                found_part_by_sent.append(all([re.search(i, norm_sent_str) for i in norm_obj.split(' ')]))
                found_root_by_sent.append(any([self.match_keyword(word_i, norm_obj) for word_i in norm_sent_str]))
            found_group = tuple()
            #found_possible = tuple()
            if norm_obj and category == 'quantity':
                    for sent_groups in found_group_by_sent:
                        for group_i in sent_groups:
                            if all(group_i):
                                found_group = group_i
                                break
                    if not found_group:
                        for sent_groups in found_group_by_sent:
                            for group_i in sent_groups:
                                if group_i[2]:
                                    found_group = group_i
                                    break
                    if not found_group:
                        norm_obj_words = norm_obj.split(' ')
                        for ingred_line_i in self.ingredient_token_list:
                            norm_sent_str = normalize_sentence_tokens(ingred_line_i)
                            found_obj = re.search(norm_obj, norm_sent_str)
                            if found_obj:
                                search_groups = self.match_number_unit_group(norm_sent_str, cur_unit_pat, norm_obj)
                                if search_groups:
                                    for search_group_i in search_groups:
                                        if search_group_i[2]:
                                            found_group = search_group_i
                                            break
                                    if not found_group:
                                        found_group = search_groups[0]
                        
                        if not found_obj and len(norm_obj_words) > 1:
                            for ingred_line_i in self.ingredient_token_list:
                                norm_sent_str = normalize_sentence_tokens(ingred_line_i)
                                found_obj =  all([re.search(i, norm_sent_str) for i in norm_obj_words])
                                if found_obj:
                                    search_groups = self.match_number_unit_group(norm_sent_str, cur_unit_pat, norm_obj)
                                    if search_groups:
                                        for search_group_i in search_groups:
                                            if search_group_i[2]:
                                                found_group = search_group_i
                                                break
                                        if not found_group:
                                            found_group = search_groups[0]
                                
                        if not found_obj and len(norm_obj_words) > 1:
                            for ingred_line_i in self.ingredient_token_list:
                                norm_sent_str = normalize_sentence_tokens(ingred_line_i)
                                found_obj = any([self.match_keyword(norm_obj_words, i) for i in norm_sent_str])
                                if found_obj:
                                    search_groups = self.match_number_unit_group(norm_sent_str, cur_unit_pat, norm_obj)
                                    if search_groups:
                                        for search_group_i in search_groups:
                                            if search_group_i[2]:
                                                found_group = search_group_i
                                                break
                                        if not found_group:
                                            found_group = search_groups[0]
                        if found_group:
                            response_text = 'You need it in a different step. According to the ingredient list: '
            
            groups_with_unit = []
            #groups_no_unit = []
            for found_obj_i, found_groups_i in zip(found_obj_by_sent, found_group_by_sent):
                if found_obj_i:
                    for group_i in found_groups_i:
                        if group_i[1]:
                            groups_with_unit.append(group_i)
                        #else:
                        #    groups_no_unit.append(group_i)
            if groups_with_unit:
                found_group = groups_with_unit[0]
            #elif groups_no_unit:
            #    found_possible = groups_no_unit[0]
                    
            if not found_group:
                groups_with_unit = []
                #groups_no_unit = []
                for found_part_i, found_groups_i in zip(found_part_by_sent, found_group_by_sent):
                    if found_part_i:
                        for group_i in found_groups_i:
                            if group_i[1]:
                                groups_with_unit.append(group_i)
                            #else:
                            #    groups_no_unit.append(group_i)
                if groups_with_unit:
                    found_group = groups_with_unit[0]
                #elif groups_no_unit:
                #    found_possible = groups_no_unit[0]
                    
            if not found_group:
                groups_with_unit = []
                #groups_no_unit = []
                for found_root_i, found_groups_i in zip(found_root_by_sent, found_group_by_sent):
                    if found_root_i:
                        for group_i in found_groups_i:
                            if group_i[1]:
                                groups_with_unit.append(group_i)
                            #else:
                            #    groups_no_unit.append(group_i)
                if groups_with_unit:
                    found_group = groups_with_unit[0]
                #elif groups_no_unit:
                #    found_possible = groups_no_unit[0]
                
            if found_group:
                response_text += '{} {}\n'.format(self.convert_number(found_group[0]), found_group[1])
            else:
                response_text = 'We could not find the answer in the current step!\n'
            
        return response_text
    
    def search_substituation(self, q_obj):
        has_recipe = self.check_has_recipe()
        if has_recipe:
            return has_recipe
        
        response_text = ''
        norm_obj = normalize_keyword(q_obj)
        found_ingred = ''
        for ingred_i in self.cur_substitutions:
            if self.match_keyword(ingred_i, norm_obj):
                found_ingred = ingred_i
                break
        if found_ingred:
            trans_styles = [(i, trans_word_table[found_ingred][i]) for i in trans_word_table[found_ingred]]
            if len(trans_styles) > 1:
                response_text = 'Here are some substitution options for {}!\n'.format(norm_obj)
                for trans_pair in trans_styles:
                    response_text += '{}: {}\n'.format(trans_pair[0], trans_pair[1])
            else:
                trans_pair = trans_styles[0]
                response_text ='You can replace {} with {} for the {} option\n'.format(norm_obj, trans_pair[1], trans_pair[0])
        else:
            response_text = 'We found no good substitutions for {}\n!'.format(norm_obj)
            response_text += 'There might be some answers here: https://www.google.com/search?q=substitutions+for+{}'.format(norm_obj.replace(' ','+'))
        return response_text
    
    def set_cur_step(self, step_ind):
        self.cur_step_ind = step_ind
        self.cur_step_ind = 0 if self.cur_step_ind < 0 \
            else len(self.recipe_instructions) - 1 if self.cur_step_ind >= len(self.recipe_instructions) \
                else self.cur_step_ind
        
        token_list = self.direction_token_list[self.cur_step_ind] if self.cur_step_ind < len(self.direction_token_list) else []
        found_ingredient = []
        found_substitution = []
        found_cooking_method = []
        found_cooking_tool = []
        
        start_ind = 0
        cur_ind = 0
        while start_ind < len(token_list):
            cur_ind = start_ind + min(self.keyword_limit, len(token_list) - start_ind)
            while cur_ind > start_ind:
                cur_word_tokens = token_list[start_ind:cur_ind]
                cur_normal_word = normalize_keyword_tokens(cur_word_tokens)
                if cur_normal_word in all_ingredient_table:
                    self.add_keyword_to_list(cur_normal_word,found_ingredient)
                elif cur_normal_word in trans_word_table:
                    if not cur_normal_word in found_substitution:
                        found_substitution.append(cur_normal_word)
                elif cur_normal_word in cooking_method_table:
                    self.add_keyword_to_list(cooking_method_table[cur_normal_word],found_cooking_method)
                elif cur_normal_word in cooking_method_table_normalized:
                    self.add_keyword_to_list(cur_normal_word,found_cooking_method)
                elif cur_normal_word in cooking_tool_table:
                    self.add_keyword_to_list(cur_normal_word,found_cooking_tool)
                cur_ind -= 1
            start_ind += 1
            cur_ind = start_ind
        
        self.cur_ingredients = found_ingredient
        self.cur_substitutions = found_substitution
        self.cur_tools = found_cooking_tool
        self.cur_methods = found_cooking_method
        
        
    def match_keyword(self, word_in, check_word):
        len_diff = abs(len(word_in) - len(check_word))
        matched = False
        if len(word_in) <= len(check_word):
            matched = word_in == check_word[len_diff:]
        else:
            matched = word_in[len_diff:] == check_word
        return matched
    
    def add_keyword_to_list(self, keyword_in, cur_keywords, to_update = True):
        found_keyword = False
        to_remove = ''
        for check_i in cur_keywords:
            if self.match_keyword(check_i, keyword_in):
                found_keyword = True
                to_remove = check_i if len(keyword_in) > len(check_i) else ''
                break
        if found_keyword:
            if to_remove and to_update:
                cur_keywords.remove(to_remove)
                cur_keywords.append(keyword_in)
        else:
            cur_keywords.append(keyword_in)
        return found_keyword
    
    def match_number_unit_group(self, str_in, unit_pat, obj_in):
        found_group = re.findall('([1-9]/[1-9][0-9]*|[1-9][0-9]*|[\u00BC\u00BD\u00BE\u2150-\u215F])(?:\s+({})\s+)?\s*({})?'.format(unit_pat, obj_in), str_in)
        return found_group
    
    def convert_number(self, str_in):
        if '/' in str_in:
            return Fraction(str_in)
        elif str_in in dict_vulgar_fraction_unicodes:
            return  Fraction(dict_vulgar_fraction_unicodes[str_in])
        elif str_in.isdigit():
            return int(str_in)
        elif re.search('[0-9]+\.[0-9]+', str_in):
            return float(str_in)
        else:
            return ''
            
    def check_has_recipe(self):
        return '' if self.has_loaded_recipe else 'Please enter a URL for learning about the recipe!'
    
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
                q_match = re.search('^parameter (temperature|duration|quantity) ([A-Za-z]*)',next_input)
                if q_match:
                    print(testing.search_parameter(q_match[2], q_match[1]))
                else:
                    q_obj = re.search('^what is it',next_input)
                    q_cat = 'obj'
                    if not q_obj:
                        q_obj = re.search('^how to do it',next_input)
                        q_cat = 'act'
                    if q_obj:
                        print(testing.search_reference_answer(q_cat))
                    else:
                        q_obj = re.search('^what is\s*(.+)',next_input)
                        if not q_obj:
                            q_obj = re.search('^how to\s*(.+)',next_input)
                        if q_obj:
                            print(testing.search_answer(q_obj[1]))
                        else:
                        
                            q_obj = re.search('^substitute\s*(.+)',next_input)
                            if q_obj:
                                print(testing.search_substituation(q_obj[1]))
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
    
        

