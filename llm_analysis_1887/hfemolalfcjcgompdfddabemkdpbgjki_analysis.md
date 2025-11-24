# CoCo Analysis: hfemolalfcjcgompdfddabemkdpbgjki

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hfemolalfcjcgompdfddabemkdpbgjki/opgen_generated_files/cs_0.js
Line 565: `window.addEventListener('message', (e) => {`
Line 566: `commandHandler(e.data.command, e.data.data);`
Line 504: `let index = data[0];`
Line 506: `value[index] = data;`
Line 507: `chrome.storage.sync.set({ 'liveSessions': JSON.stringify(value) });`

**Code:**

```javascript
// Content script (cs_0.js) - Lines 565-567
window.addEventListener('message', (e) => {
    commandHandler(e.data.command, e.data.data);
}, false);

// Handler function - Lines 500-509
case 'editLive':
    // edit an entry of Live Sessions port
    chrome.storage.sync.get(['liveSessions'], (items) => {
        let value = JSON.parse(items.liveSessions);
        let index = data[0];
        data = data[1];
        value[index] = data;
        chrome.storage.sync.set({ 'liveSessions': JSON.stringify(value) });
    });
    break;

// Injected script (home-inject.js) - Lines 161
window.postMessage({ 'command': 'editLive', 'data': [index, data] }, '*');
```

**Classification:** FALSE POSITIVE

**Reason:** This is internal extension communication, not an external attack vector. The extension injects its own script (home-inject.js) into the page via `chrome.runtime.getURL('/js/home-inject.js')` (line 562 of cs_0.js). The injected script uses `window.postMessage` to communicate with the content script, which is a standard pattern for isolated world communication within a single extension. The webpage itself cannot trigger this flow because:
1. The postMessage originates from the extension's own injected script, not from the webpage
2. The extension only runs on specific domains (https://online.manchester.ac.uk/*)
3. This is the extension communicating with itself, not a webpage attacking the extension

Additionally, this is storage poisoning only - there is no retrieval path where an attacker could read the stored data back.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hfemolalfcjcgompdfddabemkdpbgjki/opgen_generated_files/cs_0.js
Line 565: `window.addEventListener('message', (e) => {`
Line 566: `commandHandler(e.data.command, e.data.data);`
Line 505: `data = data[1];`
Line 507: `chrome.storage.sync.set({ 'liveSessions': JSON.stringify(value) });`

**Code:**

Same flow as Sink 1, just tracking a different variable assignment (data[1] instead of data[0]).

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - internal extension communication pattern, not an external attack vector. The postMessage is sent by the extension's own injected script, not by webpage code. Additionally, storage poisoning only with no retrieval path.
