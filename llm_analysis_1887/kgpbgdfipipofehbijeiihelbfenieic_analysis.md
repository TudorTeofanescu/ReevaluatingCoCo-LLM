# CoCo Analysis: kgpbgdfipipofehbijeiihelbfenieic

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 6 (multiple similar traces)

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgpbgdfipipofehbijeiihelbfenieic/opgen_generated_files/cs_0.js
Line 1103: `window.addEventListener("message", function(event) {`
Line 1107: `var messageId = event.data.type + "." + event.data.id;`
Line 1435: `url: wexUtil.buildWallpaperDirectUrl(data.wallId) + "." + (data.extension === "png" ? "png" : "jpg")`
Line 1142: `return getProtocol() + "://w.wallhaven.cc/full/" + bucket + "/wallhaven-" + id;`

**Code:**

```javascript
// Content script - cs_0.js (lines 1103-1143)
window.addEventListener("message", function(event) {
    if (event.source != window || event.type != "message")
        return;

    var messageId = event.data.type + "." + event.data.id; // ← event.data from postMessage

    if (eventCallbacks[messageId]) {
        eventCallbacks[messageId].forEach(callback => {
            callback(event.data); // ← passes event.data to callbacks
        });
    }
});

// Callback registered for "inject.downloadImage" messages
wexUtil.onMessage("inject.downloadImage", function(data) {
    chrome.runtime.sendMessage({
        id: "download_image",
        url: wexUtil.buildWallpaperDirectUrl(data.wallId) + "." + (data.extension === "png" ? "png" : "jpg")
        // ← data.wallId comes from event.data
    });
});

// buildWallpaperDirectUrl function
var buildWallpaperDirectUrl = function(id) {
    var bucket = id.slice(0, 2); // ← takes first 2 chars
    return getProtocol() + "://w.wallhaven.cc/full/" + bucket + "/wallhaven-" + id;
    // ← constructs URL with hardcoded domain w.wallhaven.cc
};

// Background script - bg.js (lines 965-973)
chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.id == "download_image") {
            chrome.downloads.download({
                url: request.url // ← uses URL from message
            });
        }
    }
);
```

**Classification:** FALSE POSITIVE

**Reason:** While the extension accepts messages via window.postMessage and uses attacker-controlled data (data.wallId) to construct a download URL, the URL is constrained to the hardcoded domain "w.wallhaven.cc". The buildWallpaperDirectUrl function constructs: `https://w.wallhaven.cc/full/[bucket]/wallhaven-[id]`. The attacker can only control the ID portion, which results in downloading different images from the legitimate wallhaven.cc domain. The attacker cannot cause arbitrary downloads from attacker-controlled domains. This does not achieve the "arbitrary downloads" impact criterion required for a TRUE POSITIVE - the downloads are restricted to legitimate wallpaper images from wallhaven.cc.
