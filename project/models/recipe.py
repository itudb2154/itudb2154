class Recipe:
    def __init__(self, user_id, recipe_name, meal_name, photo_url, instruction, portion, drink_alternate, video_url):
        self.user_id = user_id
        self.recipe_name = recipe_name
        self.meal_name = meal_name
        self.photo_url = photo_url
        self.instruction = instruction
        self.portion = portion
        self.drink_alternate = drink_alternate
        self.video_url = video_url