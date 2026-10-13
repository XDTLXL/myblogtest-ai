@echo off
REM ============================================================
REM  Blog list page automation - one click runner
REM
REM  Usage: double click this file, or run:  run-tests-list.cmd
REM  Extra arguments are passed to Playwright, e.g.
REM      run-tests-list.cmd --headed      show the browser window
REM      run-tests-list.cmd --ui          interactive UI mode
REM      run-tests-list.cmd -g "F1"       run only the F1 case
REM ============================================================

cd /d "%~dp0"

if not defined PLAYWRIGHT_BROWSERS_PATH (
  if exist "%LOCALAPPDATA%\ms-playwright" (
    set "PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\ms-playwright"
  )
)
echo [i] Browsers: %PLAYWRIGHT_BROWSERS_PATH%

echo [i] Checking http://127.0.0.1:9090 ...
curl -s -o nul --max-time 5 http://127.0.0.1:9090/blog_list.html
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
echo  Running blog LIST page tests
echo ============================================================
REM Use the "list" project to scope the spec file, so that user arguments
REM such as -g "B4" stay free and are not mistaken for a file path.
call npx playwright test --project=list %*

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
