## Run sploit lottery_2.py

1. Copy oleg-service in new folder `sploited_oleg_service`
2. Enter new folder
3. Replace `main.cpp` with `sploits/sploit 2/main.cpp 
4. Copy `sploit/lottery_2.py` to `sploited_oleg_service`
5. Run `make` to build c++ service in th `build` directory
6. Create systemctl service named `lottery.service` with binary `build/oleg-service`
7. Run `lottery_2.py`
