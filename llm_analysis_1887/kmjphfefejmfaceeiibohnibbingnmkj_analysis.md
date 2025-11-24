# CoCo Analysis: kmjphfefejmfaceeiibohnibbingnmkj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detections of same flow)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmjphfefejmfaceeiibohnibbingnmkj/opgen_generated_files/bg.js
Line 1037 chrome.storage.sync.set({ 'authToken': message.token });

**Code:**

```javascript
// bg.js - Lines 1032-1050: External message listener
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    console.log('Received message from external extension: ' + JSON.stringify(message));

    switch(message.purpose) {
        case 'saveToken':
            chrome.storage.sync.set({ 'authToken': message.token }); // ← Attacker-controlled token stored
            chrome.action.setBadgeText({ text: null });
            break;
        default:
            // Just to fix a bug with zenodotus not not updating anything
            chrome.storage.sync.set({ 'authToken': message.token }); // ← Also stored in default case
            chrome.action.setBadgeText({ text: null });
            console.log('Unknown message purpose: ' + message.purpose);
            break;
    }
    return true;
})

// auth_management.js - Lines 3-6: Token retrieval
async function getAuthKey() {
    let result = await chrome.storage.sync.get(['authToken']);
    return result.authToken; // ← Retrieved token
}

// bg.js - Lines 1052-1084: Token used to submit links
async function submitLink(url) {
    var authKey = await getAuthKey(); // ← Gets potentially poisoned token

    let data = {
        url: url,
        auth_key: authKey // ← Sent to developer's backend
    };

    var result = await fetch(`${BASE_URL}/api/submit`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
        }
    });
    // Response is not sent back to attacker
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While the whitelisted website (https://vault.factcheckinsights.org/*) can send messages via onMessageExternal to poison the authToken in storage.sync, there is no retrieval path for the attacker to access the poisoned value. The stored token is only used internally by the extension to authenticate with the developer's backend (https://vault.factcheckinsights.org/api/submit). According to the methodology: (1) Storage poisoning alone is NOT a vulnerability - the attacker must be able to retrieve the poisoned data back via sendResponse, postMessage, or trigger a read operation that sends data to attacker-controlled destination, (2) Data sent to hardcoded backend URLs is trusted infrastructure, not attacker-accessible. The poisoned token goes to the developer's own backend, not to an attacker-controlled URL. The attacker cannot observe or retrieve the stored value to complete the exploitation chain.

---
