

class recipe_assistant():
    def __init__(self):
        pass
    
    def navigate_by_step_num(self, q_text:str, q_slot_1:int):
        return 'Step {}'.format(q_slot_1)
    
    def answer_how(self, q_text:str, q_slot_1:str):
        return 'https://www.google.com/search?q={}'.format(q_text.replace(' ','+'))

if __name__ == '__main__':
    RA_example = recipe_assistant()
