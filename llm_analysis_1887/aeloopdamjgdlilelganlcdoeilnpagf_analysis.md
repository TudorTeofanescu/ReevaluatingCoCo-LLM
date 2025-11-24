# CoCo Analysis: aeloopdamjgdlilelganlcdoeilnpagf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aeloopdamjgdlilelganlcdoeilnpagf/opgen_generated_files/bg.js
Line 985: `chrome.storage.sync.set({ bearerToken: message.token }, () => {`

**Code:**

```javascript
// Background script - External message listener (line 981)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    // to store bearerToken
    if (message.action === "addToken") {
      chrome.storage.sync.set({ bearerToken: message.token }, () => { // ← SINK: storage write
        // ← message.token is attacker-controlled from external message
        if (chrome.runtime.lastError) {
          sendResponse({ status: "Error Setting token" });
        } else {
          sendResponse({ status: "Token received successfully and set" }); // ← only status, not token
        }
      });
    }

    // to remove bearerToken
    if (message.action === "clearToken") {
      chrome.storage.sync.remove("bearerToken", () => {
        if (chrome.runtime.lastError) {
          sendResponse({ status: "Error clearing token" });
        } else {
          sendResponse({ status: "Token cleared successfully" });
        }
      });
    }

    return true; // Indicate async response if needed
  }
);

// Content script - Token retrieval and usage (cs_0.js)
const TOKEN_KEY = "bearerToken";
const SERVER_URL = "https://data.qoruz.com"; // ← hardcoded backend

async function getProfileData(url, token) {
  const response = await fetch(
    `${SERVER_URL}/api/profile.details?url=${url}`, // ← hardcoded backend URL
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`, // ← token sent to hardcoded backend
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    }
  );
  // ... response handling
}

// Token retrieval example
const { bearerToken: chromeToken } = await getChromeStorageSync(TOKEN_KEY);
if (chromeToken) {
  const result = await getProfileData(profileURL, chromeToken); // ← token used with hardcoded backend
}
```

**Manifest permissions:**
```json
{
  "permissions": ["storage", "tabs"],
  "externally_connectable": {
    "matches": ["https://app.qoruz.com/*"] // ← app.qoruz.com can send external messages
  }
}
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages from app.qoruz.com can write arbitrary tokens to chrome.storage.sync, the stored token is only used in fetch() calls to the hardcoded developer backend at "https://data.qoruz.com" (line 689 in cs_0.js, line 499 in getProfileData, line 579 in getUserPlans, line 630 in addProfileToList). Per CRITICAL RULE #3: "Hardcoded backend URLs are still trusted infrastructure" - data TO/FROM developer's own backend servers is FALSE POSITIVE. The attacker sending a malicious token to app.qoruz.com that gets stored and then sent to data.qoruz.com is not an extension vulnerability; it's compromising developer infrastructure which is a separate security concern. The token never flows back to the attacker via sendResponse/postMessage, and is never sent to attacker-controlled URLs.
