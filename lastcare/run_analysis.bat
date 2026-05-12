@echo off

cd /d D:\@project AI test4_29_26\v6_analyzer_code

echo ==============================
echo RUN ANALYSIS ALL
echo ==============================

echo.
echo [1] v1_overview
python analysis\v1_overview.py

echo.
echo [2] v2_trend_zone
python analysis\v2_trend_zone.py

echo.
echo [3] v3_mtf
python analysis\v3_mtf.py

echo.
echo [4] v4_score
python analysis\v4_score.py

echo.
echo [5] v5_behavior
python analysis\v5_behavior.py

echo.
echo [6] v6_coin
python analysis\v6_coin.py

echo.
echo ==============================
echo DONE
pause