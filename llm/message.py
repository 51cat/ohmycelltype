class Message:
    def __init__(self, system_prompt) -> None:

        self._message = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, input):
        self._message.append({
            "role": "user" , 
            "content": input
            })
    
    def add_ai_message(self, input):
        self._message.append({
            "role": "assistant" , 
            "content": input
            })
    
    @property
    def message(self):
        return self._message
    
    def show(self):
        print(self._message)