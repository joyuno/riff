# 한국 소상공인·프리랜서 법규 사실 (기준일 2026-10-28)

이 파일은 FRAME에서 한국 사용자이고 돈·개인정보가 걸릴 때만 읽는다. **판단이 아니라
확인 질문의 재료다** — 사용자 상황에 적용되는지는 묻고, 적용 판정이 애매하면 세무사·전문가
확인이 필요하다고 말한다. 숫자는 코드 상수가 아니라 설정값으로 두고 기준일을 남긴다.
기준일에서 6개월 넘게 지났거나 근거가 필요하면 `discovery-research.md` 조사로 재확인한다.

## 세금

| 사실 | 앱에 주는 영향 | 근거 |
|---|---|---|
| 사업자등록 없는 인적용역 프리랜서는 부가세 면세, 사업자가 지급할 때 3.3%(소득세 3%+지방세 0.3%) 원천징수. 3%→2% 인하 개정안 있음(확정 미확인) | 세금 신분부터 묻는다. 부가세 10% 기본값 금지. 세율은 설정값 | [국세청](https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=238925) |
| 간이과세 기준 직전연도 공급대가 1억400만원 미만. 4,800만원 이상 간이과세자는 세금계산서 발급 | 과세유형에 따라 세금계산서 기능 분기 | [국세청 상담](https://call.nts.go.kr/call/qna/selectQnaInfo.do?ctgId=CTG11937&mi=1329) |
| 개인사업자 전자세금계산서 의무: 직전연도 공급가액 8천만원 이상. 발급은 다음 달 10일까지 | 발급 대상이면 기한 알림 | [법령](http://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsId=003666&lsJoLnkSeq=1001064199&print=print) |
| 현금영수증 의무발행업종은 건당 10만원 이상 현금거래 시 요청 없어도 발급 | 업종·결제수단 확인 | [국세청](https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7796) |
| 해외 고객 용역의 영세율(0%)은 국외 제공 또는 외화획득 요건을 갖출 때만 | 해외 고객이라고 자동 0% 금지 | [부가가치세법 §22·§24](https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsId=001571&lsJoLnkSeq=900316816&print=print) |

## 소비자·개인정보·연락

| 사실 | 앱에 주는 영향 | 근거 |
|---|---|---|
| 계약 체결·이행에 필요한 이름·연락처는 동의 없이 수집 가능(개인정보보호법 §15①4). 필요 이상은 수집 금지(§16) | 예약·견적용 수집은 동의창 불필요, 마케팅 이용은 별도 동의 | [법령](https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsId=011357&lsJoLnkSeq=900078940&print=print) |
| 광고성 문자·알림은 명시적 사전 동의(기본값 체크 금지), 21시~8시는 별도 동의(정보통신망법 §50). 예약 확인 같은 정보성 알림은 대상 아님 | 광고 수신 동의 칸 분리(기본 해제), 야간 발송 차단 | [법령](https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsId=000030&lsJoLnkSeq=1000688185&print=print) |
| 온라인 판매 청약철회 7일. 용역 제공이 시작되면 철회 제한, 주문제작은 사전 고지·동의 등 요건 충족 시만 제한(전자상거래법 §17) | 취소·환불 화면에 고지와 동의 기록 | [찾기쉬운 생활법령](https://www.easylaw.go.kr/CSP/CnpClsMain.laf?ccfNo=4&cciNo=1&cnpClsNo=2&csmSeq=835) |
| 외식 노쇼 위약금 상한: 예약기반 음식점 총액의 40%, 일반 20%(2025-12-18 시행), 사전 고지 필수. 분쟁해결기준은 별도 약정 없을 때의 권고 기준. 미용업 기준은 미확인 | 위약금 규칙은 사용자 약관값으로, 고지 문구 함께 | [정책브리핑](https://www.korea.kr/news/policyNewsView.do?newsId=148956738) · [소비자원](https://www.kca.go.kr/odr/cm/in/rsltnCrtral.do) |
| 전자 형태라는 이유만으로 전자서명 효력을 부인할 수 없음(전자서명법 §3) | 견적 승인은 클릭으로 가능 — 승인 시각·승인자 기록 보관 | [법령](https://www.law.go.kr/LSW/lsSideInfoP.do?docCls=jo&joBrNo=00&joNo=0003&lsiSeq=236201&urlMode=lsScJoRltInfoR) |
