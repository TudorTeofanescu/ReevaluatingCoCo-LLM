# CoCo Analysis: nbolkmjllpbfmloclgmmelkbhfhkgjja

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nbolkmjllpbfmloclgmmelkbhfhkgjja/opgen_generated_files/bg.js
Line 1036 if (request.type === "download" && request.fileName) {

**Code:**

```javascript
// Background script - service_worker.js
const setLocalCurrentDownload = (value) => {
  chrome.storage.local.set({ currentDownloadItem: value }, function () {
    console.log("New file value is: " + value);
  });
};

// External message handler
chrome.runtime.onMessageExternal.addListener(function (
  request,
  _sender,
  sendResponse
) {
  if (request.type === "download" && request.fileName) {
    try {
      setLocalCurrentDownload(request.fileName); // ← attacker-controlled fileName stored
      sendResponse({ status: "success" });
    } catch (error) {
      sendResponse({ status: "error" });
    }
  } else if (request.type === "check") {
    sendResponse({ status: "installed" });
  }
});

// Download completion handler - retrieval path
chrome.downloads.onChanged.addListener(async function (delta) {
  if (!delta.state || delta.state.current != "complete") {
    return;
  }

  if (delta.state.current === "complete") {
    chrome.storage.local.get(["currentDownloadItem"], function (result) {
      if (!result.currentDownloadItem) return;

      // Search for matching downloads
      chrome.downloads.search(
        {
          orderBy: ["-startTime"],
          limit: 10,
        },
        function (downloadedItems) {
          // Filter: stored value only used as search filter, not returned to attacker
          const downloadedItem = downloadedItems.find(
            ({ filename = "" }) =>
              filename &&
              filename.includes(`${result.currentDownloadItem}`) && // ← stored value used for filtering
              filename.endsWith(".zip")
          );

          if (downloadedItem) {
            setLocalCurrentDownload("");
            // Open in RadiAnt - uses actual download filename, not attacker-controlled value
            chrome.tabs.create({
              url: `radiant://?n=f&v=${escape(
                `"${downloadedItem.filename}"` // ← comes from chrome.downloads.search, not storage
              )}`,
              active: true,
            });
          }
        }
      );
    });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** While the extension accepts external messages and stores the attacker-controlled `fileName` value, this is incomplete storage exploitation. The stored value is retrieved but only used internally as a filter for matching downloads via `filename.includes(result.currentDownloadItem)`. The attacker cannot retrieve the poisoned value back through sendResponse, postMessage, or any attacker-accessible output. Per the methodology, storage poisoning alone (without retrieval path to attacker) is NOT a vulnerability.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nbolkmjllpbfmloclgmmelkbhfhkgjja/opgen_generated_files/cs_0.js
Line 469 window.addEventListener("message", (event) => {
Line 472 event.data &&
Line 474 event.data.fileName

**Code:**

```javascript
// Content script - content.js
window.addEventListener("message", (event) => {
  if (
    event.source == window &&
    event.data &&
    event.data.type == "download" &&
    event.data.fileName // ← attacker-controlled
  ) {
    const { fileName, type } = event.data;

    // Forward to background script
    browser.runtime.sendMessage({ fileName, type });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Same flow as Sink 1, but triggered via content script `window.postMessage` instead of `chrome.runtime.onMessageExternal`. The attacker-controlled `fileName` from the webpage flows through the content script to the background script where it's stored. However, as analyzed in Sink 1, this is incomplete storage exploitation without a retrieval path back to the attacker.
