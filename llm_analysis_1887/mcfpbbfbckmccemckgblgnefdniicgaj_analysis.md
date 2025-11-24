# CoCo Analysis: mcfpbbfbckmccemckgblgnefdniicgaj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 distinct flow types (BookmarkTreeNode_source → sendResponseExternal, HistoryItem_source → sendResponseExternal, bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink, bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink, cs_window_eventListener_message → BookmarkSearchQuery_sink, cs_window_eventListener_message → bg_localStorage_setItem_value_sink)

---

## Sink 1: BookmarkTreeNode_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/bg.js
Line 848-853: BookmarkTreeNode constructor (multiple lines flagged)
Line 868-871: BookmarkTreeNode_source creation
```

**Classification:** FALSE POSITIVE (Referenced only CoCo framework code)

**Reason:** All the BookmarkTreeNode_source detections (20 separate detections) only reference CoCo's mock framework code (lines 844-874). These are CoCo's synthetic implementations of `chrome.bookmarks.getTree()` and `chrome.bookmarks.search()` for testing purposes. The actual extension code starts after the third "// original" marker. More critically, the extension lacks the "bookmarks" permission in manifest.json, which is required to access the Chrome bookmarks API. Without this permission, the bookmarks API would fail at runtime.

---

## Sink 2: HistoryItem_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/bg.js
Line 775-783: HistoryItem mock object creation
```

**Classification:** FALSE POSITIVE (Referenced only CoCo framework code)

**Reason:** All HistoryItem_source detections (8 separate detections) only reference CoCo's mock framework code (lines 773-786) that simulates `chrome.history.search()`. This is not actual extension code. Additionally, the extension lacks the "history" permission in manifest.json, which is required to access the Chrome history API. Without this permission, the history API would fail at runtime.

---

## Sink 3: bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/bg.js
Line 1079: searchBookmarks(request.query).then(res => {
```

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => { // ← attacker-controlled query
                sendResponse(res);
            });
            break;
        // ... other cases
    }
}

function searchBookmarks(query) {
    return new Promise((resolve, reject) => {
        chrome.bookmarks.search(query, (res) => { // BookmarkSearchQuery_sink
            resolve(res);
        });
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Missing required permissions. While an external attacker from whitelisted domain (findonlinemaps.xyztab.com) could trigger the flow via `chrome.runtime.onMessageExternal`, the extension lacks the "bookmarks" permission in manifest.json. Without this permission, `chrome.bookmarks.search()` would fail at runtime, making the vulnerability unexploitable.

---

## Sink 4: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/bg.js
Line 1107: if (request.status && request.account) {
Line 1108: localStorage.setItem('account', JSON.stringify(request.account));
```

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {
                localStorage.setItem('account', JSON.stringify(request.account)); // ← attacker-controlled
            } else {
                localStorage.removeItem('account');
            }
            break;
        // ... other cases
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is an incomplete storage exploitation pattern. An attacker from the whitelisted domain (findonlinemaps.xyztab.com) can write to `localStorage` via `chrome.runtime.onMessageExternal`, but there is no retrieval path where the poisoned data flows back to the attacker. Storage poisoning alone without a retrieval mechanism (sendResponse, postMessage to attacker, or use in a subsequent vulnerable operation) is NOT exploitable according to the methodology.

---

## Sink 5: cs_window_eventListener_message → BookmarkSearchQuery_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', function (e) {
Line 468: if (!e.data.from || e.data.from != '__findonlinemaps') {
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/bg.js
Line 1079: searchBookmarks(request.query).then(res => {
```

**Code:**

```javascript
// Content script (cs_0.js)
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__findonlinemaps') { // Check for specific origin marker
        return false;
    }

    chrome.runtime.sendMessage(e.data, (res) => { // ← attacker-controlled via postMessage
        const sender = {
            event: e.data.event,
            res: res
        };
        sendMessage(sender);
    });
});

// Background script (bg.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => { // ← attacker-controlled query
                sendResponse(res);
            });
            break;
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Missing required permissions. While a malicious webpage could bypass the `from` check (client-side checks are not security boundaries) and trigger the flow via `window.postMessage`, the extension lacks the "bookmarks" permission in manifest.json. Without this permission, `chrome.bookmarks.search()` would fail at runtime, making the vulnerability unexploitable.

---

## Sink 6: cs_window_eventListener_message → bg_localStorage_setItem_value_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', function (e) {
Line 468: if (!e.data.from || e.data.from != '__findonlinemaps') {
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mcfpbbfbckmccemckgblgnefdniicgaj/opgen_generated_files/bg.js
Line 1107: if (request.status && request.account) {
Line 1108: localStorage.setItem('account', JSON.stringify(request.account));
```

**Code:**

```javascript
// Content script (cs_0.js)
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__findonlinemaps') { // Bypassable check
        return false;
    }

    chrome.runtime.sendMessage(e.data, (res) => { // ← attacker-controlled via postMessage
        const sender = {
            event: e.data.event,
            res: res
        };
        sendMessage(sender);
    });
});

// Background script (bg.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {
                localStorage.setItem('account', JSON.stringify(request.account)); // ← attacker-controlled
            } else {
                localStorage.removeItem('account');
            }
            break;
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is an incomplete storage exploitation pattern. A malicious webpage could bypass the client-side `from` check and trigger storage writes via `window.postMessage`, but there is no retrieval path where the poisoned data flows back to the attacker. Storage poisoning alone without a retrieval mechanism is NOT exploitable according to the methodology.
