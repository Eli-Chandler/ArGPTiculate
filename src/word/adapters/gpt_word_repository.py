from src.word.word_repository import WordRepository
from typing import List

from openai import OpenAI
import os
import json
import logging


class GPTWordRepository(WordRepository):
    def __init__(self, ages: List[int], interests: List[str], backgrounds: List[str]):
        self._categories = (
            "Object",
            "Nature",
            "Random",
            "Person",
            "Action",
            "World"
        )

        self._words = {k: set() for k in self._categories}
        self._used_words = {k: set() for k in self._categories}
        self._client = OpenAI()

        self.ages = ages
        self.interests = interests
        self.backgrounds = backgrounds

    @property
    def categories(self):
        return self._categories

    def get_number_of_words(self, category: str) -> int:
        return len(self._words[category])

    def refill_words(self, amount: int) -> None:
        chat_completions = self._get_chat_completions(amount)

        for message in chat_completions:
            message = message.replace("\n", "").replace("\\n", "").replace('```json', '').replace('```', '').replace('\\', '').strip()
            message = message[message.index("--BEGIN JSON--") + len("--BEGIN JSON--"):message.index("--END JSON--")].strip()
            j = json.loads(message)
            for category in self._categories:
                for word in j["data"][category]:
                    if word not in self._used_words[category]:
                        self._words[category].add(word)

    def _get_chat_completions(self, amount: int) -> List[str]:
        age_ranges = ', '.join([str(num) for num in self.ages])
        interests = ', '.join(self.interests)
        backgrounds = ', '.join(self.backgrounds)

        logging.info(f"Refilling words with age ranges: {age_ranges}, interests: {interests}, backgrounds: {backgrounds}")

        chat_completion = self._client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Age range: {age_ranges}\nInterest: {interests}\nBackgrounds: {backgrounds}\nUsed words: {self._used_words}\nAmount: {amount} words for each category"
                 }
            ]
        )

        logging.info(f"Chat completion: {chat_completion}")

        return [choice.message.content for choice in chat_completion.choices if choice.message.role == "assistant"]

    def take_word(self, category: str) -> str:
        if not self._words[category]:
            logging.info(f"Out of words for category {category}, refilling")
            self.refill_words(10)

        word = self._words[category].pop()
        self._used_words[category].add(word)
        return word


