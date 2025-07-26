from collections import Counter
import re

class TextAnalyzer:
    def __init__(self, text):
        """
        Initialize with text to analyze.
        Args:
            text (str): Text to analyze
        """
        self.original_text = text
        self.text = text.lower()  # For case-insensitive analysis

    def get_character_frequency(self, include_spaces=False):
        """
        Get frequency of each character
        Args:
            include_spaces (bool): Whether to include spaces in count
        Returns:
            Counter: Character frequencies
        """
        filtered = self.text if include_spaces else self.text.replace(' ', '')
        return Counter(filtered)

    def get_word_frequency(self, min_length=1):
        """
        Get frequency of each word (minimum length filter)
        Args:
            min_length (int): Minimum word length to include
        Returns:
            Counter: Word frequencies
        """
        words = re.findall(r'\b\w+\b', self.text)
        filtered_words = [word for word in words if len(word) >= min_length]
        return Counter(filtered_words)

    def get_sentence_length_distribution(self):
        """
        Analyze sentence lengths (in words)
        Returns:
            dict: Contains 'lengths' (Counter), 'average', 'longest', 'shortest'
        """
        sentences = re.split(r'[.!?]+', self.original_text.strip())
        lengths = [len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences if sentence.strip()]
        if not lengths:
            return {'lengths': Counter(), 'average': 0, 'longest': 0, 'shortest': 0}
        return {
            'lengths': Counter(lengths),
            'average': sum(lengths) / len(lengths),
            'longest': max(lengths),
            'shortest': min(lengths)
        }

    def find_common_words(self, n=10, exclude_common=True):
        """
        Find most common words, optionally excluding very common English words
        Args:
            n (int): Number of words to return
            exclude_common (bool): Exclude common words like 'the', 'and', etc.
        Returns:
            list: List of tuples (word, count)
        """
        common_words_set = {
            'the', 'and', 'is', 'a', 'of', 'to', 'in', 'it', 'for', 'on', 'with',
            'as', 'that', 'this', 'an', 'by', 'be', 'are', 'at', 'or', 'from',
            'has', 'was', 'but', 'not', 'have', 'which'
        }
        freq = self.get_word_frequency(min_length=1)
        if exclude_common:
            for word in common_words_set:
                freq.pop(word, None)
        return freq.most_common(n)

    def get_reading_statistics(self):
        """
        Get comprehensive reading statistics
        Returns:
            dict: Contains character_count, word_count, sentence_count,
                  average_word_length, reading_time_minutes (assume 200 WPM)
        """
        words = re.findall(r'\b\w+\b', self.original_text)
        sentences = re.split(r'[.!?]+', self.original_text.strip())
        char_count = len(self.original_text)
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        reading_time_minutes = word_count / 200  # Assuming 200 WPM
        return {
            'character_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'average_word_length': avg_word_length,
            'reading_time_minutes': round(reading_time_minutes, 2)
        }

    def compare_with_text(self, other_text):
        """
        Compare this text with another text
        Args:
            other_text (str): Text to compare with
        Returns:
            dict: Contains 'common_words', 'similarity_score',
                  'unique_to_first', 'unique_to_second'
        """
        first_words = set(re.findall(r'\b\w+\b', self.text))
        second_words = set(re.findall(r'\b\w+\b', other_text.lower()))

        common = first_words & second_words
        unique_to_first = first_words - second_words
        unique_to_second = second_words - first_words

        similarity_score = len(common) / max(len(first_words | second_words), 1)

        return {
            'common_words': list(common),
            'similarity_score': round(similarity_score * 100, 2),  # percentage
            'unique_to_first': list(unique_to_first),
            'unique_to_second': list(unique_to_second)
        }


# Test your implementation
sample_text = """
Python is a high-level, interpreted programming language with dynamic semantics. 
Its high-level built-in data structures, combined with dynamic typing and dynamic binding, 
make it very attractive for Rapid Application Development. Python is simple, easy to learn syntax 
emphasizes readability and therefore reduces the cost of program maintenance. 
Python supports modules and packages, which encourages program modularity and code reuse. 
The Python interpreter and the extensive standard library are available in source or binary form 
without charge for all major platforms, and can be freely distributed.
"""

analyzer = TextAnalyzer(sample_text)

# Test outputs
print("Character frequency (top 5):", analyzer.get_character_frequency()[:5])
print("Word frequency (top 5):", analyzer.get_word_frequency()[:5])
print("Common words:", analyzer.find_common_words(5))
print("Sentence length distribution:", analyzer.get_sentence_length_distribution())
print("Reading statistics:", analyzer.get_reading_statistics())

# Compare with another text
other_text = "Java is a programming language. Java is object-oriented and platform independent."
comparison = analyzer.compare_with_text(other_text)
print("Comparison results:", comparison)