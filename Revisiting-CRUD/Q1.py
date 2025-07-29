from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
import random


# Abstract Base Classes
class MediaContent(ABC):
    """Abstract base class for all media types"""
    
    def __init__(self, title: str, category: str):
        self.title = title
        self.category = category
        self.ratings: List[float] = []
        self.is_premium = False
    
    @abstractmethod
    def play(self) -> str:
        """Play the media content"""
        pass
    
    @abstractmethod
    def get_duration(self) -> Union[int, float]:
        """Get duration in minutes"""
        pass
    
    @abstractmethod
    def get_file_size(self) -> Union[int, float]:
        """Get file size in MB"""
        pass
    
    @abstractmethod
    def calculate_streaming_cost(self) -> Union[int, float]:
        """Calculate streaming cost based on content type"""
        pass
    
    def add_rating(self, rating: float) -> None:
        """Add a rating to the content"""
        if 1.0 <= rating <= 5.0:
            self.ratings.append(rating)
    
    def get_average_rating(self) -> float:
        """Get average rating of the content"""
        if not self.ratings:
            return 0.0
        return sum(self.ratings) / len(self.ratings)
    
    def is_premium_content(self) -> bool:
        """Check if content is premium"""
        return self.is_premium


class StreamingDevice(ABC):
    """Abstract base class for different streaming devices"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> str:
        """Connect the device"""
        pass
    
    @abstractmethod
    def stream_content(self, content: MediaContent) -> Dict:
        """Stream content on the device"""
        pass
    
    @abstractmethod
    def adjust_quality(self, quality: str) -> str:
        """Adjust streaming quality"""
        pass
    
    def get_device_info(self) -> Dict:
        """Get device information"""
        return {
            "name": self.name,
            "connected": self.is_connected,
            "type": self.__class__.__name__
        }
    
    def check_compatibility(self, content: MediaContent) -> bool:
        """Check if device is compatible with content"""
        return True  # Default implementation


# Concrete Media Content Classes
class Movie(MediaContent):
    """Movie content class"""
    
    def __init__(self, title: str, category: str, duration: int, resolution: str, director: str):
        super().__init__(title, category)
        self.duration_minutes = duration
        self.resolution = resolution
        self.director = director
        self.genre = category
    
    def play(self) -> str:
        return f"Now playing movie: {self.title} directed by {self.director}"
    
    def get_duration(self) -> int:
        return self.duration_minutes
    
    def get_file_size(self) -> float:
        # File size calculation based on duration and resolution
        base_size = self.duration_minutes * 50  # Base MB per minute
        if self.resolution == "4K":
            return base_size * 4
        elif self.resolution == "HD":
            return base_size * 2
        return base_size
    
    def calculate_streaming_cost(self) -> float:
        base_cost = 0.05 * self.duration_minutes
        if self.is_premium:
            base_cost *= 1.5
        if self.resolution == "4K":
            base_cost *= 1.3
        return base_cost


class TVShow(MediaContent):
    """TV Show content class"""
    
    def __init__(self, title: str, category: str, seasons: int, total_episodes: int, current_episode: int):
        super().__init__(title, category)
        self.seasons = seasons
        self.total_episodes = total_episodes
        self.current_episode = current_episode
        self.episode_duration = 45  # Average episode duration
    
    def play(self) -> str:
        return f"Now playing TV Show: {self.title}, Episode {self.current_episode}"
    
    def get_duration(self) -> int:
        return self.episode_duration
    
    def get_file_size(self) -> float:
        return self.episode_duration * 40  # MB per minute for TV shows
    
    def calculate_streaming_cost(self) -> float:
        base_cost = 0.03 * self.episode_duration
        if self.is_premium:
            base_cost *= 1.5
        return base_cost


class Podcast(MediaContent):
    """Podcast content class"""
    
    def __init__(self, title: str, category: str, duration: int, episode_number: int, transcript_available: bool):
        super().__init__(title, category)
        self.duration_minutes = duration
        self.episode_number = episode_number
        self.transcript_available = transcript_available
    
    def play(self) -> str:
        return f"Now playing podcast: {self.title}, Episode {self.episode_number}"
    
    def get_duration(self) -> int:
        return self.duration_minutes
    
    def get_file_size(self) -> float:
        return self.duration_minutes * 1.5  # Audio files are smaller
    
    def calculate_streaming_cost(self) -> float:
        return 0.01 * self.duration_minutes  # Podcasts are cheaper to stream


class Music(MediaContent):
    """Music content class"""
    
    def __init__(self, title: str, category: str, duration: int, artist: str, album: str, lyrics_available: bool):
        super().__init__(title, category)
        self.duration_seconds = duration
        self.artist = artist
        self.album = album
        self.lyrics_available = lyrics_available
    
    def play(self) -> str:
        return f"Now playing music: {self.title} by {self.artist}"
    
    def get_duration(self) -> float:
        return self.duration_seconds / 60  # Convert to minutes
    
    def get_file_size(self) -> float:
        return (self.duration_seconds / 60) * 5  # MB per minute for music
    
    def calculate_streaming_cost(self) -> float:
        return 0.005 * (self.duration_seconds / 60)  # Very low cost for music


# Concrete Device Classes
class SmartTV(StreamingDevice):
    """Smart TV streaming device"""
    
    def __init__(self, name: str, screen_size: str, supports_4k: bool):
        super().__init__(name)
        self.screen_size = screen_size
        self.supports_4k = supports_4k
        self.surround_sound = True
    
    def connect(self) -> str:
        self.is_connected = True
        return f"Smart TV {self.name} connected successfully"
    
    def stream_content(self, content: MediaContent) -> Dict:
        quality = "4K" if self.supports_4k and hasattr(content, 'resolution') else "HD"
        return {
            "quality": quality,
            "status": "success",
            "device": "SmartTV",
            "audio": "surround"
        }
    
    def adjust_quality(self, quality: str) -> str:
        return f"Quality adjusted to {quality} on Smart TV"


class Laptop(StreamingDevice):
    """Laptop streaming device"""
    
    def __init__(self, name: str, screen_size: str, processor: str):
        super().__init__(name)
        self.screen_size = screen_size
        self.processor = processor
        self.headphone_support = True
    
    def connect(self) -> str:
        self.is_connected = True
        return f"Laptop {self.name} connected successfully"
    
    def stream_content(self, content: MediaContent) -> Dict:
        return {
            "quality": "HD",
            "status": "success",
            "device": "Laptop",
            "audio": "headphones"
        }
    
    def adjust_quality(self, quality: str) -> str:
        return f"Quality adjusted to {quality} on Laptop"


class Mobile(StreamingDevice):
    """Mobile streaming device"""
    
    def __init__(self, name: str, os: str, battery_level: int):
        super().__init__(name)
        self.os = os
        self.battery_level = battery_level
        self.battery_optimization = True
    
    def connect(self) -> str:
        self.is_connected = True
        return f"Mobile {self.name} connected successfully"
    
    def stream_content(self, content: MediaContent) -> Dict:
        quality = "SD" if self.battery_level < 30 else "HD"
        return {
            "quality": quality,
            "status": "success",
            "device": "Mobile",
            "audio": "mobile_speakers"
        }
    
    def adjust_quality(self, quality: str) -> str:
        return f"Quality adjusted to {quality} on Mobile"


class SmartSpeaker(StreamingDevice):
    """Smart Speaker streaming device (audio only)"""
    
    def __init__(self, name: str, voice_assistant: str, voice_control: bool):
        super().__init__(name)
        self.voice_assistant = voice_assistant
        self.voice_control = voice_control
        self.audio_only = True
    
    def connect(self) -> str:
        self.is_connected = True
        return f"Smart Speaker {self.name} connected successfully"
    
    def stream_content(self, content: MediaContent) -> Dict:
        # Smart speakers can only play audio content
        if isinstance(content, (Podcast, Music)):
            return {
                "quality": "High",
                "status": "success",
                "device": "SmartSpeaker",
                "audio": "speakers"
            }
        else:
            return {
                "quality": "N/A",
                "status": "error",
                "device": "SmartSpeaker",
                "message": "This device supports audio only content"
            }
    
    def adjust_quality(self, quality: str) -> str:
        return f"Audio quality adjusted to {quality} on Smart Speaker"


# Additional Classes
class User:
    """User class for managing subscriptions and preferences"""
    
    def __init__(self, username: str, subscription_tier: str, preferences: List[str]):
        self.username = username
        self.subscription_tier = subscription_tier  # Free, Premium, Family
        self.preferences = preferences
        self.watch_history: List[MediaContent] = []
        self.watch_time = 0
    
    def add_to_history(self, content: MediaContent) -> None:
        """Add content to watch history"""
        self.watch_history.append(content)
        self.watch_time += content.get_duration()
    
    def get_favorite_genres(self) -> List[str]:
        """Get user's favorite genres based on watch history"""
        genre_count = {}
        for content in self.watch_history:
            genre = content.category
            genre_count[genre] = genre_count.get(genre, 0) + 1
        
        if not genre_count:
            return self.preferences
        
        # Return top 3 genres
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, _ in sorted_genres[:3]]