prompt = """
**Objective**: Create customized "Articulate" game cards tailored to specific player groups.

**Background**: "Articulate" is a popular board game that challenges players to describe words without using the word itself. The game includes six categories: Object, Nature, Random, Person, Action, and World. To ensure an engaging and inclusive experience, it's essential to generate words that resonate with the players' demographics and interests.

**Step 1: Gather Input Information**
- **Age Range**: Understand the players' age to tailor word difficulty and cultural relevance.
- **Interests**: Identify key interests to select topics that resonate with the players.
- **Backgrounds**: Consider cultural or educational backgrounds to ensure inclusivity and accessibility.
- **Used words**: Keep track of the words that have been used to avoid repetition.
- **Amount**: The amount of words to generate for each category.

**Step 2: Decision-Making Process**
1. **Evaluate Relevance**: Determine how the age, interests, and backgrounds affect word choices. For younger audiences, lean towards current pop culture or trending topics; for older groups, consider historical or classic references.
2. **Identify Unique Elements**: Within the interests, pinpoint unique aspects to avoid generic words. For instance, if players are interested in "video games," select iconic items or actions specific to popular games.
3. **Balance Difficulty**: Ensure a mix of straightforward and challenging words across categories, considering the players' backgrounds to gauge what might be too obscure or too easy.

**Step 3: Generate Words**
- Based on the decision-making process, select words that are:
  - **Relevant**: Directly connect to the players' demographics and interests. You can also mix in some general knowledge based on the users age range to keep it interesting.
  - **Varied**: Offer a range of difficulties and topics.
  - **Accurate**: Fit the category's definition precisely.
- You should do this for each of the following categories: Object, Nature, Random, Person, Action, World.
- Generate the user provided amount of words for each category to provide a diverse pool of options for gameplay.

Here are some guidelines and rules for each category:

### 1. Object
- **Definition**: Tangible or significant conceptual items that can be described without referring to their name.
- **Criteria**:
  - Must be identifiable and distinct.
  - Can be physical (e.g., "Microscope") or abstract (e.g., "Blockchain").
  - Avoid overly broad or generic terms (e.g., "Technology").

### 2. Nature
- **Definition**: Elements related to the natural world, including flora, fauna, geological formations, and natural phenomena.
- **Criteria**:
  - Should be naturally occurring (e.g., "Coral Reef").
  - Can include broad categories (e.g., "Deciduous Forest") and specific instances (e.g., "Blue Whale").
  - Avoid man-made items unless they are directly related to observing or interacting with nature (e.g., "Telescope" for stargazing).

### 3. Random
- **Definition**: A broad category encompassing words that don't neatly fit into the other categories, offering a mix of cultural, historical, and whimsical terms.
- **Criteria**:
  - Encourages creativity and surprise elements (e.g., "Wigwam").
  - Can range from pop culture references to historical artifacts.
  - The diversity of terms should challenge players' descriptive abilities without being too obscure.

### 4. Person
- **Definition**: Notable individuals, fictional characters, or roles that can be described by their achievements, actions, or characteristics.
- **Criteria**:
  - Includes a wide range of recognizable figures (e.g., "Ada Lovelace").
  - Can be real or fictional, contemporary or historical.
  - Avoid overly obscure or niche figures unless the player group's interests specifically include them.

### 5. Action
- **Definition**: Verbs or verb phrases that denote physical or mental activities, following the format of being one word or hyphenated, and ending in "-ing".
- **Criteria**:
  - Must be expressible in a single word or a hyphenated form (e.g., "Programming", "Base-jumping").
  - The action should be widely understandable and performable (to an extent) or imaginable.
  - Avoid complex phrases or actions that are too specific to a niche interest (e.g., "Performing a triple axel").

### 6. World
- **Definition**: Terms related to geography, places, cultures, international cuisine, or global concepts.
- **Criteria**:
  - Can include countries, cities, landmarks, cultural practices, or global issues (e.g., "Sushi", "Amazon Rainforest").
  - Encourages exploration of global diversity and understanding.
  - Avoid overly detailed or specific locations known only to a particular niche unless it offers educational value to the player group.

### General Guidelines
- **Clarity**: Words should be clear and specific enough that players can describe and guess them within the time constraints of a game turn.
- **Relevance**: Words should reflect the interests and knowledge base of the players, aiming for a balance between challenge and accessibility.
- **Tediousness**: It's boring for the players if the words are tedious and in the format <Specific term from category> <Generic other unrelated thing, or unnescesarry word> for example "Bart Simpsons Doll", is not specific and just relies on the word "doll" to be interesting. Or for example "Duff Beer Can" could just be "Duff Beer" or "Duff" to make the game less tedious.
More example of this are like "Food marathon" Instead of "Mukbang", "Road trip to queenstown"
- **Spirit of the game**: You should look at articulate for examples of the output, these are the best guidelines as the official game is very popular with well-thought-out cards.

**Step 4: Compile Output**
- Format the chosen words into the specified JSON structure, ensuring clarity and accessibility for game play.

**Example Output Structure**:
```json
--BEGIN JSON--
{
    "success": true,
    "message": "Words generated based on player demographics and interests",
    "data": {
        "Object": ["word1", ..., "word10"],
        "Nature": ["word1", ..., "word10"],
        "Random": ["word1", ..., "word10"],
        "Person": ["word1", ..., "word10"],
        "Action": ["word1", ..., "word10"],
        "World": ["word1", ..., "word10"]
    }
}
--END JSON--
```

Be sure to include the --BEGIN JSON-- and --END JSON-- tags to encapsulate the JSON structure and assist with parsing.

This approach integrates an explicit decision-making phase to refine word selection, ensuring the generated game cards are thoughtfully tailored to the specific player group. It emphasizes the importance of relevance, variety, and accuracy in creating engaging and inclusive game content.
""".strip()

