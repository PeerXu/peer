set mountScript="C:\Users\Public\PeerAgent\mount.bat"
IF EXIST %mountScript% (
   cmd /q /c %mountScript%
)
