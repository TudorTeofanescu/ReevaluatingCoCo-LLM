# CoCo Analysis: pbfcbgceiloelbgjlplcgodohedpcnjo

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 8 (all related to storage.set with various data fields)

---

## Sink: document_eventListener_handler-hack → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pbfcbgceiloelbgjlplcgodohedpcnjo/opgen_generated_files/cs_0.js
Line 542 document.addEventListener("handler-hack", function (e) {
Line 543 var detail = e.detail;
Line 544 chrome.runtime.sendMessage({"id": detail.id, "data": detail.data});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pbfcbgceiloelbgjlplcgodohedpcnjo/opgen_generated_files/bg.js
Line 1021 playlists[data["playlist-id"]].items.push(new PlaylistItem(data.title, data.description, data["image-url"], data.url, data.type));
Line 1023 chrome.storage.sync.set({'playlists': playlists});

**Code:**

```javascript
// handler-hack.js (injected script running in page context)
window.embeddedMedia.handle = function(ev, data) {
    _handle(ev, data);
    var event = new CustomEvent("handler-hack", {
        "detail": {"id": "content/handler-hack", "data": nData}
    });
    document.dispatchEvent(event);
}

// cs_0.js (content script)
document.addEventListener("handler-hack", function (e) {
    var detail = e.detail;
    chrome.runtime.sendMessage({"id": detail.id, "data": detail.data});
}, false);

// bg.js (background script)
chrome.runtime.onMessage.addListener(function(info, sender, sendResponse) {
    var data = info.data;
    switch (info.id) {
        case "content/playlist-controls": {
            playlists[data["playlist-id"]].items.push(
                new PlaylistItem(data.title, data.description,
                                data["image-url"], data.url, data.type)
            );
            chrome.storage.sync.set({'playlists': playlists});
            break;
        }
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without any retrieval path to the attacker. The extension stores attacker-controlled data (title, description, image-url, url, type) in chrome.storage.sync, but there is no mechanism for the attacker to retrieve this data back. The stored playlists are only used internally by the extension's popup and are not sent back to content scripts or web pages. Storage poisoning alone is not a vulnerability per the methodology.
