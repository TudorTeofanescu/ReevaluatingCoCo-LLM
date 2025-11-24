# CoCo Analysis: hniomffglcknlkjfhgelajihlafjnfpc

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 25

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hniomffglcknlkjfhgelajihlafjnfpc/opgen_generated_files/cs_0.js
Line 816: `window.addEventListener("message", function(event) {`
Line 819: `var msg = JSON.parse(event.data);`
Line 821: `var params = msg.params;`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hniomffglcknlkjfhgelajihlafjnfpc/opgen_generated_files/bg.js
Line 1388: `sidebar = params.sidebar;`
Line 1260-1266: `chrome.storage.local.set(items, function() {...`

**Code:**

```javascript
// Content script - sidebar.js (Lines 816-839)
window.addEventListener("message", function(event) {
    try {
        var msg = JSON.parse(event.data);
        var command = msg.command;
        var params = msg.params;
    }
    catch (e) {
        return;
    }

    switch (command) {
        case "fsGetSidebar":
            window.frames['fsSidebarFrame'].contentWindow.postMessage(
                JSON.stringify({command: "fsSetSidebar", params: sidebar}), "*");
            break;

        case "fsSetSidebar":
            toggleSidebar(false);
            setTimeout(function() {
                // Forward to background script
                chrome.runtime.sendMessage({command: "fsSetSidebar", params: params}); // ← attacker-controlled
            }, 350);
            break;
    }
});

// Background script - background.js (Lines 1387-1390)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    var command = request.command;
    var params = request.params;

    switch (command) {
        case "fsSetSidebar":
            sidebar = params.sidebar; // ← attacker-controlled data
            sidebarRestoreActive = true;
            saveSidebar(); // Writes to storage
            break;
    }
});

// saveSidebar function (Lines 1219-1283)
function saveSidebar() {
    chrome.storage.local.get(null, function(items) {
        if (items.fsSidebar.favorites.sort().join(",") != sidebar.favorites.sort().join(",")) {
            googleAnalitics({object: "Favorites", event: "update"});
            sidebar.requesting = true;
        }

        items.fsSidebar = sidebar; // Store attacker-controlled sidebar object
        chrome.storage.local.set(items, function() { // Storage write sink
            // Broadcast to all tabs
            chrome.tabs.query({}, function(tabs) {
                for (var i in tabs) {
                    if (tabs[i].url != "chrome://extensions/") {
                        chrome.tabs.sendMessage(tabs[i].id, {
                            command: "fsUpdateSidebar",
                            params: {sidebar: sidebar, restore: sidebarRestoreActive && (tabs[i].id == activeTab)}
                        });
                    }
                }
            });
        });
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker trigger. The content script only injects on FanSided Network sites and listens for postMessage events from an embedded iframe (`window.frames['fsSidebarFrame']`). The iframe is loaded from the extension itself (`index.html` as a web_accessible_resource). This is internal communication between the extension's own content script and its own iframe UI, not from external malicious webpages. A malicious website cannot trigger this flow because:
1. The message handler expects messages from the extension's own iframe
2. The iframe is part of the extension's trusted UI component
3. This is user interaction within the extension's own interface, not attacker-controlled input

The storage writes are initiated by user actions in the extension's sidebar UI, making this internal extension logic only.
