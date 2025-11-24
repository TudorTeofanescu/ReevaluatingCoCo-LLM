# CoCo Analysis: lppaogojmfkmdopjfgclkphjemdkcobi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 event listeners with storage.sync poisoning

---

## Sink 1: cs_window_eventListener_commentim-success-login-on-site → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lppaogojmfkmdopjfgclkphjemdkcobi/opgen_generated_files/cs_0.js
Line 487: window.addEventListener("commentim-success-login-on-site", function(evt) {
Line 488: chrome.runtime.sendMessage(evt.detail);
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lppaogojmfkmdopjfgclkphjemdkcobi/opgen_generated_files/bg.js
Line 972: if (msg.type === 'isDevelopment')
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 487)
window.addEventListener("commentim-success-login-on-site", function(evt) {
    chrome.runtime.sendMessage(evt.detail);  // ← attacker-controlled data
}, false);

// Background script - Message handler (bg.js Line 970)
chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if(msg.type === 'userLoggedIn')
        notifyAllTabsAboutLogin(msg);  // ← attacker-controlled msg
})

// Background storage write (bg.js Line 1009)
function notifyAllTabsAboutLogin (msg) {
    chrome.storage.sync.set({'authData': msg}, function() {  // ← attacker-controlled authentication data stored
        //console.log('Settings saved');
    });

    msg.isBackground = true;
    chrome.tabs.query({}, function(tabs) {
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id, msg);  // ← broadcast to all tabs
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. While an attacker can poison the authData in storage by dispatching a custom event, there's no evidence in the CoCo traces showing that this stored data flows back to the attacker via sendResponse, postMessage, or is used in a subsequent vulnerable operation. The methodology requires a complete exploitation chain for TRUE POSITIVE.

---

## Sink 2: cs_window_eventListener_commentim-success-logout → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lppaogojmfkmdopjfgclkphjemdkcobi/opgen_generated_files/cs_0.js
Line 491: window.addEventListener("commentim-success-logout", function(evt) {
Line 492: logout(evt.detail);
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lppaogojmfkmdopjfgclkphjemdkcobi/opgen_generated_files/bg.js
Line 972: if (msg.type === 'isDevelopment')
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 491)
window.addEventListener("commentim-success-logout", function(evt) {
    logout(evt.detail);  // ← attacker-controlled data
}, false);

// Content script logout function (cs_0.js Line 505)
function logout(eventData) {
    chrome.runtime.sendMessage(eventData);  // ← forwards attacker data to background
}

// Background script - Message handler (bg.js Line 976)
chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if(msg.type === 'userLoggedOut')
        notifyAllTabsAboutLogout(msg);  // ← attacker-controlled msg
})

// Background storage manipulation (bg.js Line 1022)
function notifyAllTabsAboutLogout (msg) {
    chrome.storage.sync.remove(['authData'], function() {  // ← removes authData
        //todo: send request to server to verify token
    });

    msg.isBackground = true;
    chrome.tabs.query({}, function(tabs) {
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id, msg);  // ← broadcast to all tabs
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage manipulation without retrieval path. Although an attacker can trigger storage.remove() to delete authData, this is storage manipulation, not storage poisoning with a retrieval path. The methodology requires that stored data must flow back to attacker for TRUE POSITIVE.

---

## Sink 3: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lppaogojmfkmdopjfgclkphjemdkcobi/opgen_generated_files/cs_0.js
Line 495: window.addEventListener('message', function(event) {
Line 496: if (event.data.type && (event.data.type === "userLoggedOut"))
Line 496: event.data.type
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 495)
window.addEventListener('message', function(event) {
    if (event.data.type && (event.data.type === "userLoggedOut"))  // ← attacker controls event.data
        logout(event.data);  // ← attacker-controlled data
    if (event.data.type && (event.data.type === "toggleAnon"))
        chrome.runtime.sendMessage(event.data);
}, false);

// Content script logout function (cs_0.js Line 505)
function logout(eventData) {
    chrome.runtime.sendMessage(eventData);  // ← forwards to background
}

// Background script - Message handler (bg.js Line 976)
chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if(msg.type === 'userLoggedOut')
        notifyAllTabsAboutLogout(msg);  // ← triggers storage manipulation
    if(msg.type === 'userLoggedIn')
        notifyAllTabsAboutLogin(msg);  // ← triggers storage write
})

// Background storage operations
function notifyAllTabsAboutLogout (msg) {
    chrome.storage.sync.remove(['authData'], function() {});  // ← storage manipulation
    msg.isBackground = true;
    chrome.tabs.query({}, function(tabs) {
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id, msg);  // ← broadcast
        }
    });
}

function notifyAllTabsAboutLogin (msg) {
    chrome.storage.sync.set({'authData': msg}, function() {});  // ← storage write
    msg.isBackground = true;
    chrome.tabs.query({}, function(tabs) {
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id, msg);  // ← broadcast
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. While an attacker can use window.postMessage to trigger storage writes (userLoggedIn → storage.set) or storage removal (userLoggedOut → storage.remove), there's no evidence that the stored data flows back to the attacker. Per the methodology, storage poisoning alone is not a vulnerability - the stored data must flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation.
