# CoCo Analysis: biojpligokehpgapnjhiicniepfeedhf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (chrome_storage_local_set_sink with multiple repeated detections)

---

## Sink: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/biojpligokehpgapnjhiicniepfeedhf/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 2130: var data = JSON.parse(response);

Note: Line 332 is in CoCo framework code (before the 3rd "// original" marker at line 963). The actual extension code flow is analyzed below.

**Code:**

```javascript
// Background - XMLHttpRequest to hardcoded government API (bg.js line 2088)
var request = new XMLHttpRequest();
var url = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMinuDustFrcstDspth"; // ← hardcoded Korean government API

var queryParams = "?ServiceKey=" + "QTzJ%2B%2FuQfP7snvTvTbqdqN68%2BXGRmzFUTBThr%2B%2BS4zsmPemgvRQ763sixylmLQIoCank5CvO0nJ3yxP00MmfaA%3D%3D";
queryParams += "&searchDate=" + dataTime;
queryParams += "&informCode=" + "pm10";
queryParams += "&_returnType=" + "json";

request.open("GET", url + queryParams, true);
request.onload = function () {
    if (request.status == 200) {
        parseAKForecastData(request.responseText); // ← data from hardcoded trusted API
    }
};
request.send(null);

// Parse response from hardcoded government API
function parseAKForecastData(response) {
    var data = JSON.parse(response); // ← CoCo detected this line (2130)

    // ... processing logic for air quality forecast data ...

    var todayOverall = pickOverall(data.list, getToday(), moment);
    var tomorrowOverall = pickOverall(data.list, getTomorrow(), moment);
    var dayAfterTomorrowOverall = pickOverall(data.list, getDayAfterTomorrow(), moment);

    // ... more processing ...

    setAKOveralls(todayOverall, tomorrowOverall, dayAfterTomorrowOverall, moment, getCurrentHour());
}

// Store air quality forecast data in storage
function setAKOveralls(todayOverall, tomorrowOverall, dayAfterTomorrowOverall, moment, currentHour) {
    chrome.storage.local.set({
        'ak_overall_today': todayOverall,  // ← data from trusted government API
        'ak_overall_tomorrow': tomorrowOverall,
        'ak_overall_dayAfterTomorrow': dayAfterTomorrowOverall,
        'ak_forecastedTime': moment,
        'ak_call_time': currentHour
    }, function() {
        console.log('예보정보를 스토리지에 저장합니다.');
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** The data flow is from a hardcoded trusted backend URL (Korean government air quality API: `http://openapi.airkorea.or.kr/`). Per the analysis methodology: "Hardcoded backend URLs are still trusted infrastructure - Data TO/FROM developer's own backend servers = FALSE POSITIVE." The extension is a weather/air quality app that fetches forecast data from the official Korean Air Quality API and stores it for display. There is no external attacker trigger (no message listeners, no external connections). The flow runs automatically on window.onload to fetch legitimate air quality data. Compromising the government API infrastructure is a separate issue from extension vulnerabilities.

---

## Notes

- CoCo detected Line 332 which is in the framework code (before line 963, the third "// original" marker)
- The actual extension code (after line 963) uses XMLHttpRequest to fetch data from hardcoded trusted API
- Extension name translates to "Show Me The Dust (Fine Dust and Weather)" - Korean air quality monitoring app
- No external message listeners or connection handlers exist in the extension code
- All XMLHttpRequest calls are to hardcoded trusted URLs:
  - `http://apis.skplanetx.com/weather/*` (SK Planet weather API)
  - `http://openapi.airkorea.or.kr/*` (Korean Air Quality API)
  - `https://apis.daum.net/local/*` (Daum location API)
- Extension permissions only include access to these specific hardcoded APIs
- The storage.set operations store legitimate air quality and weather data for user display
