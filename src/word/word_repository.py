from abc import ABC, abstractmethod


class WordRepository(ABC):

    @property
    @abstractmethod
    def categories(self):
        pass

    @abstractmethod
    def get_number_of_words(self, category: str) -> int:
        pass

    @abstractmethod
    def refill_words(self, amount: int) -> None:
        pass

    @abstractmethod
    def take_word(self, category: str) -> str:
        pass
