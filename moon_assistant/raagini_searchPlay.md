# Music Search and Playback Implementation

This document provides an overview of the code responsible for searching and playing music in Raagini.

## 1. Searching Music

The search functionality is primarily implemented in `lib/services/common_services.dart`. It uses the `youtube_explode_dart` package to interact with YouTube.

### Key Search Functions

#### `fetchSongsList(String searchQuery)`
This function takes a search query and returns a list of songs (as maps) derived from YouTube search results.

```dart
Future<List> fetchSongsList(String searchQuery) async {
  try {
    // Perform search using youtube_explode_dart
    final List<Video> searchResults = await ytClient.search.search(searchQuery);
    
    // Map YouTube Video objects to the app's internal song layout
    final songsList = searchResults
        .map((video) => returnSongLayout(0, video))
        .toList();

    return songsList;
  } catch (e, stackTrace) {
    logger.log('Error in fetchSongsList', error: e, stackTrace: stackTrace);
    return [];
  }
}
```

#### `getSearchSuggestions(String query)`
Fetches search suggestions as the user types.

```dart
Future<List<String>> getSearchSuggestions(String query) async {
  // Uses built-in YouTube search query suggestions
  final suggestions = await ytClient.search.getQuerySuggestions(query);
  return suggestions;
}
```

---

## 2. Playing Music

Playback is handled by the `RaaginiAudioHandler` in `lib/services/audio_service.dart`, which leverages the `just_audio` package.

### Core Playback Components

- **`RaaginiAudioHandler`**: Extends `BaseAudioHandler` to manage audio playback state, queue, and background services.
- **`just_audio.AudioPlayer`**: The underlying engine used for playing audio streams or files.

### Key Playback Logic

#### Playing a Song from the Queue
The `_playFromQueue` method coordinates loading a song and updating the UI state.

```dart
Future<void> _playFromQueue(int index) async {
  // ... (queue management and state updates)
  
  // Call the core playSong method
  final success = await playSong(_queueList[index], mediaId: uniqueId);
  
  if (success) {
    _consecutiveErrors = 0;
    _preloadUpcomingSongs(); // Start preloading next songs for gapless playback
  }
}
```

#### The `playSong` Method
This is the main entry point for starting a song. It handles both offline files and online streams.

```dart
Future<bool> playSong(Map song, {String? mediaId}) async {
  // ... (offline check)
  
  // Get the stream URL (either local path or remote YouTube URL)
  var songUrl = await _getSongUrl(song, isOffline);
  
  if (songUrl == null || songUrl.isEmpty) return false;

  // Build the AudioSource (handles URI, files, and SponsorBlock)
  final audioSource = await buildAudioSource(song, songUrl, isOffline);
  
  // Set the source and start playback
  final result = await _setAudioSourceAndPlay(song, audioSource, songUrl, isOffline);
  return result;
}
```

#### Fetching the Stream URL (`common_services.dart`)
When playing online, the app fetches the actual audio stream URL from YouTube.

```dart
Future<String?> fetchSongStreamUrl(String songId, bool isLive) async {
  // ... (cache check)
  
  // Extract audio streams from the YouTube manifest
  final manifest = await _fetchStreamManifest(songId);
  final audioStreams = manifest?.audioOnly;
  
  // Select the appropriate stream based on quality settings
  final selectedStream = selectAudioOnlyStreamForQuality(audioStreams.sortByBitrate());
  final url = selectedStream.url.toString();

  return url;
}
```

## Summary of Technologies
- **`just_audio`**: For robust audio playback control.
- **`youtube_explode_dart`**: For searching and extracting high-quality audio streams from YouTube.
- **`audio_service`**: To ensure music continues playing when the app is in the background.
