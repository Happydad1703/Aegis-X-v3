54_Regime_Backtest_and_Calibration_Spec.md (v1.0)

이제 Regime Backtest & Calibration System을 설계·구현합니다.
목표는 Regime Engine의 수학적 정합성·안정성·예측력을 과거 데이터로 검증하고, bounded update로만 보정하는 것입니다.

1️⃣ 목표
	과거 N년 데이터로 Regime Engine 재현
	Regime → Allocation → Fleet → 가상수익률 시뮬레이션
	성과지표 산출(Sharpe, MDD, Hit Rate 등)
	파라미터 bounded calibration(±10%)
	결과를 DB에 기록(재현 가능성 확보)
Backtest도 반드시 DB-first 원칙.
________________________________________
2️⃣ 데이터 소스(Backtest 입력)
	macro_context (FRED/ECOS/DART 과거값)
	ext_event_raw (뉴스 카운트/감성 proxy)
	engine_result (market_proxy: 지수 수익률/변동성 proxy 저장)
	과거 시세(최소 일봉 close; engine_result에 저장 권장)
추가 테이블 (권장)
CREATE TABLE market_daily (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    trade_date DATE,
    close_price NUMERIC,
    return_pct NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_market_daily_symbol_date
ON market_daily(symbol, trade_date DESC);
________________________________________
3️⃣ Backtest Engine 구조
Backtest Runner
   ├─ Load Historical Features (DB)
   ├─ Regime Compute (t)
   ├─ Allocation Compute (t)
   ├─ Fleet Budget (t)
   ├─ Simulated PnL (t+1)
   ├─ Portfolio Curve Update
   └─ Metrics Aggregation
________________________________________
4️⃣ 시뮬레이션 가정(MVP)
	Battlefield = KOSPI proxy
	Return_t+1 = market_daily.return_pct
	Allocation weight에 따라 포트폴리오 수익 계산
PortfolioReturn_t=Σ(W_b (t)×Return_b (t+1))

________________________________________
5️⃣ 핵심 지표
	CAGR
	Max Drawdown
	Sharpe Ratio (rf≈0 가정)
	Regime Accuracy (상승장에 Goldilocks 비율 등)
	Crisis Recall (하락 구간에서 Crisis 탐지율)
________________________________________
6️⃣ 구현 스켈레톤
6.1 workers/regime_backtest_engine.py
from sqlalchemy import text
import math

def run_regime_backtest(db, symbol="KOSPI", start_date=None, end_date=None):

    q = text("""
        SELECT trade_date, return_pct
        FROM market_daily
        WHERE symbol = :s
        ORDER BY trade_date ASC
    """)

    rows = db.execute(q, {"s": symbol}).fetchall()

    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    returns = []

    for i in range(len(rows)-1):
        ret_next = float(rows[i+1][1] or 0)

        # 1) regime 계산 (과거 데이터 기반 stub)
        regime_score = 0.5  # TODO: 실제 과거 피처 사용
        weight = 0.7 if regime_score > 0 else 0.3

        portfolio_ret = weight * ret_next
        equity *= (1 + portfolio_ret)
        returns.append(portfolio_ret)

        peak = max(peak, equity)
        dd = (equity - peak) / peak
        max_dd = min(max_dd, dd)

    sharpe = compute_sharpe(returns)
    cagr = equity ** (252/len(returns)) - 1 if returns else 0

    return {
        "final_equity": round(equity, 4),
        "cagr": round(cagr, 4),
        "max_drawdown": round(max_dd, 4),
        "sharpe": round(sharpe, 4),
        "total_days": len(returns)
    }


def compute_sharpe(returns):
    if not returns:
        return 0
    mean = sum(returns)/len(returns)
    std = math.sqrt(sum((r-mean)**2 for r in returns)/len(returns))
    if std == 0:
        return 0
    return (mean/std) * math.sqrt(252)
________________________________________
7️⃣ Calibration Engine
목적
	Regime 가중치(Trend/Vol/Macro 비율)
	Crisis threshold
	Allocation α, β
을 ±10% 범위 내 자동 탐색.
________________________________________
7.1 bounded grid search
def bounded_calibration(base_params, performance_fn, delta=0.1):

    best_score = -999
    best_params = base_params

    for k in base_params:
        for sign in [-1, 1]:
            trial = base_params.copy()
            trial[k] *= (1 + sign*delta)

            score = performance_fn(trial)

            if score > best_score:
                best_score = score
                best_params = trial

    return best_params, best_score
delta는 0.05~0.10 권장.
________________________________________
8️⃣ DB 기록
CREATE TABLE regime_backtest_result (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    cagr NUMERIC,
    max_drawdown NUMERIC,
    sharpe NUMERIC,
    params JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
Backtest 실행 시 반드시 기록.
________________________________________
9️⃣ Warroom Backtest Panel
표시 항목:
	Equity Curve
	CAGR / MDD / Sharpe
	Regime Confusion Matrix
	Calibration History
________________________________________
🔥 운영 원칙
	Backtest는 BACKTEST Mode에서만 실행
	실시간 엔진과 분리 프로세스 권장
	결과가 FULL_LIVE 파라미터를 자동 변경하지 않음
	변경은 bounded + 승인 필요
________________________________________
 
