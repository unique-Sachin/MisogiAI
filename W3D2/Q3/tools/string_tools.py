def count_vowels(word: str) -> int:
    return sum(1 for char in word.lower() if char in 'aeiou')

def count_letters(word: str) -> int:
    return len([c for c in word if c.isalpha()])