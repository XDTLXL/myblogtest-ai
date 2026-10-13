@echo off
REM ============================================================
REM  Blog login page automation - one click runner
REM
REM  Usage: double click this file, or run:  run-tests.cmd
REM  Any extra arguments are passed to Playwright, e.g.
REM      run-tests.cmd --headed        show the browser window
REM      run-tests.cmd -g "D1"         run only tests matching D1
REM      run-tests.cmd --ui            open interactive UI mode
REM      run-tests.cmd --repeat-each=2 run everything twice
REM ============================================================

cd /d "%~dp0"

REM Locate the Playwright browser cache automatically.
if not defined PLAYWRIGHT_BROWSERS_PATH (
  if exist "%LOCALAPPDATA%\ms-playwright" (
    set "PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\ms-playwright"
  )
)
echo [i] Browsers: %PLAYWRIGHT_BROWSERS_PATH%

REM Check that the system under test is reachable.
echo [i] Checking http://127.0.0.1:9090 ...
curl -s -o nul --max-time 5 http://127.0.0.1:9090/blog_login.html
if errorlevel 1 (
  echo [!] Cannot reach the test environment. Start the blog system first.
  echo.
  pause
  exit /b 1
)
echo [i] Test environment is reachable.

REM Install dependencies on first run.
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
echo  Running tests
echo ============================================================
call npx playwright test %*

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

REM Return the real test result to the caller (CI, scripts, etc).
exit /b %RESULT%
