import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios';

const BASE_BACKEND_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [imdbId, setImdbId] = useState('');
  const [newImdbId, setNewImdbId] = useState('');
  const [contentMetadata, setContentMetadata] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(1);
  const [selectedEpisode, setSelectedEpisode] = useState(1);
  const [torrentsData, setTorrentsData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState(null);
  const [watchedContent, setWatchedContent] = useState([]);
  const [indexedContent, setIndexedContent] = useState([]);
  const [selectedContent, setSelectedContent] = useState(null);
  const [showWatchedList, setShowWatchedList] = useState(false);
  const [showContentDetail, setShowContentDetail] = useState(false);

  // Load data from chrome storage on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        if (typeof chrome !== 'undefined' && chrome.storage) {
          const result = await chrome.storage.local.get(['imdbId', '404stream_watched', '404stream_indexed']);
          if (result.imdbId) {
            setImdbId(result.imdbId);
            // Auto-load content metadata when IMDB ID is loaded
            await loadContentMetadata(result.imdbId);
          }
          if (result['404stream_watched']) {
            setWatchedContent(result['404stream_watched']);
          }
          if (result['404stream_indexed']) {
            setIndexedContent(result['404stream_indexed']);
          }
        } else {
          // Fallback to localStorage for development
          const saved = localStorage.getItem('imdbId');
          if (saved) {
            setImdbId(saved);
            await loadContentMetadata(saved);
          }
        }
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    loadData();
  }, []);

  const loadContentMetadata = async (id) => {
    if (!id) return;

    setIsScraping(true);
    try {
      // First check Chrome storage directly for watched content
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await chrome.storage.local.get(['404stream_watched', '404stream_indexed']);
        const watched = result['404stream_watched'] || [];
        const indexed = result['404stream_indexed'] || [];

        // Check if already in watched
        const watchedItem = watched.find(item => item.imdb_id === id);
        if (watchedItem) {
          setContentMetadata(watchedItem);
          setIsScraping(false);
          return;
        }

        // Then check if already indexed
        const indexedItem = indexed.find(item => item.imdb_id === id);
        if (indexedItem) {
          setContentMetadata(indexedItem);
          setIsScraping(false);
          return;
        }
      } else {
        // Fallback: check state arrays for development
        const watchedItem = watchedContent.find(item => item.imdb_id === id);
        if (watchedItem) {
          setContentMetadata(watchedItem);
          setIsScraping(false);
          return;
        }

        const indexedItem = indexedContent.find(item => item.imdb_id === id);
        if (indexedItem) {
          setContentMetadata(indexedItem);
          setIsScraping(false);
          return;
        }
      }

      // If not found, scrape from API
      const response = await axios.get(`${BASE_BACKEND_URL}/scrape/${id}`);
      if (response.status === 200) {
        const metadata = {
          ...response.data,
          imdb_id: id
        };
        setContentMetadata(metadata);

        // Store in indexed collection
        await saveToIndexed(metadata);
      }
    } catch (error) {
      console.error('Error loading content metadata:', error);
      setContentMetadata(null);
    } finally {
      setIsScraping(false);
    }
  };

  const saveToIndexed = async (metadata) => {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await chrome.storage.local.get(['404stream_indexed']);
        const indexed = result['404stream_indexed'] || [];

        // Check if already exists
        const existingIndex = indexed.findIndex(item => item.imdb_id === metadata.imdb_id);
        if (existingIndex === -1) {
          indexed.push(metadata);
          await chrome.storage.local.set({ '404stream_indexed': indexed });
          setIndexedContent(indexed);
        }
      }
    } catch (error) {
      console.error('Error saving to indexed:', error);
    }
  };

  const saveToWatched = async (metadata, torrentInfo) => {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await chrome.storage.local.get(['404stream_watched']);
        const watched = result['404stream_watched'] || [];

        // Find existing or create new
        let existingIndex = watched.findIndex(item => item.imdb_id === metadata.imdb_id);

        if (existingIndex !== -1) {
          // Update existing - clear last_watched from others and add new torrent
          watched.forEach(item => item.last_watched = false);
          watched[existingIndex].last_watched = true;

          // Check if this specific episode/movie already watched
          const alreadyWatched = watched[existingIndex].torrents?.some(t =>
            metadata.is_movie ? true : (t.season === torrentInfo.season && t.episode === torrentInfo.episode)
          );

          if (!alreadyWatched) {
            watched[existingIndex].torrents = [...(watched[existingIndex].torrents || []), torrentInfo];
          }
        } else {
          // Create new entry
          watched.forEach(item => item.last_watched = false);
          watched.push({
            ...metadata,
            torrents: [torrentInfo],
            last_watched: true
          });
        }

        await chrome.storage.local.set({ '404stream_watched': watched });
        setWatchedContent(watched);
      }
    } catch (error) {
      console.error('Error saving to watched:', error);
    }
  };

  const handleContentClick = async (content) => {
    setSelectedContent(content);
    setShowWatchedList(true);

    // Update the states to match the clicked content
    setImdbId(content.imdb_id);
    setContentMetadata(content);

    // Save the new IMDB ID to Chrome storage
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        await chrome.storage.local.set({ imdbId: content.imdb_id });
      } else {
        // Fallback to localStorage for development
        localStorage.setItem('imdbId', content.imdb_id);
      }
    } catch (error) {
      console.error('Error saving IMDB ID to storage:', error);
    }

    // If it's a TV show, set season and episode to the last watched episode
    if (!content.is_movie && content.torrents && content.torrents.length > 0) {
      // Get the most recent torrent (last in array)
      const lastTorrent = content.torrents[content.torrents.length - 1];
      setSelectedSeason(lastTorrent.season || 1);
      setSelectedEpisode(lastTorrent.episode || 1);
    }
  };

  const handleBackToWatched = () => {
    setSelectedContent(null);
    setShowWatchedList(false);
  };

  const handleShowContentDetail = () => {
    if (contentMetadata) {
      setShowContentDetail(true);
    }
  };

  const handleBackToMain = () => {
    setShowContentDetail(false);
  };

  const handleEpisodeSelect = (season, episode) => {
    setSelectedSeason(season);
    setSelectedEpisode(episode);
    getTorrents(contentMetadata.is_movie, imdbId, season, episode, setTorrentsData, setIsLoading);
  };

  const playContent = async (content, season = null, episode = null) => {
    // Find the best torrent for this content
    const bestTorrent = content.torrents?.find(t =>
      season ? (t.season === season && t.episode === episode) : true
    ) || content.torrents?.[0];

    if (bestTorrent) {
      await streamWithSave(
        bestTorrent,
        content.is_movie,
        season || bestTorrent.season || 1,
        episode || bestTorrent.episode || 1,
        content.imdb_id
      );
    }
  };

  const handleImdbIdChange = async () => {
    if (newImdbId.trim()) {
      const cleanId = newImdbId.trim();
      setImdbId(cleanId);
      setTorrentsData([]);
      setShowContentDetail(false);

      try {
        if (typeof chrome !== 'undefined' && chrome.storage) {
          await chrome.storage.local.set({ imdbId: cleanId });

          // Also update the Chrome storage with current IMDB ID for sync
          const result = await chrome.storage.local.get(['404stream_watched']);
          if (result['404stream_watched']) {
            setWatchedContent(result['404stream_watched']);
          }
        } else {
          // Fallback to localStorage for development
          localStorage.setItem('imdbId', cleanId);
        }

        // Auto-load content metadata
        await loadContentMetadata(cleanId);
      } catch (error) {
        console.error('Error saving IMDB ID:', error);
      }

      setNewImdbId('');
    }
  };

  const handleAutoSelect = () => {
    if (torrentsData.length > 0) {
      streamWithSave(torrentsData[0], contentMetadata.is_movie, selectedSeason, selectedEpisode, imdbId);
    }
  };

  const handleNextEpisode = async () => {
    if (!contentMetadata.is_movie && contentMetadata.episodes) {
      // Find current season episodes
      const currentSeasonData = contentMetadata.episodes.find(s => s.season === selectedSeason);
      if (currentSeasonData) {
        const nextEpisode = selectedEpisode + 1;
        if (nextEpisode <= currentSeasonData.episodes.length) {
          setSelectedEpisode(nextEpisode);
          await getTorrents(false, imdbId, selectedSeason, nextEpisode, setTorrentsData, setIsLoading);
        }
      }
    }
  };

  // Streaming function with saveWatchedContent integration
  const streamWithSave = async (torrent, is_movie, season, episode, imdbId) => {
    await stream(torrent, is_movie, season, episode, imdbId, setIsStreaming, setStreamingContent);

    // Reload watched content after streaming to update the UI
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await chrome.storage.local.get(['404stream_watched']);
        if (result['404stream_watched']) {
          setWatchedContent(result['404stream_watched']);
        }
      }
    } catch (error) {
      console.error('Error reloading watched content:', error);
    }
  };

  const refetchImdbId = async () => {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await chrome.storage.local.get(['imdbId']);
        if (result['imdbId']) {
          setImdbId(result['imdbId']);
        }
      } else {
        const storedId = localStorage.getItem('imdbId');
        if (storedId) {
          setImdbId(storedId);
        }
      }
    } catch (error) {
      console.error('Error refetching IMDB ID:', error);
    }
  }

  const handleRedirectToImdb = async () => {
    const url = `https://www.imdb.com/`;
    window.open(url, '_blank');
    chrome.runtime.sendMessage({ action: "close_popup" });
  };

  return (
    <div className="w-[100%] h-[100%] bg-gradient-to-br from-slate-900 to-slate-800 p-4 overflow-hidden">
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="text-center mb-4">
          <h1 className="text-2xl font-bold text-white mb-1">404Stream</h1>
          <p className="text-slate-300 text-sm">Stream your favorite content</p>
        </div>

        {/* GitHub Star Section */}
        <div className="text-center mb-4">
          <a
            href="https://github.com/Saadiq8149/404Stream"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 border border-gray-600"
          >
            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
            </svg>
            ⭐ Star on GitHub
          </a>
        </div>

        <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
          {/* Left Column - Controls */}
          <div className="bg-white rounded-lg shadow-xl p-4 flex flex-col">
            {/* IMDB ID Display */}
            <button
              onClick={handleRedirectToImdb}
              className="px-2 py-1 bg-yellow-500 text-black text-md rounded hover:bg-blue-600 transition-colors flex-shrink-0 text-bold mb-4"
            >
              Search Titles in IMDB
            </button>

            <div className="mb-4">

              <div className="mt-1 bg-gray-50 rounded p-2 font-mono text-xs text-gray-800 display flex justify-between items-center">
                <p>Current: {imdbId}</p>
                <button
                  onClick={refetchImdbId}
                  className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors flex-shrink-0"
                >
                  Refetch
                </button>
              </div>

            </div>

            {/* Content Metadata Display */}
            {isScraping && (
              <div className="mb-4 p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-16 bg-gray-300 rounded flex items-center justify-center flex-shrink-0 animate-pulse">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
                      <h3 className="font-semibold text-gray-600 text-sm">
                        Loading content details...
                      </h3>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Fetching metadata from IMDB
                    </p>
                  </div>
                </div>
              </div>
            )}

            {contentMetadata && !isScraping && (
              <div className="mb-4 p-3 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-16 bg-gray-300 rounded flex items-center justify-center flex-shrink-0">
                    {contentMetadata.poster && contentMetadata.poster !== 'placeholder' ? (
                      <img src={contentMetadata.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                    ) : (
                      <span className="text-lg">{contentMetadata.is_movie ? '🎬' : '📺'}</span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 text-sm truncate">
                      {contentMetadata.title || contentMetadata.imdb_id}
                    </h3>
                    <p className="text-xs text-gray-600">
                      {contentMetadata.is_movie ? 'Movie' : `TV Show • ${contentMetadata.seasons || 0} seasons`}
                    </p>
                    <div className="flex gap-1 mt-1">
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-blue-100 text-blue-800">
                        {contentMetadata.is_movie ? 'Movie' : 'Series'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={handleShowContentDetail}
                    className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors flex-shrink-0"
                  >
                    📋 Details
                  </button>
                </div>
              </div>
            )}

            {/* Episode Selection for TV Shows */}
            {contentMetadata && !contentMetadata.is_movie && contentMetadata.episodes && (
              <div className="mb-4">
                <label className="block text-xs font-medium text-gray-700 mb-2">
                  Select Episode
                </label>

                {/* Season Selector */}
                <div className="mb-2">
                  <label className="block text-xs text-gray-500 mb-1">Season</label>
                  <select
                    value={selectedSeason}
                    onChange={(e) => {
                      setSelectedSeason(parseInt(e.target.value));
                      setSelectedEpisode(1);
                    }}
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    {contentMetadata.episodes.map((seasonData, index) => (
                      <option key={index} value={seasonData.season}>
                        Season {seasonData.season}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Episode Grid */}
                <div className="mb-2">
                  <label className="block text-xs text-gray-500 mb-1">Episode</label>
                  <div className="max-h-32 overflow-y-auto">
                    <div className="grid grid-cols-4 gap-1">
                      {(() => {
                        const currentSeason = contentMetadata.episodes.find(s => s.season === selectedSeason);
                        return currentSeason?.episodes.map((ep, index) => (
                          <button
                            key={index}
                            onClick={() => setSelectedEpisode(ep.episode)}
                            className={`px-2 py-1 text-xs rounded transition-colors ${selectedEpisode === ep.episode
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                              }`}
                            title={ep.title}
                          >
                            {ep.episode}
                          </button>
                        )) || [];
                      })()}
                    </div>
                  </div>
                </div>

                {/* Selected Episode Info */}
                {(() => {
                  const currentSeason = contentMetadata.episodes.find(s => s.season === selectedSeason);
                  const currentEpisode = currentSeason?.episodes.find(e => e.episode === selectedEpisode);
                  return currentEpisode && (
                    <div className="bg-gray-50 rounded p-2 text-xs">
                      <p className="font-medium text-gray-800">
                        S{selectedSeason}E{selectedEpisode}: {currentEpisode.title}
                      </p>
                    </div>
                  );
                })()}
              </div>
            )}

            {/* Buttons */}
            <div className="space-y-2 mt-auto">
              <button
                onClick={() => getTorrents(contentMetadata?.is_movie || false, imdbId, selectedSeason, selectedEpisode, setTorrentsData, setIsLoading)}
                disabled={!imdbId || isLoading || isScraping}
                className={`w-full font-medium py-2 px-4 text-sm rounded transition-all ${!imdbId || isLoading || isScraping
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700'
                  }`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Searching...
                  </div>
                ) : isScraping ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading details...
                  </div>
                ) : (
                  '🔍 Find Torrents'
                )}
              </button>

              {contentMetadata && !contentMetadata.is_movie && torrentsData.length > 0 && (
                <button
                  onClick={handleNextEpisode}
                  disabled={isLoading}
                  className={`w-full font-medium py-2 px-4 text-sm rounded transition-all ${isLoading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700'
                    }`}
                >
                  ⏭️ Next Episode (E{selectedEpisode + 1})
                </button>
              )}
            </div>
          </div>

          {/* Right Column - Torrents List */}
          <div className="flex flex-col min-h-0">
            {torrentsData.length > 0 && (
              <div className="bg-white rounded-lg shadow-xl p-4 h-full flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-bold text-gray-800">Available Torrents</h2>
                  <button
                    onClick={handleAutoSelect}
                    disabled={isStreaming || torrentsData.length === 0}
                    className={`px-3 py-1 text-xs rounded transition-colors ${isStreaming || torrentsData.length === 0
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-yellow-500 hover:bg-yellow-600 text-white'
                      }`}
                  >
                    ⚡ Auto Select
                  </button>
                </div>

                {/* Disclaimer */}
                <div className="bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
                  <p className="text-yellow-800 text-xs">
                    <strong>⚠️ Note:</strong> Auto-select chooses the top torrent. Manual selection recommended for specific preferences.
                  </p>
                </div>

                {/* Scrollable Torrents List */}
                <div className="flex-1 overflow-y-auto space-y-2">
                  {torrentsData.map((torrent, index) => (
                    <div key={index} className="bg-gray-50 rounded p-3 border border-gray-200 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-800 text-sm mb-1 truncate">
                            {torrent.name}
                          </h3>
                          <div className="flex flex-wrap gap-1 text-xs">
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
                              {torrent.quality}
                            </span>
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-green-100 text-green-800">
                              🌱 {torrent.seeders}
                            </span>
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-800">
                              📦 {torrent.size}
                            </span>
                            {index === 0 && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full bg-yellow-100 text-yellow-800">
                                ⭐ Best
                              </span>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => stream(torrent, contentMetadata?.is_movie || false, selectedSeason, selectedEpisode, imdbId, setIsStreaming, setStreamingContent)}
                          disabled={isStreaming}
                          className={`ml-2 px-2 py-1 text-xs rounded transition-colors flex items-center gap-1 ${isStreaming
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                            }`}
                        >
                          ▶️ Stream
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty state when no torrents */}
            {torrentsData.length === 0 && !isLoading && !showWatchedList && !showContentDetail && (
              <div className="bg-white rounded-lg shadow-xl p-4 h-full flex flex-col">
                <div className="text-center mb-4">
                  <div className="text-4xl mb-2">🔍</div>
                  <h3 className="text-sm font-semibold mb-1">No Torrents</h3>
                  <p className="text-xs text-gray-500">
                    {contentMetadata
                      ? 'Click "Find Torrents" to search'
                      : 'Enter IMDB ID to start'
                    }
                  </p>
                </div>

                {watchedContent.length > 0 && (
                  <div className="flex-1 flex flex-col">
                    {/* Last Watched Section */}
                    {(() => {
                      const lastWatched = watchedContent.find(content => content.last_watched);
                      return lastWatched && (
                        <div className="mb-4">
                          <h3 className="text-sm font-semibold text-gray-800 mb-2">🕒 Last Watched</h3>
                          <div
                            className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200 cursor-pointer hover:shadow-md transition-shadow"
                            onClick={() => handleContentClick(lastWatched)}
                          >
                            <div className="flex items-center space-x-3">
                              <div className="w-12 h-16 bg-gray-300 rounded flex items-center justify-center text-xs">
                                {lastWatched.poster && lastWatched.poster !== 'placeholder' ? (
                                  <img src={lastWatched.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                                ) : (
                                  <span className="text-lg">{lastWatched.is_movie ? '🎬' : '📺'}</span>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <h4 className="font-medium text-gray-800 text-sm truncate">
                                  {lastWatched.title || lastWatched.imdb_id}
                                </h4>
                                <p className="text-xs text-gray-600">
                                  {lastWatched.is_movie ? 'Movie' : `TV Show • ${lastWatched.torrents?.length || 0} episodes`}
                                </p>
                                <div className="flex gap-1 mt-1">
                                  <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-blue-100 text-blue-800">
                                    {lastWatched.is_movie ? 'Movie' : 'Series'}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })()}

                    {/* Watched Section */}
                    {(() => {
                      const otherWatched = watchedContent.filter(content => !content.last_watched);
                      return otherWatched.length > 0 && (
                        <div className="flex-1 flex flex-col min-h-0">
                          <h3 className="text-sm font-semibold text-gray-800 mb-2">📚 Watched</h3>
                          <div className="flex-1 overflow-y-auto space-y-2">
                            {otherWatched.map((content, index) => (
                              <div
                                key={index}
                                className="bg-gray-50 rounded-lg p-3 border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
                                onClick={() => handleContentClick(content)}
                              >
                                <div className="flex items-center space-x-3">
                                  <div className="w-10 h-14 bg-gray-300 rounded flex items-center justify-center text-xs flex-shrink-0">
                                    {content.poster && content.poster !== 'placeholder' ? (
                                      <img src={content.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                                    ) : (
                                      <span className="text-sm">{content.is_movie ? '🎬' : '📺'}</span>
                                    )}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <h4 className="font-medium text-gray-800 text-sm truncate">
                                      {content.title || content.imdb_id}
                                    </h4>
                                    <p className="text-xs text-gray-600">
                                      {content.is_movie ? 'Movie' : `TV Show • ${content.torrents?.length || 0} episodes`}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}
              </div>
            )}

            {/* Content Detail View */}
            {showContentDetail && contentMetadata && (
              <div className="bg-white rounded-lg shadow-xl p-4 h-full flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <button
                    onClick={handleBackToMain}
                    className="px-2 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600 transition-colors"
                  >
                    ← Back
                  </button>
                  <h2 className="text-lg font-bold text-gray-800 truncate">
                    {contentMetadata.title || contentMetadata.imdb_id}
                  </h2>
                </div>

                {contentMetadata.is_movie ? (
                  /* Movie Detail View */
                  <div className="text-center flex-1 flex flex-col justify-center">
                    <div className="mb-4">
                      <div className="w-20 h-28 bg-gray-300 rounded mx-auto mb-3 flex items-center justify-center">
                        {contentMetadata.poster && contentMetadata.poster !== 'placeholder' ? (
                          <img src={contentMetadata.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                        ) : (
                          <span className="text-2xl">🎬</span>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-800 mb-2">
                        {contentMetadata.title || contentMetadata.imdb_id}
                      </h3>
                      <div className="flex justify-center gap-2 mb-4">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                          Movie
                        </span>
                      </div>
                      <button
                        onClick={() => getTorrents(true, imdbId, 1, 1, setTorrentsData, setIsLoading)}
                        className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                      >
                        🔍 Find Movie Torrents
                      </button>
                    </div>
                  </div>
                ) : (
                  /* TV Show Detail View */
                  <div className="flex-1 flex flex-col min-h-0">
                    <div className="mb-3">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-12 h-16 bg-gray-300 rounded flex items-center justify-center">
                          {contentMetadata.poster && contentMetadata.poster !== 'placeholder' ? (
                            <img src={contentMetadata.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                          ) : (
                            <span className="text-lg">📺</span>
                          )}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-800">
                            {contentMetadata.title || contentMetadata.imdb_id}
                          </h3>
                          <p className="text-xs text-gray-600">
                            {contentMetadata.seasons || 0} seasons available
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Seasons & Episodes List */}
                    <div className="flex-1 overflow-y-auto">
                      <h4 className="text-sm font-semibold text-gray-800 mb-2">All Episodes</h4>
                      <div className="space-y-3">
                        {contentMetadata.episodes?.map((seasonData, seasonIndex) => (
                          <div key={seasonIndex} className="border border-gray-200 rounded-lg p-3">
                            <h5 className="font-medium text-gray-800 mb-2">Season {seasonData.season}</h5>
                            <div className="grid grid-cols-2 gap-2">
                              {seasonData.episodes.map((ep, epIndex) => (
                                <button
                                  key={epIndex}
                                  onClick={() => handleEpisodeSelect(seasonData.season, ep.episode)}
                                  className="bg-gray-50 hover:bg-blue-50 rounded p-2 text-left transition-colors"
                                >
                                  <div className="font-medium text-xs text-gray-800">
                                    E{ep.episode}
                                  </div>
                                  <div className="text-xs text-gray-600 truncate">
                                    {ep.title}
                                  </div>
                                </button>
                              ))}
                            </div>
                          </div>
                        )) || (
                            <div className="text-center text-gray-500 py-4">
                              <p className="text-sm">No episode data available</p>
                            </div>
                          )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Watched Content Detail View */}
            {showWatchedList && selectedContent && (
              <div className="bg-white rounded-lg shadow-xl p-4 h-full flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <button
                    onClick={handleBackToWatched}
                    className="px-2 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600 transition-colors"
                  >
                    ← Back
                  </button>
                  <h2 className="text-lg font-bold text-gray-800 truncate">
                    {selectedContent.title || selectedContent.imdb_id}
                  </h2>
                </div>

                {selectedContent.is_movie ? (
                  /* Movie View */
                  <div className="text-center flex-1 flex flex-col justify-center">
                    <div className="mb-4">
                      <div className="w-20 h-28 bg-gray-300 rounded mx-auto mb-3 flex items-center justify-center">
                        {selectedContent.poster && selectedContent.poster !== 'placeholder' ? (
                          <img src={selectedContent.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                        ) : (
                          <span className="text-2xl">🎬</span>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-800 mb-2">
                        {selectedContent.title || selectedContent.imdb_id}
                      </h3>
                      <div className="flex justify-center gap-2 mb-4">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                          Movie
                        </span>
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                          Watched
                        </span>
                      </div>
                      <button
                        onClick={() => playContent(selectedContent)}
                        className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                      >
                        ▶️ Play Movie
                      </button>
                    </div>
                  </div>
                ) : (
                  /* TV Show View */
                  <div className="flex-1 flex flex-col min-h-0">
                    <div className="mb-3">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-12 h-16 bg-gray-300 rounded flex items-center justify-center">
                          {selectedContent.poster && selectedContent.poster !== 'placeholder' ? (
                            <img src={selectedContent.poster} alt="Poster" className="w-full h-full object-cover rounded" />
                          ) : (
                            <span className="text-lg">📺</span>
                          )}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-800">
                            {selectedContent.title || selectedContent.imdb_id}
                          </h3>
                          <p className="text-xs text-gray-600">
                            {selectedContent.torrents?.length || 0} episodes watched
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Episodes List */}
                    <div className="flex-1 overflow-y-auto">
                      <h4 className="text-sm font-semibold text-gray-800 mb-2">Watched Episodes</h4>
                      <div className="space-y-2">
                        {selectedContent.torrents
                          ?.sort((a, b) => {
                            // Sort by season first, then episode
                            if (a.season !== b.season) {
                              return (a.season || 1) - (b.season || 1);
                            }
                            return (a.episode || 1) - (b.episode || 1);
                          })
                          .map((torrent, index) => (
                            <div key={index} className="bg-gray-50 rounded p-2 border border-gray-200">
                              <div className="flex items-center justify-between">
                                <div className="flex-1 min-w-0">
                                  <h5 className="font-medium text-gray-800 text-sm truncate">
                                    S{torrent.season || 1}E{torrent.episode || 1}
                                    {(() => {
                                      // Try to find episode title from content metadata
                                      const seasonData = selectedContent.episodes?.find(s => s.season === torrent.season);
                                      const episodeData = seasonData?.episodes.find(e => e.episode === torrent.episode);
                                      return episodeData ? ` - ${episodeData.title}` : ` - ${torrent.name}`;
                                    })()}
                                  </h5>
                                  <div className="flex gap-1 mt-1">
                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-blue-100 text-blue-800">
                                      {torrent.quality}
                                    </span>
                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-green-100 text-green-800">
                                      🌱 {torrent.seeders}
                                    </span>
                                  </div>
                                </div>
                                <div className="flex gap-1">
                                  <button
                                    onClick={() => playContent(selectedContent, torrent.season || 1, torrent.episode || 1)}
                                    className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors flex-shrink-0"
                                  >
                                    ▶️ Play
                                  </button>
                                  {!selectedContent.is_movie && (() => {
                                    // Find next episode or next season
                                    const currentSeason = selectedContent.episodes?.find(s => s.season === torrent.season);
                                    const nextEpisode = (torrent.episode || 1) + 1;
                                    const hasNextEpisode = currentSeason?.episodes.some(ep => ep.episode === nextEpisode);

                                    // If no next episode in current season, check for next season
                                    let nextSeasonNum = null;
                                    let nextSeasonFirstEp = null;
                                    if (!hasNextEpisode) {
                                      const nextSeason = selectedContent.episodes?.find(s => s.season === (torrent.season || 1) + 1);
                                      if (nextSeason && nextSeason.episodes.length > 0) {
                                        nextSeasonNum = nextSeason.season;
                                        nextSeasonFirstEp = nextSeason.episodes[0].episode;
                                      }
                                    }

                                    if (hasNextEpisode || nextSeasonNum) {
                                      const targetSeason = hasNextEpisode ? (torrent.season || 1) : nextSeasonNum;
                                      const targetEpisode = hasNextEpisode ? nextEpisode : nextSeasonFirstEp;
                                      const buttonText = hasNextEpisode ? "⏭️ Next" : "⏩ S" + nextSeasonNum;

                                      return (
                                        <button
                                          onClick={() => {
                                            // Set states and find torrents for next episode/season
                                            setSelectedSeason(targetSeason);
                                            setSelectedEpisode(targetEpisode);
                                            setImdbId(selectedContent.imdb_id);
                                            setContentMetadata(selectedContent);
                                            getTorrents(false, selectedContent.imdb_id, targetSeason, targetEpisode, setTorrentsData, setIsLoading);
                                            setShowWatchedList(false);
                                          }}
                                          className="px-2 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 transition-colors flex-shrink-0"
                                        >
                                          {buttonText}
                                        </button>
                                      );
                                    }
                                    return null;
                                  })()}
                                </div>
                              </div>
                            </div>
                          )) || (
                            <div className="text-center text-gray-500 py-4">
                              <p className="text-sm">No episodes watched yet</p>
                            </div>
                          )}
                      </div>
                    </div>

                    {/* Quick Season/Episode Selector */}
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <h4 className="text-sm font-semibold text-gray-800 mb-2">Find New Episode</h4>
                      <div className="flex gap-2 items-end">
                        <div className="flex-1">
                          <label className="block text-xs text-gray-500 mb-1">Season</label>
                          <select
                            value={selectedSeason}
                            onChange={(e) => {
                              setSelectedSeason(parseInt(e.target.value));
                              setSelectedEpisode(1);
                            }}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none"
                          >
                            {selectedContent.episodes?.map((seasonData, index) => (
                              <option key={index} value={seasonData.season}>
                                Season {seasonData.season}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="flex-1">
                          <label className="block text-xs text-gray-500 mb-1">Episode</label>
                          <select
                            value={selectedEpisode}
                            onChange={(e) => setSelectedEpisode(parseInt(e.target.value))}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none"
                          >
                            {(() => {
                              const currentSeason = selectedContent.episodes?.find(s => s.season === selectedSeason);
                              return currentSeason?.episodes.map((ep, index) => (
                                <option key={index} value={ep.episode}>
                                  E{ep.episode} - {ep.title}
                                </option>
                              )) || [];
                            })()}
                          </select>
                        </div>
                        <button
                          onClick={() => {
                            // Set the IMDB ID and fetch torrents for the specified episode
                            setImdbId(selectedContent.imdb_id);
                            setContentMetadata(selectedContent);
                            getTorrents(false, selectedContent.imdb_id, selectedSeason, selectedEpisode, setTorrentsData, setIsLoading);
                            setShowWatchedList(false);
                          }}
                          className="px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 transition-colors"
                        >
                          🔍 Find
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Streaming Overlay */}
        {isStreaming && streamingContent && (
          <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
            <div className="text-center text-white">
              <div className="mb-4">
                <div className="animate-pulse text-6xl mb-4">📺</div>
                <h2 className="text-3xl font-bold mb-2">Now Streaming</h2>
              </div>
              <div className="bg-black bg-opacity-50 rounded-lg p-6 max-w-md">
                <h3 className="text-xl font-semibold mb-2">{streamingContent.name}</h3>
                {!streamingContent.isMovie && (
                  <p className="text-lg text-gray-300">
                    Season {streamingContent.season} • Episode {streamingContent.episode}
                  </p>
                )}
                <div className="mt-4 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-2"></div>
                  <span>Loading stream...</span>
                </div>
                <button
                  onClick={() => {
                    setIsStreaming(false);
                    setStreamingContent(null);
                  }}
                  className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

async function getTorrents(isMovie, imdbId, season, episode, setTorrentsData, setIsLoading) {
  if (!imdbId) {
    alert('Please enter a valid IMDB ID');
    return;
  }

  setIsLoading(true);
  setTorrentsData([]);

  try {
    const url = isMovie
      ? `${BASE_BACKEND_URL}/torrents/movie/`
      : `${BASE_BACKEND_URL}/torrents/show/`;

    const response = await axios.get(url, {
      params: {
        imdb_id: imdbId,
        season: isMovie ? undefined : season,
        episode: isMovie ? undefined : episode
      }
    });

    if (response.status === 200) {
      const torrents = response.data.torrents;
      if (torrents && torrents.length > 0) {
        setTorrentsData(torrents);
      } else {
        alert(`No torrents found for ${isMovie ? 'this movie' : `Season ${season} Episode ${episode}`}`);
      }
    } else {
      alert('Error fetching torrents');
    }
  } catch (error) {
    console.error('Error fetching torrents:', error);
    alert('Error fetching torrents. Please check backend service is running.');
  } finally {
    setIsLoading(false);
  }
}

async function stream(torrent, is_movie, season, episode, imdbId, setIsStreaming, setStreamingContent) {
  if (!torrent) {
    alert('Please select a valid torrent');
    return;
  }

  setIsStreaming(true);

  // Set streaming content info for the overlay
  setStreamingContent({
    name: torrent.name,
    isMovie: is_movie,
    season: season,
    episode: episode
  });

  try {
    const url = `${BASE_BACKEND_URL}/stream/vlc`;

    const response = await axios.get(url, {
      params: {
        magnet_link: torrent.magnet,
        file_idx: torrent.file_idx,
        file_name: torrent.name,
        imdb_id: imdbId,
        is_movie: is_movie,
        info_hash: torrent.info_hash,
        season: season,
        episode: episode
      }
    });

    if (response.status === 200) {
      // Store in watched database with new structure
      await saveWatchedContent(imdbId, is_movie, season, episode, torrent);

      // Keep the overlay visible for a few seconds to show streaming started
      setTimeout(() => {
        setIsStreaming(false);
        setStreamingContent(null);
      }, 3000);
    } else {
      alert('Error streaming torrent');
      setIsStreaming(false);
      setStreamingContent(null);
    }
  } catch (error) {
    console.error('Error streaming torrent:', error);
    alert('Error streaming. Please check backend service is running.');
    setIsStreaming(false);
    setStreamingContent(null);
  }
}

async function saveWatchedContent(imdbId, is_movie, season, episode, torrent) {
  try {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      // Get current watched and indexed data
      const result = await chrome.storage.local.get(['404stream_watched', '404stream_indexed']);
      const watched = result['404stream_watched'] || [];
      const indexed = result['404stream_indexed'] || [];

      // Find metadata (first in watched, then in indexed)
      let metadata = watched.find(item => item.imdb_id === imdbId);
      if (!metadata) {
        metadata = indexed.find(item => item.imdb_id === imdbId);
      }

      if (!metadata) {
        // If no metadata found, create basic entry
        metadata = {
          imdb_id: imdbId,
          title: torrent.name,
          poster: 'placeholder',
          is_movie: is_movie,
          seasons: is_movie ? 0 : 1,
          episodes: []
        };
      }

      // Clear last_watched from all items first
      watched.forEach(item => item.last_watched = false);

      // Find existing watched entry or create new
      let existingIndex = watched.findIndex(item => item.imdb_id === imdbId);

      if (existingIndex !== -1) {
        // Update existing entry
        watched[existingIndex].last_watched = true;

        // Check if this specific episode/movie already watched
        const alreadyWatched = watched[existingIndex].torrents?.some(t =>
          is_movie ? true : (t.season === season && t.episode === episode)
        );

        if (!alreadyWatched) {
          watched[existingIndex].torrents = [...(watched[existingIndex].torrents || []), { ...torrent, season, episode }];
        }
      } else {
        // Create new entry - move from indexed to watched
        watched.push({
          ...metadata,
          torrents: [{ ...torrent, season, episode }],
          last_watched: true
        });

        // Remove from indexed if it was there
        const indexedIndex = indexed.findIndex(item => item.imdb_id === imdbId);
        if (indexedIndex !== -1) {
          indexed.splice(indexedIndex, 1);
          await chrome.storage.local.set({ '404stream_indexed': indexed });
        }
      }

      await chrome.storage.local.set({ '404stream_watched': watched });
    }
  } catch (error) {
    console.error('Error saving watched content:', error);
  }
}
