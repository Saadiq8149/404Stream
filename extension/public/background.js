const imdbBaseUrl = "https://www.imdb.com/title/tt";
let popupWindowId = null;

chrome.action.onClicked.addListener(async (tab) => {
    // Extract IMDB ID from current tab if on IMDB
    if (tab.url && tab.url.startsWith(imdbBaseUrl)) {
        const imdbId = tab.url.split("/")[4];
        // Store IMDB ID using chrome.storage
        try {
            await chrome.storage.local.set({ imdbId: imdbId });
        } catch (error) {
            console.error("Error saving IMDB ID:", error);
        }
    }

    if (popupWindowId !== null) {
        try {
            await chrome.windows.remove(popupWindowId);
        } catch (e) {
            console.log("No active popup to close.");
        }
        popupWindowId = null;
    }

    chrome.windows.create({
        url: chrome.runtime.getURL("index.html"), // your custom HTML
        type: "popup",
    }, (win) => {
        popupWindowId = win.id;
    });
});

// Listen for tab updates to automatically detect IMDB pages
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith(imdbBaseUrl)) {
        const imdbId = tab.url.split("/")[4];
        try {
            await chrome.storage.local.set({ imdbId: imdbId });
        } catch (error) {
            console.error("Error saving auto-detected IMDB ID:", error);
        }
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Received message:", message);
    if (message.action === "close_popup" && popupWindowId !== null) {
        chrome.windows.remove(popupWindowId, () => {
            popupWindowId = null;
        });
    }
});
