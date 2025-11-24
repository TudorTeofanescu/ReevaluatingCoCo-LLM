# CoCo Analysis: cafckninonjkogajnihihlnnimmkndgf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all same pattern)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cafckninonjkogajnihihlnnimmkndgf/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1148	var link = req.responseText.replace(/[\n\r]/g, '');
Line 1150	link = link.replace(/\|\|\|\|\|(\d+).*$/, '');

Line 1081	var response = req.responseText.replace(/[\n\r\s]/g, '').replace(/\.href/g, '');
Line 1084	var link2 = response.replace(/^.*?location\=[\'\"]([^\'\"]+).*$/, "$1");
Line 1091	var link2 = response.replace(/^.*?metahttp\-equiv\=\"refresh\"content\=\"\d+\;URL\=([^\">]+).*$/i, "$1");

**Code:**

```javascript
// Background script - bg.js Lines 1143-1167
// Called from chrome.webRequest.onCompleted listener (Line 1125)
var req = new XMLHttpRequest();
req.timeout = 10000;
req.onreadystatechange = function () {
  if (req.readyState == 4) {
    if (req.status == 200) {
      var link = req.responseText.replace(/[\n\r]/g, '');  // Response from hardcoded backend
      var dtime = link.replace(/^.*\|\|\|\|\|(\d+).*$/, '$1');
      link = link.replace(/\|\|\|\|\|(\d+).*$/, '');
      if (/^https?\:\/\//.test(link) && (link != doc_url)) {
        var domain = doc_url.replace(/^https?\:\/\/([^\/]+).*$/, '$1');
        if (/^\d+$/.test(dtime)) {
          ttlz.statistics.used_domains[doc_domain] = parseInt(dtime);
        }
        ttlz.statistics.success(link, domain);  // Follows redirects from backend response
      } else {
        ttlz.statistics.used_domains[doc_domain] = statistics_time*2;
      }
    }
  }
};
//-----------------------------------------------------------------------
req.open("POST", 'https://stat.totallzero.com/stat.html', true);  // Hardcoded backend URL
req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
req.send('addon=' + ttlz.statistics.name + '&url=' + encodeURIComponent(doc_url) + '&x_frame=checkserver2&x_time=' + statistics_time);

// ttlz.statistics.success then makes more XHR requests (Lines 1072-1103)
ttlz.statistics.success2 = function(link, domain) {
  var req = new XMLHttpRequest();
  req.timeout = 10000;
  req.onreadystatechange = function () {
    if (req.readyState == 4) {
      if (req.status == 200) {
        var response = req.responseText.replace(/[\n\r\s]/g, '').replace(/\.href/g, '');
        var is_ok = false;
        if (response.length < 1000) {
          var link2 = response.replace(/^.*?location\=[\'\"]([^\'\"]+).*$/, "$1");  // Extract redirect URL
          if (/^https?\:\/\//.test(link2)) {
            ttlz.statistics.success2(link2, domain);  // Recursive call with URL from backend response
            is_ok = true;
          }
        }
        if (! is_ok) {
          var link2 = response.replace(/^.*?metahttp\-equiv\=\"refresh\"content\=\"\d+\;URL\=([^\">]+).*$/i, "$1");
          if (/^https?\:\/\//.test(link2)) {
            ttlz.statistics.success2(link2, domain);  // Recursive call
            is_ok = true;
          }
        }
      }
    }
  };
  req.open("GET", link, true);  // Link from backend response
  req.setRequestHeader("ttlz-x-accept", 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8');
  req.send();
}
```

**Classification:** FALSE POSITIVE

**Reason:** All detected flows involve data from the hardcoded backend URL (https://stat.totallzero.com/stat.html) being used in subsequent XMLHttpRequest calls. This is trusted infrastructure - the extension developer controls this backend server. The extension sends statistics data to the backend, receives a response (potentially with redirect URLs), and follows those redirects for statistics tracking purposes. The data from the developer's own backend is not attacker-controlled. No external attacker can trigger this flow or inject malicious URLs. The flow is automatically triggered by chrome.webRequest.onCompleted for main_frame requests, but the actual XHR destinations are determined by responses from the trusted backend server. Compromising the developer's backend infrastructure is a separate issue from extension vulnerabilities.
