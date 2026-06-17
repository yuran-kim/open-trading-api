# Samsung Auto Trader

한국투자증권 Open API(KIS Open API)를 활용하여 삼성전자(005930)를 자동으로 거래하는 프로그램이다.

본 프로젝트는 GitHub Codespaces 환경에서 개발되었으며, REST API 기반으로 현재가 조회, 계좌 조회, 주문 실행, 주문 결과 확인 기능을 구현하였다.

---

# 1. 프로젝트 개요

Samsung Auto Trader는 한국투자증권 Open API를 이용하여 삼성전자(005930)를 자동으로 거래하는 프로그램이다.

프로그램은 현재 주가를 지속적으로 조회하며, 기준 가격(reference price)을 중심으로 자동으로 매수·매도 주문을 수행한다.

주요 기능은 다음과 같다.

* OAuth2 기반 토큰 인증
* 현재가 조회
* 계좌 및 보유 종목 조회
* 시장가 매수/매도 주문
* 자동 거래 로직 수행
* KST(한국 표준시) 로그 출력
* API 재시도(Retry) 및 예외 처리

---

# 2. 개발 환경

| 항목             | 내용                        |
| -------------- | ------------------------- |
| Language       | Python 3                  |
| API            | Korea Investment Open API |
| Environment    | GitHub Codespaces         |
| Target Stock   | 삼성전자 (005930)             |
| Trading Type   | 모의투자                      |
| Order Type     | 시장가 주문                    |
| Authentication | OAuth2 Access Token       |

---

# 3. 실행 방법

## 3.1 라이브러리 설치

```bash
pip install -r requirements.txt
```

## 3.2 GitHub Secrets 설정

프로그램은 계좌번호 및 API Key를 환경변수로 관리한다.

필요한 Secrets는 다음과 같다.

```text
GH_ACCOUNT
GH_APPKEY
GH_APPSECRET
```

## 3.3 프로그램 실행

```bash
cd samsung_auto_trader

python main.py
```

---

# 4. 거래 로직

## 최초 실행

프로그램이 처음 실행되면 현재가를 조회한 뒤 시장가로 1주를 매수한다.

예시

```text
현재가 = 335,000원

시장가 매수

reference_price = 335,000
```

매수 이후 해당 가격을 기준가격(reference price)으로 저장한다.

---

## 기준가격 기반 자동 거래

프로그램은 이후 주기적으로 현재가를 조회하며 다음 조건을 확인한다.

### 매도 조건

```text
현재가 >= 기준가격 + 1000원
```

조건이 충족되면 시장가 매도 주문을 실행한다.

예시

```text
기준가격 = 335,000

현재가 = 336,500

→ 시장가 매도
```

---

### 매수 조건

```text
현재가 <= 기준가격 - 1000원
```

조건이 충족되면 시장가 매수 주문을 실행한다.

예시

```text
기준가격 = 335,000

현재가 = 334,000

→ 시장가 매수
```

---

## 기준가격 갱신

매수 또는 매도가 발생하면 현재 가격으로 기준가격을 다시 설정한다.

```text
reference_price = 현재가
```

---

# 5. 프로그램 구조

```text
samsung_auto_trader/

├── main.py
├── config.py
├── auth.py
├── api_client.py
├── market_data.py
├── account.py
├── orders.py
├── trader.py
├── logger.py
├── token_cache.json
├── requirements.txt
└── README.md
```

---

# 6. 파일별 기능 및 함수 설명

## main.py

프로그램의 실행 진입점이다. 인증을 수행한 뒤 API 통신 객체를 만들고, 자동매매 세션을 실행한다.

### `main()`

프로그램 전체 실행 흐름을 관리하는 함수이다.

주요 기능은 다음과 같다.

* `authenticate()`를 호출하여 Access Token을 발급받거나 캐시된 토큰을 재사용한다.
* `GH_APPKEY`, `GH_APPSECRET`, `GH_ACCOUNT` 환경변수를 읽어온다.
* 환경변수가 없을 경우 오류를 발생시켜 프로그램이 잘못 실행되는 것을 방지한다.
* `ApiClient` 객체를 생성한다.
* `TradingSession` 객체를 생성하고 `session.run()`을 실행하여 자동매매 루프를 시작한다.
* 실행 중 예외가 발생하면 로그로 기록한다.

---

## config.py

프로그램 전반에서 사용하는 설정값을 모아둔 파일이다. API 주소, 종목코드, 거래 시간, 주문 설정, TR ID 등을 한 곳에서 관리한다.

