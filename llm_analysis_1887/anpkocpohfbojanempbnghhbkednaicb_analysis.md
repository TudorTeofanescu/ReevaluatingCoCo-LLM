# CoCo Analysis: anpkocpohfbojanempbnghhbkednaicb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 31 (21 bookmark/history data disclosure sinks, 2 bookmark search sinks, 2 storage poisoning sinks, plus duplicates)

---

## Sink Group 1: BookmarkTreeNode_source → sendResponseExternal_sink (20 detections)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anpkocpohfbojanempbnghhbkednaicb/opgen_generated_files/bg.js
Lines 845-871: Multiple properties of BookmarkTreeNode object (CoCo framework mock code)

**Note:** CoCo detected these flows in framework mock code. The actual extension code attempts to use chrome.bookmarks.search API.

**Code:**

```javascript
// Background script (bg.js)

// External message handler
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {  // Line 1072
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {  // Line 1077
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:  // Line 1082
            searchBookmarks(request.query).then(res => {  // Line 1083
                sendResponse(res);  // Line 1084 - Would send bookmark data to external caller
            });
            break;
        // ... other cases
    }
}

function searchBookmarks(query) {  // Line 1123
    return new Promise((resolve, reject) => {
        chrome.bookmarks.search(query, (res) => {  // Line 1125 - Requires "bookmarks" permission
            resolve(res);
        });
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Missing permissions. The extension attempts to use chrome.bookmarks.search API (line 1125) which requires the "bookmarks" permission in manifest.json. The manifest only declares "storage" permission (line 45), so the bookmarks API calls will fail. Without the required permission, the extension cannot access bookmark data, making this flow non-exploitable.

---

## Sink Group 2: HistoryItem_source → sendResponseExternal_sink (8 detections)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anpkocpohfbojanempbnghhbkednaicb/opgen_generated_files/bg.js
Lines 775-783: Properties of HistoryItem object (CoCo framework mock code)

**Code:**

```javascript
// Background script (bg.js)

function listener(request, sender, sendResponse) {  // Line 1077
    switch(request.event) {
        case EVENTS.SEARCH_HISTORY:  // Line 1087
            searchHistory(request.query).then(res => {  // Line 1088
                sendResponse(res);  // Line 1089 - Would send history data to external caller
            });
            break;
        // ... other cases
    }
}

function searchHistory(query) {  // Line 1131
    return new Promise((resolve, reject) => {
        chrome.history.search({ text: query, maxResults: 10 }, (res) => {  // Line 1133 - Requires "history" permission
            resolve(res);
        });
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Missing permissions. The extension attempts to use chrome.history.search API (line 1133) which requires the "history" permission in manifest.json. The manifest only declares "storage" permission, so the history API calls will fail. Without the required permission, the extension cannot access history data, making this flow non-exploitable.

---

## Sink Group 3: bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anpkocpohfbojanempbnghhbkednaicb/opgen_generated_files/bg.js
Line 1083: searchBookmarks(request.query)

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink Group 1 - missing "bookmarks" permission. The chrome.bookmarks.search API requires the "bookmarks" permission which is not declared in manifest.json.

---

## Sink Group 4: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anpkocpohfbojanempbnghhbkednaicb/opgen_generated_files/bg.js
Line 1111: if (request.status && request.account)
Line 1112: chrome.storage.local.set({account: JSON.stringify(request.account)})

**Code:**

```javascript
// Background script (bg.js)

chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {  // Line 1072
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {  // Line 1077
    switch(request.event) {
        case EVENTS.SET_USER_STATUS:  // Line 1110
            if (request.status && request.account) {  // Line 1111
                chrome.storage.local.set({account: JSON.stringify(request.account)})  // Line 1112 - SINK
            }
            break;
        // ... other cases
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. This is storage poisoning only (chrome.storage.local.set) without a retrieval path back to the attacker. The extension does not have any code that reads the 'account' value from storage and sends it back via sendResponse, postMessage, or any other attacker-accessible output. Storage poisoning alone is not exploitable per the methodology - the attacker must be able to retrieve the poisoned data back.

---

## Sink Group 5: cs_window_eventListener_message → BookmarkSearchQuery_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anpkocpohfbojanempbnghhbkednaicb/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', function (e)
Line 468: if (!e.data.from || e.data.from != '__newtab')
Line 477: chrome.runtime.sendMessage(e.data)

**Code:**

```javascript
// Content script (cs_0.js)

window.addEventListener('message', function (e) {  // Line 467
    if (!e.data.from || e.data.from != '__newtab') {  // Line 468 - Attacker can set this
        return false;
    }

    chrome.runtime.sendMessage(e.data, (res) => {  // Line 477 - Forwards to background
        const sender = {
            event: e.data.event,
            res: res
        };
        sendMessage(sender);  // Line 486 - Sends response back via postMessage
    });
});

function sendMessage(sender) {  // Line 501
    sender.from = 'ext';
    window.postMessage(sender, '*');  // Line 503 - Wildcard origin
}
```

**Classification:** FALSE POSITIVE

**Reason:** Missing permissions. Although this flow exists (webpage → postMessage → content script → background → bookmarks API), the chrome.bookmarks.search API still requires the "bookmarks" permission which is not in manifest.json. The API call will fail regardless of how it's triggered.

---

## Sink Group 6: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anpkocpohfbojanempbnghhbkednaicb/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', function (e)
Line 477: chrome.runtime.sendMessage(e.data)

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink Group 4 - incomplete storage exploitation. Although the attacker can trigger storage.set via postMessage → runtime.sendMessage, there's no retrieval path to get the poisoned data back. The stored 'account' value is never read and sent back to the attacker.
