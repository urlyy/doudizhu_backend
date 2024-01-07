class Card:
    suit: str
    number: str

    def __init__(self, number, suit=""):
        self.suit = suit
        self.number = number

    def __str__(self):
        return f"{{suit:{self.suit},number:{self.number}}}"

    # def dumps(self) -> str:
    #     return json.dumps(self)
    #
    # @staticmethod
    # def loads(s: str):
    #     d = jsonpickle.decode(s)
    #     return Card(d['number'], d.get('suit'))