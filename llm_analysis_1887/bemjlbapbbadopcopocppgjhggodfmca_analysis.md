# CoCo Analysis: bemjlbapbbadopcopocppgjhggodfmca

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (plus 1 chrome_storage_local_clear detection)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bemjlbapbbadopcopocppgjhggodfmca/opgen_generated_files/cs_0.js
Line 511 `event`
Line 515 `event.data`
Line 515 `event.data.token`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bemjlbapbbadopcopocppgjhggodfmca/opgen_generated_files/bg.js
Line 1023 `chrome.storage.local.set({ token: token }, ...)`

**Code:**

```javascript
// Content script (cs_0.js / content.js) - Lines 505-534
const ORIGINS = [
  "https://explaintxt-ca7a4.firebaseapp.com",
  "https://explaintxt.com",
  "https://explaintxt.com/",
];

function handleMessage(event) {
  if (!ORIGINS.includes(event.origin)) {  // Origin whitelist check
    return;
  }
  if (event.data.type === "AUTH_TOKEN" && event.data.token) {
    sendAuthTokenToBackground(event.data.token);  // ← attacker-controlled token
  } else if (event.data.type === "SIGNOUT") {
    chrome.runtime.sendMessage({ action: "SIGNOUT" });
  }
}

function sendAuthTokenToBackground(token) {
  chrome.runtime.sendMessage({ action: "storeToken", token });  // ← forwards to background
}

window.addEventListener("message", handleMessage);

// Background script (bg.js) - Lines 974-981, 1022-1026
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case "storeToken":
      storeToken(message.token);  // ← attacker-controlled token
      break;
    case "SIGNOUT":
      signOut();
      break;
    // ... other cases
  }
});

function storeToken(token) {
  chrome.storage.local.set({ token: token }, () => {
    // console.log("Token stored successfully");
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (content script runs on <all_urls>, listens to messages from whitelisted origins)

**Attack:**

```javascript
// On https://explaintxt.com or https://explaintxt-ca7a4.firebaseapp.com
// (or via XSS on these domains):
window.postMessage({
    type: "AUTH_TOKEN",
    token: "attacker_controlled_malicious_token"
}, "*");

// This stores the attacker's token in chrome.storage.local
```

**Impact:** Storage poisoning vulnerability. While there is an origin whitelist check restricting exploitation to specific domains (explaintxt.com and its Firebase subdomain), per the methodology: "If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE." An attacker who controls or finds XSS on the whitelisted domains can poison the extension's storage with a malicious authentication token. This could be used to:
1. Replace legitimate user tokens with attacker-controlled tokens
2. Potentially hijack user sessions if the stored token is used for authentication
3. Impersonate users in requests made by the extension

The methodology explicitly states to IGNORE manifest.json and origin restrictions - if window.addEventListener("message") exists with a path to a dangerous sink, assume it's exploitable.
