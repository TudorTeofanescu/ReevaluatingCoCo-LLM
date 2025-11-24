# CoCo Analysis: eeaoemhlndempejchkcdapgdhfledkcn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eeaoemhlndempejchkcdapgdhfledkcn/opgen_generated_files/bg.js
Line 1057    if (request.jwt) {
Stores request.jwt to chrome.storage.sync
```

**Analysis:**

The vulnerability involves an external message listener that stores attacker data. Examining the background script:

```javascript
// Line 1008-1028 - setToken function stores JWT
function setToken(value) {
  return new Promise((resolve, reject) => {
    chrome.storage.sync.set({ Bearer: value }, function () {  // Line 1011
      if (chrome.runtime.lastError) {
        console.error("Error setting Bearer to " + value);
        resolve(false);
      } else {
        resolve(true);
      }
    })
  })
}

// Line 1052-1076 - External message listener
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    if (request.jwt) {
      setToken(request.jwt)  // ← attacker-controlled JWT stored
        .then(async (res) => {
          if (res) {
            sendResponse({ success: true, message: "Token has been received" })
            openExt("welcome.html")
          }
        })
        .catch((err) => {
          console.log("error setting token", err)
          openExt("error.html")
        })
    } else if (request.removeJWT) {
      removeToken()
    }
    return Promise.resolve("Dummy response to keep the console quiet")
  }
)
```

**Manifest.json externally_connectable:**
```json
"externally_connectable": {
  "matches": [
    "http://in-creator.lightbulb.rs/*",
    "https://app.in-creator.com/*",
    "http://127.0.0.1:8000/*"
  ]
}
```

**Code:**

```javascript
// Entry point - external messages from whitelisted domains
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    if (request.jwt) {
      // Store attacker-controlled JWT in storage
      chrome.storage.sync.set({ Bearer: request.jwt }, function () {
        // Send response but JWT is never retrieved/used
        sendResponse({ success: true, message: "Token has been received" })
      })
    }
  }
)

// getToken function exists but is never called
async function getToken() {
  chrome.storage.sync.get(["Bearer"], function (result) {
    return result.Bearer
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation - storage poisoning without retrieval. While whitelisted domains can send external messages to store a JWT token in chrome.storage.sync, the stored Bearer token is never retrieved or used anywhere in the extension code. The `getToken()` function exists but is never called. According to the methodology, "Storage poisoning alone (storage.set without retrieval) is NOT a vulnerability." For a TRUE POSITIVE, the stored value MUST flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation (fetch to attacker URL, executeScript, etc.). Since the Bearer token is written but never read, there is no exploitable impact.

---