class StreamingPlatform:
    """Main streaming platform class that orchestrates everything"""
    
    def __init__(self, name: str):
        self.name = name
        self.content_library: List[MediaContent] = []
        self.users: List[User] = []
        self.user_devices: Dict[str, List[StreamingDevice]] = {}
    
    def add_content(self, content: MediaContent) -> None:
        """Add content to the platform"""
        self.content_library.append(content)
    
    def register_user(self, user: User) -> None:
        """Register a new user"""
        self.users.append(user)
        self.user_devices[user.username] = []
    
    def register_device(self, device: StreamingDevice, user: User) -> None:
        """Register a device for a user"""
        if user.username in self.user_devices:
            self.user_devices[user.username].append(device)
    
    def get_recommendations(self, user: User) -> List[MediaContent]:
        """Get content recommendations based on user preferences"""
        recommendations = []
        user_genres = user.preferences + user.get_favorite_genres()
        
        for content in self.content_library:
            # Skip premium content for free users
            if content.is_premium and user.subscription_tier == "Free":
                continue
            
            # Recommend based on genre preferences
            if content.category in user_genres:
                recommendations.append(content)
            
            # Recommend highly rated content
            elif content.get_average_rating() > 4.0:
                recommendations.append(content)
        
        # Remove duplicates and shuffle
        recommendations = list(set(recommendations))
        random.shuffle(recommendations)
        return recommendations[:10]  # Return top 10 recommendations
    
    def start_watching(self, user: User, content: MediaContent, device: StreamingDevice) -> Dict:
        """Start a watch session"""
        # Check subscription restrictions
        if content.is_premium and user.subscription_tier == "Free":
            return {
                "status": "error",
                "message": "Premium subscription required for this content"
            }
        
        # Check device compatibility
        if not device.check_compatibility(content):
            return {
                "status": "error",
                "message": "Device not compatible with this content"
            }
        
        # Start streaming
        stream_result = device.stream_content(content)
        if stream_result["status"] == "success":
            user.add_to_history(content)
            return {
                "status": "started",
                "content": content.title,
                "device": device.name,
                "quality": stream_result["quality"]
            }
        
        return stream_result
    
    def get_user_analytics(self, user: User) -> Dict:
        """Get user analytics and viewing statistics"""
        return {
            "total_watch_time": user.watch_time,
            "content_watched": len(user.watch_history),
            "favorite_genres": user.get_favorite_genres(),
            "subscription_tier": user.subscription_tier,
            "average_session_length": user.watch_time / max(len(user.watch_history), 1)
        }


