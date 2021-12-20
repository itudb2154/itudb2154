class Comment:
    def __init__(self, user_id, recipe_id, message, created_date, updated_date, text_color, language, user_name):
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.message = message
        self.created_date = created_date
        self.updated_date = updated_date
        self.text_color = text_color
        self.language = language
        self.user_name = user_name