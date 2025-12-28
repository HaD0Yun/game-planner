@echo off
REM Game Planner - Global OpenCode Installation Script (Windows)
REM This script installs game-planner commands and agents to your global OpenCode config

setlocal EnableDelayedExpansion

echo ================================
echo   Game Planner Installer
echo ================================
echo.

REM Determine OpenCode config directory
REM Priority: %USERPROFILE%\.opencode > %USERPROFILE%\.config\opencode
set "OPENCODE_DIR="

if exist "%USERPROFILE%\.opencode" (
    set "OPENCODE_DIR=%USERPROFILE%\.opencode"
) else if exist "%USERPROFILE%\.config\opencode" (
    set "OPENCODE_DIR=%USERPROFILE%\.config\opencode"
) else (
    REM Create default location
    set "OPENCODE_DIR=%USERPROFILE%\.opencode"
)

echo Target directory: %OPENCODE_DIR%

REM Get script directory (where game-planner is located)
set "SCRIPT_DIR=%~dp0"

REM Source files
set "AGENT_DIR=%SCRIPT_DIR%.opencode\agent"
set "COMMAND_DIR=%SCRIPT_DIR%.opencode\command"

REM Check source files exist
if not exist "%AGENT_DIR%\game-designer.yaml" (
    echo Error: game-designer.yaml not found at %AGENT_DIR%
    exit /b 1
)

if not exist "%AGENT_DIR%\game-reviewer.yaml" (
    echo Error: game-reviewer.yaml not found at %AGENT_DIR%
    exit /b 1
)

if not exist "%COMMAND_DIR%\GamePlan.md" (
    echo Error: GamePlan.md not found at %COMMAND_DIR%
    exit /b 1
)

REM Create target directories if they don't exist
if not exist "%OPENCODE_DIR%\agent" mkdir "%OPENCODE_DIR%\agent"
if not exist "%OPENCODE_DIR%\command" mkdir "%OPENCODE_DIR%\command"

REM Backup and install agent files
echo.
echo Installing agent configurations...

if exist "%OPENCODE_DIR%\agent\game-designer.yaml" (
    echo   Backing up existing game-designer.yaml...
    copy /Y "%OPENCODE_DIR%\agent\game-designer.yaml" "%OPENCODE_DIR%\agent\game-designer.yaml.backup" >nul
)
copy /Y "%AGENT_DIR%\game-designer.yaml" "%OPENCODE_DIR%\agent\" >nul
echo   [OK] game-designer.yaml

if exist "%OPENCODE_DIR%\agent\game-reviewer.yaml" (
    echo   Backing up existing game-reviewer.yaml...
    copy /Y "%OPENCODE_DIR%\agent\game-reviewer.yaml" "%OPENCODE_DIR%\agent\game-reviewer.yaml.backup" >nul
)
copy /Y "%AGENT_DIR%\game-reviewer.yaml" "%OPENCODE_DIR%\agent\" >nul
echo   [OK] game-reviewer.yaml

REM Install command file
echo.
echo Installing slash command...

if exist "%OPENCODE_DIR%\command\GamePlan.md" (
    echo   Backing up existing GamePlan.md...
    copy /Y "%OPENCODE_DIR%\command\GamePlan.md" "%OPENCODE_DIR%\command\GamePlan.md.backup" >nul
)
copy /Y "%COMMAND_DIR%\GamePlan.md" "%OPENCODE_DIR%\command\" >nul
echo   [OK] GamePlan.md (/GamePlan command)

REM Verify installation
echo.
echo Verifying installation...

set "VERIFY_SUCCESS=1"

if exist "%OPENCODE_DIR%\agent\game-designer.yaml" (
    echo   [OK] game-designer agent
) else (
    echo   [FAIL] game-designer agent
    set "VERIFY_SUCCESS=0"
)

if exist "%OPENCODE_DIR%\agent\game-reviewer.yaml" (
    echo   [OK] game-reviewer agent
) else (
    echo   [FAIL] game-reviewer agent
    set "VERIFY_SUCCESS=0"
)

if exist "%OPENCODE_DIR%\command\GamePlan.md" (
    echo   [OK] /GamePlan command
) else (
    echo   [FAIL] /GamePlan command
    set "VERIFY_SUCCESS=0"
)

echo.
if "%VERIFY_SUCCESS%"=="1" (
    echo ================================
    echo   Installation Complete!
    echo ================================
    echo.
    echo You can now use the /GamePlan command in OpenCode:
    echo.
    echo   opencode -c                   # Start OpenCode
    echo   /GamePlan zombie roguelike    # Generate GDD
    echo.
    echo Files installed to: %OPENCODE_DIR%
) else (
    echo ================================
    echo   Installation Failed!
    echo ================================
    echo.
    echo Please check the error messages above and try again.
    exit /b 1
)

endlocal