### 주요 설정값

### `API_BASE_URL`

한국투자증권 모의투자 API 서버 주소를 저장한다.

```python
API_BASE_URL = "https://openapivts.koreainvestment.com:29443"
```

### `ENV_ACCOUNT_NUMBER`, `ENV_APP_KEY`, `ENV_APP_SECRET`

GitHub Codespaces Secrets에서 읽어올 환경변수 이름을 저장한다.

```python
ENV_ACCOUNT_NUMBER = "GH_ACCOUNT"
ENV_APP_KEY = "GH_APPKEY"
ENV_APP_SECRET = "GH_APPSECRET"
```

### `SYMBOL`

거래 대상 종목코드를 저장한다.

```python
SYMBOL = "005930"
```

삼성전자 종목코드이다.

### `ORDER_PRICE_OFFSET`

기준가격에서 매수·매도 조건을 판단할 가격 차이를 의미한다.

```python
ORDER_PRICE_OFFSET = 1000
```

현재 프로그램에서는 기준가격보다 1000원 이상 오르면 매도, 1000원 이상 내리면 매수 조건으로 사용된다.

### `TRADING_WINDOW_START`, `TRADING_WINDOW_END`

자동매매를 수행할 시간 범위를 설정한다.

```python
TRADING_WINDOW_START = time(hour=9, minute=10)
TRADING_WINDOW_END = time(hour=15, minute=30)
```

### `POLL_INTERVAL_SECONDS`

한 번의 거래 판단이 끝난 뒤 다음 사이클까지 대기하는 시간이다.

```python
POLL_INTERVAL_SECONDS = 180
```

즉 180초마다 현재가와 계좌 상태를 다시 확인한다.

### `REQUEST_TIMEOUT_SECONDS`

API 요청이 일정 시간 이상 응답하지 않을 때 timeout 처리하기 위한 설정값이다.

### `RETRY_MAX`

API 요청 실패 시 최대 재시도 횟수이다.

### `RETRY_BACKOFF_SECONDS`

API 요청 실패 후 재시도하기 전 대기 시간을 계산할 때 사용하는 값이다.

### `DRY_RUN`

실제 주문 요청을 보낼지 여부를 결정한다.

```python
DRY_RUN = True
```

* `True`: 실제 주문을 보내지 않고 로그로만 주문 내용을 출력한다.
* `False`: 한국투자증권 모의투자 API로 실제 모의주문을 전송한다.

### `TR_ID_PRICE`, `TR_ID_BALANCE`, `TR_ID_BUY`, `TR_ID_SELL`

한국투자증권 Open API 요청에 필요한 Transaction ID이다.

* `TR_ID_PRICE`: 현재가 조회
* `TR_ID_BALANCE`: 잔고 조회
* `TR_ID_BUY`: 매수 주문
* `TR_ID_SELL`: 매도 주문

---

## auth.py

한국투자증권 Open API 인증과 Access Token 관리를 담당하는 파일이다. 토큰을 매번 새로 발급하지 않고, 같은 날짜에는 `token_cache.json`에 저장된 토큰을 재사용한다.

### `load_credentials()`

GitHub Codespaces Secrets에 저장된 환경변수를 읽어오는 함수이다.

읽어오는 값은 다음과 같다.

* `GH_ACCOUNT`
* `GH_APPKEY`
* `GH_APPSECRET`

세 값 중 하나라도 없으면 `EnvironmentError`를 발생시켜 프로그램 실행을 중단한다.

### `load_token_cache()`

`token_cache.json` 파일에 저장된 토큰 정보를 읽어오는 함수이다.

주요 기능은 다음과 같다.

* 토큰 캐시 파일이 없으면 빈 딕셔너리를 반환한다.
* 파일이 존재하면 JSON으로 읽어온다.
* 파일이 손상되었거나 읽을 수 없으면 경고 로그를 남기고 새 토큰을 발급받도록 빈 값을 반환한다.

### `save_token_cache(cache)`

새로 발급받은 토큰 정보를 `token_cache.json` 파일에 저장하는 함수이다.

저장되는 정보는 다음과 같다.

* Access Token
* 만료 시간
* 발급 날짜

### `is_token_valid(cache)`

캐시된 토큰이 아직 유효한지 확인하는 함수이다.

확인하는 조건은 다음과 같다.

