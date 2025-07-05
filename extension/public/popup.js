const imdbBaseUrl = "https://www.imdb.com/title/tt";

const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

if (tab.url && tab.url.startsWith(imdbBaseUrl)) {
    console.log("Current tab URL:", tab.url);
    const imdbId = tab.url.split("/")[4];
    console.log("Extracted IMDB ID:", imdbId);
    try {
        await chrome.storage.local.set({ imdbId: imdbId });
        console.log("IMDB ID saved:", imdbId);
    } catch (error) {
        console.error("Error saving IMDB ID:", error);
    }
}
