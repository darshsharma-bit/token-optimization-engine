$ErrorActionPreference = "Stop"
Write-Host "Ensuring dependencies are fully installed... This might take a minute." -ForegroundColor Cyan
.\venv\Scripts\python.exe -m pip install websockets requests python-dotenv streamlit uvicorn fastapi pydantic

Write-Host "Dependencies installed! Launching the 4 components in new windows..." -ForegroundColor Green

# Launch Router
Start-Process powershell -ArgumentList "-NoExit -Command `"cd 'c:\zip final'; .\venv\Scripts\Activate.ps1; `$Host.UI.RawUI.WindowTitle = 'ATP Router'; Write-Host 'Starting ATP Router...' -ForegroundColor Cyan; python router.py`""

# Launch Dashboard
Start-Process powershell -ArgumentList "-NoExit -Command `"cd 'c:\zip final'; .\venv\Scripts\Activate.ps1; `$Host.UI.RawUI.WindowTitle = 'ATP Dashboard'; Write-Host 'Starting ATP Dashboard...' -ForegroundColor Cyan; python -m streamlit run dasbord.py`""

# Launch Receiver Agent
Start-Process powershell -ArgumentList "-NoExit -Command `"cd 'c:\zip final'; .\venv\Scripts\Activate.ps1; `$Host.UI.RawUI.WindowTitle = 'ATP Receiver (Coder)'; Write-Host 'Starting ATP Agent Node...' -ForegroundColor Cyan; python agent_node.py`""

# Launch Sender Agent
Start-Process powershell -ArgumentList "-NoExit -Command `"cd 'c:\zip final'; .\venv\Scripts\Activate.ps1; `$Host.UI.RawUI.WindowTitle = 'ATP Sender (Manager)'; Write-Host 'Starting ATP Agent Node...' -ForegroundColor Cyan; python agent_node.py`""

Write-Host "All processes launched! Please interact with the new terminal windows that just opened." -ForegroundColor Yellow
