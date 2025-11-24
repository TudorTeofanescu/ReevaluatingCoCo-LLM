# CoCo Analysis: hddoomkknpncfhdfockmjjeagkbnpmph

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_contextmenu → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hddoomkknpncfhdfockmjjeagkbnpmph/opgen_generated_files/cs_0.js
Line 878    document.addEventListener('contextmenu', function (event) {
Line 883      var targetElement = event.target;
Line 886        const anchorElement = targetElement.closest('a');
Line 888          let base = anchorElement.getAttribute('href')
Line 889          let address = base.replace(/\//g, '')

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hddoomkknpncfhdfockmjjeagkbnpmph/opgen_generated_files/bg.js
Line 1006    fetch(`https://api.solintel.io/token/${adr}/free`, {
```

**Code:**

```javascript
// Content script (cs_0.js Line 878)
document.addEventListener('contextmenu', function (event) {
  event.preventDefault();
  var targetElement = event.target;

  // Only processes images from pump.mypinata domain
  if (targetElement.tagName === 'IMG' && targetElement.src.includes('pump.mypinata')) {
    const anchorElement = targetElement.closest('a');
    if (anchorElement){
      let base = anchorElement.getAttribute('href')  // ← attacker-controlled from DOM
      let address = base.replace(/\//g, '')
      chrome.runtime.sendMessage({ coin: address })  // ← sends to background
      addLoader()
    }
  }
});

// Background script (bg.js Line 1005)
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    let adr = message.coin  // ← attacker-controlled
    fetch(`https://api.solintel.io/token/${adr}/free`, {  // ← hardcoded backend URL
      method: 'GET',
      headers: headers
    })
    .then(response => response.json())
    .then(data => {
      sendData(data)
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is a FALSE POSITIVE because the fetch destination is a hardcoded backend URL (`https://api.solintel.io/`). According to the methodology, data sent TO hardcoded backend URLs is considered trusted infrastructure, not a vulnerability. The extension is designed to query the solintel.io API with token addresses extracted from the page. While the attacker can control which token address is queried, they cannot:
1. Control the destination URL (hardcoded to api.solintel.io)
2. Exfiltrate data to their own server
3. Make privileged cross-origin requests to attacker-controlled destinations

The flow involves sending attacker-controlled data to the developer's trusted backend, which is not considered a vulnerability under the threat model. Compromising the developer's API service would be an infrastructure issue, not an extension vulnerability.
