from abc import ABC

class JUEGO(ABC):
    def __init__(self, date, user, fatiga_serie=-1):
        self.date = date
        self.user = user
        self.fatiga_serie = fatiga_serie