# Test Cases Implementation
if __name__ == "__main__":
    # Test Case 1: Abstract class instantiation should fail
    try:
        content = MediaContent("Test", "Test Category")
        assert False, "Should not be able to instantiate abstract class"
    except TypeError:
        pass

    try:
        device = StreamingDevice("Test Device")
        assert False, "Should not be able to instantiate abstract class"
    except TypeError:
        pass

    # Test Case 2: Polymorphic content creation and playback
    movie = Movie("Inception", "Sci-Fi", 148, "4K", "Christopher Nolan")
    tv_show = TVShow("Breaking Bad", "Drama", 5, 62, 1)
    podcast = Podcast("Tech Talk", "Technology", 45, 15, True)
    music = Music("Bohemian Rhapsody", "Rock", 355, "Queen", "A Night at the Opera", True)

    contents = [movie, tv_show, podcast, music]

    # All should implement required abstract methods
    for content in contents:
        play_result = content.play()
        assert isinstance(play_result, str)
        assert "playing" in play_result.lower()

        duration = content.get_duration()
        assert isinstance(duration, (int, float))
        assert duration > 0

        file_size = content.get_file_size()
        assert isinstance(file_size, (int, float))

        cost = content.calculate_streaming_cost()
        assert isinstance(cost, (int, float))
        assert cost >= 0

    # Test Case 3: Device-specific streaming behavior
    smart_tv = SmartTV("Samsung 4K TV", "55 inch", True)
    laptop = Laptop("MacBook Pro", "13 inch", "Intel i7")
    mobile = Mobile("iPhone 13", "iOS", 85)
    speaker = SmartSpeaker("Amazon Echo", "Alexa", True)

    devices = [smart_tv, laptop, mobile, speaker]

    for device in devices:
        connect_result = device.connect()
        assert "connected" in connect_result.lower()

        # Test polymorphic streaming
        stream_result = device.stream_content(movie)
        assert isinstance(stream_result, dict)
        assert "quality" in stream_result
        assert "status" in stream_result

    # Test Case 4: Device-content compatibility
    # Smart speaker should only play audio content
    audio_content = [podcast, music]
    video_content = [movie, tv_show]

    for content in audio_content:
        result = speaker.stream_content(content)
        assert result["status"] == "success"

    for content in video_content:
        result = speaker.stream_content(content)
        assert result["status"] == "error" or "audio only" in result.get("message", "")

    # Test Case 5: User subscription and platform integration
    user = User("john_doe", "Premium", ["Sci-Fi", "Drama"])
    platform = StreamingPlatform("NetStream")

    # Add content to platform
    for content in contents:
        platform.add_content(content)

    # Register user and device
    platform.register_user(user)
    platform.register_device(smart_tv, user)

    # Test recommendation system
    recommendations = platform.get_recommendations(user)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    # Test watch history and analytics
    watch_session = platform.start_watching(user, movie, smart_tv)
    assert watch_session["status"] == "started"

    analytics = platform.get_user_analytics(user)
    assert "total_watch_time" in analytics
    assert "favorite_genres" in analytics

    # Test Case 6: Subscription tier restrictions
    free_user = User("jane_doe", "Free", ["Comedy"])
    platform.register_user(free_user)

    # Premium content should be restricted for free users
    premium_movie = Movie("Premium Film", "Action", 120, "4K", "Director")
    premium_movie.is_premium = True
    platform.add_content(premium_movie)

    watch_attempt = platform.start_watching(free_user, premium_movie, laptop)
    assert watch_attempt["status"] == "error"
    assert "subscription" in watch_attempt["message"].lower()

    # Test Case 7: Content rating and recommendation impact
    movie.add_rating(4.5)
    movie.add_rating(4.8)
    movie.add_rating(4.2)

    assert abs(movie.get_average_rating() - 4.5) < 0.1

    # Highly rated content should appear in recommendations
    new_recommendations = platform.get_recommendations(user)
    highly_rated = [content for content in new_recommendations if content.get_average_rating() > 4.0]
    assert len(highly_rated) > 0

    print("All test cases passed successfully!")
    print(f"Platform: {platform.name}")
    print(f"Total content in library: {len(platform.content_library)}")
    print(f"Registered users: {len(platform.users)}")