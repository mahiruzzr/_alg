@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ================= 01 identity =================
python lambda_interp.py examples\01-identity.lc
echo ================= 02 bool =================
python lambda_interp.py --prelude examples\prelude.lc examples\02-bool.lc
echo ================= 03 numeral =================
python lambda_interp.py --prelude examples\prelude.lc examples\03-numeral.lc
echo ================= 04 omega (limit 6) =================
python lambda_interp.py examples\04-omega.lc --max-steps 6
echo ================= 04 strategy normal =================
python lambda_interp.py --prelude examples\prelude.lc --strategy normal examples\04-strategy.lc --max-steps 10
echo ================= 04 strategy applicative (diverge) =================
python lambda_interp.py --prelude examples\prelude.lc --strategy applicative examples\04-strategy.lc --max-steps 8
echo ================= 05 factorial (FACT 2) =================
python lambda_interp.py --prelude examples\prelude.lc examples\05-factorial.lc --max-steps 300
echo ================= 06 capture =================
python lambda_interp.py examples\06-capture.lc
echo ================= 07 list =================
python lambda_interp.py --prelude examples\prelude.lc examples\07-list.lc
echo ================= debruijn demo =================
python lambda_interp.py --debruijn -e "(\x.\y.x y) y"
echo ================= tests =================
python -m pytest test_lambda.py -v
pause
