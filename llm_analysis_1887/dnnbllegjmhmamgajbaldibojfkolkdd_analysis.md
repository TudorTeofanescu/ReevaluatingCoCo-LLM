# CoCo Analysis: dnnbllegjmhmamgajbaldibojfkolkdd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dnnbllegjmhmamgajbaldibojfkolkdd/opgen_generated_files/bg.js
Line 751	    var storage_local_get_source = {
Line 752	        'key': 'value'

**Code:**

```javascript
// Background script (bg.js lines 990-995):
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    if (message.type === "getMutedTwitterAccounts") {
        chrome.storage.local.get("mutedTwitterAccounts", ({ mutedTwitterAccounts }) => {
            sendResponse(mutedTwitterAccounts); // ← sends stored data to external caller
        });
        return true;
    }
    // ... other handlers
});

// Storage is populated from backend:
async function updateMutedTwitterAccounts() {
    const response = await fetch("https://mutebotx.xyz/muted-accounts");
    const mutedTwitterAccounts = await response.json();
    chrome.storage.local.set({ mutedTwitterAccounts }); // ← stores muted accounts
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://x.com/* (or any site if manifest restrictions are ignored):
chrome.runtime.sendMessage(
    'extension-id-here',
    { type: "getMutedTwitterAccounts" },
    (mutedAccounts) => {
        console.log("Retrieved muted accounts:", mutedAccounts);
        // Attacker receives list of muted Twitter accounts
    }
);
```

**Impact:** Information disclosure vulnerability. External websites (specifically https://x.com/* per manifest, but any site can exploit if manifest restrictions are bypassed) can retrieve the complete list of muted Twitter accounts stored by the extension. While the manifest restricts externally_connectable to https://x.com/*, per the methodology, we ignore manifest restrictions and classify this as exploitable.
