from src.word import WordRepository, GPTWordRepository
from src.word.adapters.gpt_word_repository import MockGPTWordRepository
import logging

logging.basicConfig(level=logging.INFO)

ages = [18, 19, 24, 22]
interests = ["Computer Science", "Movies", "Music", "The Simpsons"]
backgrounds = ["I am a student", "I am a teacher", "I am a software engineer"]

word_repository: WordRepository = MockGPTWordRepository(ages, interests, backgrounds)


for i in range(10):
    word = word_repository.take_word("Object")
    print(word)
    