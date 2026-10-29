---
type: regex
# 사용자가 문자 얘기를 안 해도, 회원 명단을 다루는 앱이면 가정 공개에 광고성 문자는 수신 동의한 분께만 보낸다는 기본값이 있어야 한다.
pattern: '수신\s?동의|광고성\s?(문자|알림)|마케팅\s?동의'
match: contains
target: last_message
---
