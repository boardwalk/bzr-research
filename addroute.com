REM We want to route Turbine IP addresses through our Linux box
REM Turbine IP addresses are 74.201.102.0 to 74.201.107.255
REM The best destination/netmask is 74.201.96.00/255.255.240.0
REM Our unix box is at 10.0.1.17
REM Our ethernet interface is 2

ROUTE ADD 74.201.96.0 MASK 255.255.240.0 10.0.1.17 METRIC 50 IF 3
