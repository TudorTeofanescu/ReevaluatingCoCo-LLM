# CoCo Analysis: lhgjmngaehilhmjhplnkmkficchofcco

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (authToken)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhgjmngaehilhmjhplnkmkficchofcco/opgen_generated_files/bg.js
Line 971: `storeAuthToken(message.data.authToken);`

**Code:**

```javascript
// Background script - External message handler (bg.js Line 967-984)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  console.log('Received external message:', message);
  if (message.action === 'userLoggedIn') {
    console.log('Handling userLoggedIn action');
    storeAuthToken(message.data.authToken); // ← Line 971: attacker-controlled data
    chrome.storage.local.set({ user: message.data.user }, () => {
      chrome.runtime.sendMessage({ action: 'userLoggedIn', data: message.data.user });
    });
    sendResponse({ message: 'User data received and saved successfully!' });
  }
  return true;
});

// Storage function (Line 1079-1081)
function storeAuthToken(token) {
  chrome.storage.local.set({ authToken: token }); // Storage write sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While external domains can send messages and poison storage (authToken and user data), there is no retrieval path back to the attacker. The extension only reads this data to send to its own hardcoded backend (https://getscribix.com/api/auth/renew-token in renewAuthToken function). The stored data flows to trusted infrastructure, not back to the attacker, making this storage poisoning unexploitable.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (user)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhgjmngaehilhmjhplnkmkficchofcco/opgen_generated_files/bg.js
Line 972: `chrome.storage.local.set({ user: message.data.user }, () => {...`

**Code:**

```javascript
// Background script - External message handler (bg.js Line 967-984)
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  console.log('Received external message:', message);
  if (message.action === 'userLoggedIn') {
    console.log('Handling userLoggedIn action');
    storeAuthToken(message.data.authToken);
    chrome.storage.local.set({ user: message.data.user }, () => { // ← Line 972: attacker-controlled data
      chrome.runtime.sendMessage({ action: 'userLoggedIn', data: message.data.user });
    });
    sendResponse({ message: 'User data received and saved successfully!' });
  }
  return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation. While external domains (getscribix.com, localhost:3000) can poison the 'user' storage value via onMessageExternal, there is no path for the attacker to retrieve this poisoned data. The extension only reads storage in internal message handlers (checkAuth action) and sends data to trusted infrastructure. Storage poisoning alone without a retrieval path to the attacker is not exploitable.
