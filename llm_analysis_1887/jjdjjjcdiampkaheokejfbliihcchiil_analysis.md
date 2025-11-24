# CoCo Analysis: jjdjjjcdiampkaheokejfbliihcchiil

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jjdjjjcdiampkaheokejfbliihcchiil/opgen_generated_files/bg.js
Line 1021	if (request.skin !== undefined) {

**Code:**

```javascript
// Background script (bg.js) - Line 1048: External message listener registration
chrome.extension.onMessageExternal.addListener(onRequest);

// Line 1020-1030: Message handler
var onRequest = function (request, sender, sendResponse) {
  if (request.skin !== undefined) {  // Line 1021 - CoCo flagged line
    setSkin(request.skin);  // ← attacker-controlled request.skin
  }
  if (processRequest) {
    processRequest.call(API, request, sender, sendResponse);
  }
  if (request.unload) {
    setIcon(DEFAULT_ICON);
  }
};

// Line 1007-1010: setSkin function
var setSkin = function (skin) {
  __skin = ls('skin', skin);  // ← attacker-controlled skin flows to ls()
  updateIcon();
};

// Line 968-976: ls function (localStorage sync)
var ls = function (key, val) {
  if (val === undefined) {
    return localStorage[key];
  } else {
    var obj = {}; obj[key] = val;
    chrome.storage.sync.set(obj);  // ← SINK: attacker data written to chrome.storage.sync
    return localStorage[key] = val;
  }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from any extension

**Attack:**

```javascript
// From a malicious extension or whitelisted website
chrome.runtime.sendMessage(
  'jjdjjjcdiampkaheokejfbliihcchiil',  // Target extension ID
  { skin: 'malicious_value' },  // Attacker-controlled data
  function(response) {
    console.log('Storage poisoned');
  }
);
```

**Impact:** An external attacker (malicious extension or whitelisted website) can write arbitrary attacker-controlled data to chrome.storage.sync by sending a message with a 'skin' field. The extension uses `chrome.extension.onMessageExternal` which allows ANY external extension to send messages (IGNORE manifest restrictions per methodology). The attacker-controlled `request.skin` value flows directly through `setSkin()` → `ls('skin', skin)` → `chrome.storage.sync.set()` without validation. This allows storage poisoning with arbitrary values. While storage poisoning alone is typically insufficient for TRUE POSITIVE classification, in this case the extension also reads this value on line 992 (`__skin = ls('skin')`) and uses it to construct file paths (line 999: `'icons/' + __skin + '/' + icon + '.png'`), which could potentially be exploited for path traversal attacks when the poisoned value is retrieved.