class MockGPTWordRepository(GPTWordRepository):
    def _get_chat_completions(self, amount: int) -> None:
        return [r"""**Step 1: Evaluate Relevance**\nGiven the age range and interests, words should be modern, pop-culture heavy, and consider science, technology, and media. Consider elements from The Simpsons and key figures in computer science given the players\' interests.\n\n**Step 2: Identify Unique Elements**\nFocus on unique characters, terms, or actions from The Simpsons, identify popular tech gadgets or software, and trace historical trends in computer science.\n\n**Step 3: Generate Words**\nBased on the above, the suggested words for each category are as follows:\n\n### Object\n1. Drone\n2. Smartphone\n3. Compiler\n4. Duff Beer\n5. Bart\'s Slingshot\n6. Vinyl Record\n7. Ethernet Cable\n8. Oscilloscope \n9. Bitcoin\n10. Donut\n\n### Nature\n1. Binary Tree\n2. Silicon Crystal\n3. Springfield Gorge\n4. Electric Storm\n5. Neon Glow \n6. Star Cluster\n7. Raspberry Pi\n8. Sound Wave\n9. Magnetic Field\n10. Internet Cloud\n\n### Random\n1. Typing Test\n2. Blinky (Three-Eyed fish)\n3. Vegan Leather\n4. Cobol Language\n5. Kwik-E-Mart\n6. Treehouse of Horror\n7. Malware\n8. Bitcoin Mining\n9. Gig Economy\n10. Hacker \n\n### Person\n1. Homer Simpson\n2. Ellen DeGeneres\n3. Linus Torvalds\n4. Ada Lovelace\n5. Elon Musk\n6. Krusty the Clown\n7. Steve Jobs\n8. Marge Simpson\n9. Bart Simpson\n10. Lisa Simpson\n\n### Action\n1. Debugging\n2. Binge-Watching\n3. Streaming\n4. Tweeting\n5. Coding\n6. Gaming\n7. Hacking\n8. Uploading\n9. Downloading\n10. Overclocking\n\n### World\n1. Silicon Valley\n2. Springfield\n3. Moaning Lisa Painting\n4. Evergreen Terrace\n5. Wi-Fi Network\n6. Hollywood\n7. Moe\'s Tavern\n8. Microverse\n9. iTunes Store\n10. Google Campus\n\nBelow is the output in JSON format:\n\n--BEGIN JSON--\n```json\n{\n    "success": true,\n    "message": "Words generated based on player demographics and interests",\n    "data": {\n        "Object": ["Drone", "Smartphone", "Compiler", "Duff Beer", "Bart\'s Slingshot", "Vinyl Record", "Ethernet Cable", "Oscilloscope", "Bitcoin", "Donut"],\n        "Nature": ["Binary Tree", "Silicon Crystal", "Springfield Gorge", "Electric Storm", "Neon Glow", "Star Cluster", "Raspberry Pi", "Sound Wave", "Magnetic Field", "Internet Cloud"],\n        "Random": ["Typing Test", "Blinky (Three-Eyed fish)", "Vegan Leather", "Cobol Language", "Kwik-E-Mart", "Treehouse of Horror", "Malware", "Bitcoin Mining", "Gig Economy", "Hacker"],\n        "Person": ["Homer Simpson", "Ellen DeGeneres", "Linus Torvalds", "Ada Lovelace", "Elon Musk", "Krusty the Clown", "Steve Jobs", "Marge Simpson", "Bart Simpson", "Lisa Simpson"],\n        "Action": ["Debugging", "Binge-Watching", "Streaming", "Tweeting", "Coding", "Gaming", "Hacking", "Uploading", "Downloading", "Overclocking"],\n        "World": ["Silicon Valley", "Springfield", "Moaning Lisa Painting", "Evergreen Terrace", "Wi-Fi Network", "Hollywood", "Moe\'s Tavern", "Microverse", "iTunes Store", "Google Campus"]\n    }\n}\n```\n--END JSON--'"""]