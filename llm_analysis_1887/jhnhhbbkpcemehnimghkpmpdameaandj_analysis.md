# CoCo Analysis: jhnhhbbkpcemehnimghkpmpdameaandj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jhnhhbbkpcemehnimghkpmpdameaandj/opgen_generated_files/cs_0.js
Line 618 window.addEventListener("message", function(event) {
Line 626 let postbackParams = event.data.pbParams;

**Code:**

```javascript
// Content script (only runs on *.searchinchrome.com per manifest)
window.addEventListener("message", function(event) {
    let urlPattern = /.+\.searchinchrome\.com/i;
    if (urlPattern.test(event.origin)) { // ← checks origin is *.searchinchrome.com
        if (event.data.message === "sic_install_attributed" &&
            event.data.extId === constants.extensionId) {
            chrome.storage.sync.set({ "install_attributed": true }, function() {
                console.debug("Install attributed");
            });
            let postbackParams = event.data.pbParams;  // ← attacker-controlled from whitelisted domain
            if (typeof postbackParams === "object" && Object.keys(postbackParams).length > 0) {
                chrome.storage.sync.set({ "pb_params": postbackParams }, function() {  // ← storage sink
                    console.debug(postbackParams);
                });
            }
        }
    }
}, false);

// Background script - retrieves and uses the stored data
getLocalData () {
    chrome.storage.sync.get([
        "alias",
        "install_date",
        "pb_params"
    ], data => {
        if (!data.alias || !data.install_date) {
            this.newUserSetup(this.getLocalData)
            return
        }

        this.alias = data.alias
        this.installDate = data.install_date
        if (data.pb_params) this.pbParams = data.pb_params  // ← retrieves stored data

        chrome.storage.local.get("firstSearch", data => {
            this.firstSearch = typeof data.firstSearch === "undefined" ? true : false
            this.updateDynamicRules()  // ← uses pbParams
        })
    })
}

updateDynamicRules() {
    let source = this.pbParams.source  // ← reads attacker-controlled data
    if (source.indexOf('natural') !== -1) source = 'natural'  // ← sanitizes to 'natural' if contains 'natural'

    const otherConfig = {}
    if (this.firstSearch) {
        otherConfig.scheme = 'chrome-extension'
        otherConfig.host = chrome.runtime.id
        otherConfig.path = '/html/search.html'
    }

    chrome.declarativeNetRequest.updateDynamicRules(
        {
            addRules: [
                {
                    id: 1,
                    action: {
                        type: "redirect",
                        redirect: {
                            transform: {
                                ...otherConfig,
                                queryTransform: {
                                    addOrReplaceParams: Array.from(
                                        new URLSearchParams({
                                            a: this.alias,
                                            jsrc: source,  // ← attacker-controlled source used in URL param
                                            ua: constants.limitedUA,
                                            v: constants.version,
                                        }).entries()
                                    ).map(([key, value]) => ({ key, value })),
                                },
                            },
                        },
                    },
                    condition: {
                        regexFilter: "searchinchrome.com\/search\?.*aid=59.*",  // ← redirects to hardcoded backend
                        resourceTypes: ["main_frame"],
                    },
                },
            ],
            removeRuleIds: [1],
        }
    )
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data is sent TO hardcoded backend domain (searchinchrome.com). The attacker can poison storage with pbParams data, which is later retrieved and used in the jsrc parameter of redirects to the developer's own backend (searchinchrome.com). Per the methodology, sending data to hardcoded developer backend URLs is considered trusted infrastructure. The attacker controls what tracking parameter gets sent to the developer's backend, but this is not exploitable impact - it's just poisoning analytics/tracking data that goes to the developer's own servers. There is no complete storage exploitation chain back to the attacker - the data flows to the developer's backend, not back to the attacker.