* 토큰이 존재하는가
* 만료 시간이 존재하는가
* 저장 날짜가 오늘 날짜와 같은가
* 만료 시간이 현재 시간보다 뒤인가

조건을 만족하면 `True`, 그렇지 않으면 `False`를 반환한다.

### `request_token(appkey, appsecret)`

한국투자증권 Open API 서버에 새 Access Token 발급을 요청하는 함수이다.

주요 기능은 다음과 같다.

* `/oauth2/tokenP` endpoint로 POST 요청을 보낸다.
* AppKey와 AppSecret을 이용해 토큰을 발급받는다.
* 요청 실패 시 `RETRY_MAX` 횟수만큼 재시도한다.
* 재시도 사이에는 `RETRY_BACKOFF_SECONDS`를 이용해 점점 더 오래 대기한다.

### `authenticate()`

인증 전체 흐름을 관리하는 함수이다.

동작 순서는 다음과 같다.

1. `load_credentials()`로 AppKey, AppSecret, 계좌번호를 읽어온다.
2. `load_token_cache()`로 기존 토큰이 있는지 확인한다.
3. `is_token_valid()`로 기존 토큰이 유효한지 확인한다.
4. 유효하면 기존 토큰을 재사용한다.
5. 유효하지 않으면 `request_token()`으로 새 토큰을 발급받는다.
6. 새 토큰을 `save_token_cache()`로 저장한다.
7. 최종 Access Token을 반환한다.

---

## api_client.py

한국투자증권 Open API에 GET/POST 요청을 보내는 공통 통신 모듈이다. 인증 헤더를 포함하고, timeout 및 retry 처리를 담당한다.

### `ApiClient.__init__(token, appkey, appsecret)`

API 요청에 필요한 기본 정보를 설정하는 생성자이다.

주요 기능은 다음과 같다.

* Access Token 저장
* AppKey 저장
* AppSecret 저장
* `requests.Session()` 생성
* 모든 요청에 공통으로 사용할 기본 헤더 설정

기본 헤더에는 다음 값이 포함된다.

* Authorization
* appkey
* appsecret
* Content-Type
* Accept

### `ApiClient._request(method, endpoint, params=None, json_data=None, headers=None)`

실제 API 요청을 수행하는 내부 함수이다.

주요 기능은 다음과 같다.

* GET 또는 POST 요청 실행
* query parameter 전달
* JSON body 전달
* TR ID 등 추가 header 전달
* 요청 timeout 처리
* 요청 실패 시 재시도
* 실패한 응답의 status code와 response text를 로그로 출력
* 모든 재시도 실패 시 `RuntimeError` 발생

이 함수는 직접 호출하기보다는 `get()` 또는 `post()`를 통해 사용한다.

### `ApiClient.get(endpoint, params=None, headers=None)`

GET 요청을 보내는 함수이다.

현재 프로그램에서는 주로 다음 작업에 사용된다.

* 현재가 조회
* 계좌 잔고 조회

### `ApiClient.post(endpoint, json_data=None, headers=None)`

POST 요청을 보내는 함수이다.

현재 프로그램에서는 주로 다음 작업에 사용된다.

* 매수 주문
* 매도 주문

---

## market_data.py

삼성전자 현재가를 조회하는 파일이다.

### `parse_price_response(response)`

한국투자증권 현재가 조회 API 응답에서 현재가를 추출하는 함수이다.

주요 기능은 다음과 같다.

* 응답 데이터의 `output` 영역을 확인한다.
* `stck_prpr` 필드에서 현재가를 가져온다.
* 문자열 형태의 현재가를 정수형으로 변환한다.
* 응답 구조가 예상과 다르면 오류 로그를 출력하고 `None`을 반환한다.

### `get_current_price(api_client)`

삼성전자 현재가를 조회하는 함수이다.

주요 기능은 다음과 같다.

* 현재가 조회 API endpoint로 GET 요청을 보낸다.
* 종목코드 `005930`을 요청 파라미터로 전달한다.
* `TR_ID_PRICE`를 header에 포함한다.
* `parse_price_response()`를 이용하여 현재가를 정수형으로 변환한다.
* 조회한 현재가를 로그에 출력한다.
* 현재가를 반환한다.

---

## account.py

계좌 예수금과 보유 종목 정보를 조회하는 파일이다.

### `parse_account_response(response)`

잔고조회 API 응답을 프로그램에서 사용하기 쉬운 형태로 정리하는 함수이다.

주요 기능은 다음과 같다.

