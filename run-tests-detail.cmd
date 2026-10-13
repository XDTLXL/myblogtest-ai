@echo off
REM ============================================================
REM  Blog DETAIL page automation - one click runner
REM
REM  Usage: double click this file, or run:  run-tests-detail.cmd
REM  Extra arguments are passed to Playwright, e.g.
REM      run-tests-detail.cmd --headed      show the browser window
REM      run-tests-detail.cmd --ui          interactive UI mode
REM      run-tests-detail.cmd -g "F3"       run only the F3 case
REM
REM  NOTE: this page has edit/delete actions. Destructive cases only
REM  operate on test blogs created by the suite itself (title marked
REM  with __E2E_DETAIL__) and are always cleaned up afterwards.
REM ============================================================

cd /d "%~dp0"

if not defined PLAYWRIGHT_BROWSERS_PATH (
  if exist "%LOCALAPPDATA%\ms-playwright" (
    set "PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\ms-playwright"
  )
)
echo [i] Browsers: %PLAYWRIGHT_BROWSERS_PATH%

echo [i] Checking http://127.0.0.1:9090 ...
curl -s -o nul --max-time 5 http://127.0.0.1:9090/blog_detail.html
if errorlevel 1 (
  echo [!] Cannot reach the test environment. Start the blog system first.
  echo.
  pause
  exit /b 1
)
echo [i] Test environment is reachable.

if not exist "node_modules\@playwright\test" (
  echo [i] First run: installing dependencies ...
  call npm install --cache ".npm-cache" --no-audit --no-fund
  if errorlevel 1 (
    echo [!] Dependency install failed.
    pause
    exit /b 1
  )
)

echo.
echo ============================================================
echo  Running blog DETAIL page tests
echo  (destructive cases only touch self-created test blogs,
echo   and always clean up afterwards)
echo ============================================================
REM Use the "detail" project to scope the spec file, so that user
REM arguments such as -g "F3" stay free and are not mistaken for a path.
call npx playwright test --project=detail %*

set "RESULT=%errorlevel%"
echo.
echo ============================================================
if "%RESULT%"=="0" (
  echo  RESULT: all tests passed
) else (
  echo  RESULT: some tests failed ^(exit code %RESULT%^)
)
echo ============================================================
echo  HTML report: npx playwright show-report playwright-report
echo.
exit /b %RESULT%
