# CoCo Analysis: pjafogomfdielggmlancphcgihlepjbp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjafogomfdielggmlancphcgihlepjbp/opgen_generated_files/bg.js
Line 974: `console.log('got regime. request.menuSearch: '+request.menuSearch);`

**Code:**

```javascript
// Background script - Line 966
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request) {
        if (request.message) {
            if (request.message == "version") {
                console.log('got version');
                sendResponse({version: 1.0});
            }
            else if (request.message == "regime") {
                console.log('got regime. request.menuSearch: '+request.menuSearch);
                chrome.storage.sync.set({menuSearch: request.menuSearch}, function() { // ← storage.set
                    chrome.contextMenus.removeAll();
                    if (request.menuSearch) createContextMenus();
                });
                sendResponse({menuSearch: request.menuSearch});
            }
        }
    }
    return true;
});

// Storage retrieval - Line 987
function restore_options() {
    chrome.storage.sync.get({
        menuSearch: true
    }, function(items) {
        if (items.menuSearch == true) createContextMenus(); // ← Only used internally
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While an external attacker can poison the `menuSearch` storage value via `chrome.runtime.onMessageExternal`, the stored data is only retrieved to create context menus internally. There is no path for the attacker to retrieve the poisoned data back (no sendResponse, postMessage, or fetch to attacker-controlled URL with the stored value).