* `output2`에서 예수금 정보를 추출한다.
* `dnca_tot_amt` 값을 읽어 사용 가능한 현금으로 저장한다.
* `output1`에서 보유 종목 목록을 추출한다.
* 각 보유 종목의 종목코드와 보유수량을 정리한다.
* 최종적으로 `available_cash`와 `holdings`를 포함한 딕셔너리를 반환한다.

반환 예시는 다음과 같다.

```python
{
    "available_cash": 50000000,
    "holdings": [
        {
            "symbol": "005930",
            "quantity": 1,
            "raw": {...}
        }
    ]
}
```

### `get_account_summary(api_client, account_number)`

계좌 잔고와 보유 종목을 조회하는 함수이다.

주요 기능은 다음과 같다.

* 계좌번호를 `CANO`와 `ACNT_PRDT_CD`로 분리한다.
* 잔고조회 API endpoint로 GET 요청을 보낸다.
* `TR_ID_BALANCE`를 header에 포함한다.
* 응답을 `parse_account_response()`로 정리한다.
* 예수금과 보유 종목 수를 로그로 출력한다.
* 정리된 계좌 정보를 반환한다.

### `get_symbol_holding(summary, symbol=SYMBOL)`

계좌 정보에서 특정 종목의 보유 정보를 찾는 함수이다.

현재 프로그램에서는 삼성전자(005930)의 보유수량을 확인하기 위해 사용한다.

동작 방식은 다음과 같다.

* `summary["holdings"]` 목록을 순회한다.
* 종목코드가 `005930`인 항목을 찾는다.
* 해당 종목이 있으면 보유수량을 반환한다.
* 없으면 수량 0으로 처리한다.

---

## orders.py

시장가 매수·매도 주문을 생성하고 전송하는 파일이다.

### `place_order(api_client, account_number, side, price, quantity=ORDER_QUANTITY)`

매수와 매도 주문을 공통으로 처리하는 함수이다.

주요 기능은 다음과 같다.

* 계좌번호를 `CANO`와 `ACNT_PRDT_CD`로 분리한다.
* 주문 body를 생성한다.
* 시장가 주문을 위해 `ORD_DVSN = "01"`로 설정한다.
* 시장가 주문에서는 주문단가를 `ORD_UNPR = "0"`으로 설정한다.
* 매수 또는 매도 방향에 따라 `TR_ID_BUY` 또는 `TR_ID_SELL`을 선택한다.
* `DRY_RUN=True`이면 실제 주문을 보내지 않고 mock response를 반환한다.
* `DRY_RUN=False`이면 주문 API endpoint로 POST 요청을 보낸다.
* 주문 응답을 로그로 출력하고 반환한다.

### `place_buy_order(api_client, account_number, price)`

시장가 매수 주문을 실행하는 함수이다.

내부적으로 `place_order()`를 호출하며, 주문 방향을 매수로 지정한다.

### `place_sell_order(api_client, account_number, price)`

시장가 매도 주문을 실행하는 함수이다.

내부적으로 `place_order()`를 호출하며, 주문 방향을 매도로 지정한다.

---

## trader.py

자동매매 전략의 핵심 로직이 담긴 파일이다. 현재가 조회, 기준가격 관리, 매수·매도 조건 판단, 주문 실행을 담당한다.

### `TradingSession.__init__(api_client, account_number)`

자동매매 세션 객체를 초기화하는 생성자이다.

주요 기능은 다음과 같다.

* API Client 저장
* 계좌번호 저장
* 기준가격 `reference_price` 초기화
* 최초 매수 여부 `initial_buy_done` 초기화

### `TradingSession.is_trading_window()`

현재 시간이 거래 가능 시간인지 확인하는 함수이다.

주요 기능은 다음과 같다.

* 현재 시간을 KST 기준으로 가져온다.
* 현재 시간이 `09:10 ~ 15:30` 사이인지 확인한다.
* 거래 가능 시간이면 `True`, 아니면 `False`를 반환한다.

### `TradingSession.run()`

자동매매 루프를 실행하는 함수이다.

동작 흐름은 다음과 같다.

1. 거래 세션 시작 로그 출력
2. 현재 시간이 거래 종료 시간 이후인지 확인
3. 거래 시간이 아니면 거래 시작 시간까지 대기
4. 거래 시간이면 `execute_cycle()` 실행
5. 한 사이클 종료 후 `POLL_INTERVAL_SECONDS`만큼 대기
6. 위 과정을 반복

