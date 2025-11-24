# CoCo Analysis: dnnjkhphmdlpldfbcmkkklhldgjhdhif

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (multiple duplicate detections of same flow)

---

## Sink: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dnnjkhphmdlpldfbcmkkklhldgjhdhif/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1026	var resp = JSON.parse(xhr.responseText.substring(3))[0];
Line 1028	createIcon(resp["l"], stock, resp["c"].indexOf('-') == -1);

**Code:**

```javascript
// Background script (bg.js lines 1009-1054):
function onTick(){
  chrome.storage.local.get(['clock-index', 'stocks', 'text', 'price'], function(res){
    var index = res['clock-index'];
    var stocks = res['stocks'];
    var stock = stocks[index];

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        try{
          if(stock != "eth"){
            var resp = JSON.parse(xhr.responseText.substring(3))[0]; // ← data from backend
            createIcon(resp["l"], stock, resp["c"].indexOf('-') == -1);
          } else {
            var resp = JSON.parse(xhr.responseText); // ← data from backend
            createIcon(resp["price"]["usd"], "Eth", resp["change"].indexOf('-') == -1);
          }

          chrome.storage.local.set({
              'clock-index': stocks[index + 1] ? index + 1 : 0,
              'price': resp['l'], // ← stores backend response data
              'text': stock
          }, function(){});
        } catch(e) {
          console.error(e);
        }
      }
    };

    // Hardcoded backend URLs:
    if(stock != "eth"){
      xhr.open("GET", "http://finance.google.com/finance/info?client=ig&q=" + stock, true);
    } else {
      xhr.open("GET", "https://coinmarketcap-nexuist.rhcloud.com/api/eth", true);
    }
    xhr.send();
  });
}

onTick(); // Called on extension load
```

**Classification:** FALSE POSITIVE

**Reason:** The extension fetches stock price data from hardcoded backend URLs (finance.google.com and coinmarketcap-nexuist.rhcloud.com), parses the response, and stores it in chrome.storage.local. Per methodology rule: "Hardcoded backend URLs are trusted infrastructure - data FROM hardcoded backend is FALSE POSITIVE. Compromising developer infrastructure is separate from extension vulnerabilities." There is no external attacker trigger - the extension autonomously fetches data from its trusted backends. This is internal extension logic only.