### `TradingSession.execute_cycle()`

자동매매의 핵심 판단을 수행하는 함수이다.

동작 흐름은 다음과 같다.

1. 삼성전자 현재가 조회
2. 계좌 정보 조회
3. 삼성전자 보유수량 확인
4. 현재가, 보유수량, 기준가격 로그 출력
5. 최초 실행인 경우 시장가 1주 매수
6. 최초 매수 후 현재가를 기준가격으로 저장
7. 이후에는 기준가격과 현재가를 비교
8. 현재가가 기준가격보다 1000원 이상 상승하면 시장가 매도
9. 현재가가 기준가격보다 1000원 이상 하락하면 시장가 매수
10. 매수 또는 매도 후 기준가격을 현재가로 갱신
11. 조건을 만족하지 않으면 거래하지 않고 다음 사이클로 넘어감

### `TradingSession._wait_until(target_time)`

거래 시작 시간이 될 때까지 대기하는 함수이다.

주요 기능은 다음과 같다.

* 현재 시간이 거래 시작 전이면 거래 시작 시간까지 남은 초를 계산한다.
* 계산된 시간만큼 `time.sleep()`으로 대기한다.
* 거래 시간이 이미 지났으면 대기하지 않는다.

---

## logger.py

프로그램 실행 로그를 설정하는 파일이다.

### `KSTFormatter`

로그의 시간을 KST 기준으로 출력하기 위한 사용자 정의 Formatter 클래스이다.

기본 Codespaces 환경은 UTC를 사용할 수 있으므로, `ZoneInfo("Asia/Seoul")`을 사용하여 로그 시간을 한국 시간으로 변환한다.

### `KSTFormatter.formatTime(record, datefmt=None)`

로그 기록 시각을 KST 기준 문자열로 변환하는 함수이다.

출력 예시는 다음과 같다.

```text
2026-06-17 10:25:13 KST
```

### `get_logger(name=None)`

각 파일에서 사용할 logger 객체를 생성하거나 가져오는 함수이다.

주요 기능은 다음과 같다.

* logger 생성
* StreamHandler 설정
* KSTFormatter 적용
* 로그 레벨을 INFO로 설정
* 이미 handler가 있는 경우 중복 추가를 방지

---

# 7. 실행 결과

## (1) 프로그램 시작 및 최초 매수

![Initial Buy](execution_screenshot_1.png)

설명

* 현재가 조회
* 계좌 조회
* 최초 시장가 매수 수행

---

## (2) 최초 매수 완료 및 기준가격 설정

![Buy Success](execution_screenshot_2.png)

설명

* 시장가 매수 성공
* 주문번호 생성
* 기준가격(reference price) 저장

---

## (3) 매도 조건 충족

![Sell Trigger](execution_screenshot_3.png)

설명

* 현재가가 기준가격보다 1000원 이상 상승
* 매도 조건 발생

---

## (4) 시장가 매도 완료

![Sell Success](execution_screenshot_4.png)

설명

* 시장가 매도 성공
* 기준가격 갱신

---

# 8. 구현 과정에서 해결한 문제

## 한국 시간(KST) 출력

GitHub Codespaces는 기본적으로 UTC를 사용한다.

이를 해결하기 위해 Python의 ZoneInfo를 이용하여 모든 로그를 KST 기준으로 출력하도록 수정하였다.

```python
ZoneInfo("Asia/Seoul")
```

---

## 토큰 재사용

프로그램 실행 시마다 인증 요청을 보내지 않도록 token_cache.json 파일을 이용하여 동일 날짜의 토큰을 재사용하도록 구현하였다.

---

## API 예외 처리

한국투자증권 API는 간헐적으로 응답 지연이 발생한다.

이를 해결하기 위해 Retry 및 Backoff 기능을 구현하였다.

```python
RETRY_MAX = 3
RETRY_BACKOFF_SECONDS = 2.0
```

---

# 9. 결론

본 프로젝트에서는 한국투자증권 Open API를 활용하여 삼성전자 자동매매 프로그램을 구현하였다.

현재가 조회, 계좌 조회, 시장가 주문, 토큰 관리, 예외 처리, 기준가격 기반 자동매매 로직을 구현하였으며 실제 모의투자 환경에서 정상적으로 매수 및 매도 주문이 수행되는 것을 확인하였다.

이를 통해 Open API 기반 자동매매 시스템의 기본 구조를 이해하고 구현할 수 있었다.
