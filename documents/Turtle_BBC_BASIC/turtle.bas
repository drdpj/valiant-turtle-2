   10HIMEM=&7A0C
   20PROCmessage
   30PROCmcode:PROCinit 
   40*LOAD"EQUB" 7BB7
   50CHAIN"TRTPROG"
   60END 
   70DEFPROCinit
   80*FX8,6
   90*FX3,5
  100A%=&97:X%=&6E:Y%=&40:CALL &FFF4
  110A%=&97:X%=&6B:Y%=&03:CALL &FFF4
  120*FX3,0
  130ENDPROC
  140DEFPROCmcode
  150OSWRCH=&FFEE
  160OSBYTE=&FFF4 
  170T2CL=&68 
  180T2CH=&69
  190REGINTF=&6D
  200WRITESHEILA=&97
  210RDSHEILA=&96
  220WAITMASK=&20
  230STARTLO=&A8 
  240STARTHI=&61
  250WAVETHRESHOLD=2  
  260ACCTHRESHOLD=19
  270NORMALMODE=&060
  280HALFMODE=&040 
  290WAVEMODE=&000 
  300FOR OPT%=0TO3STEP3
  310P%=HIMEM+1
  320[OPT 0
  330.DRIVER
  340 LDX #&00 \CLEAR INDEX
  350 LDA &0A01,X \GET PENVAL  
  360 STA PEN 
  370 INX
  380 LDA &0A01,X \GET DIST LO    
  390 STA DIST
  400 INX
  410 LDA &0A01,X \GET DIST HI   
  420 STA DIST+1
  430 INX
  440 LDA &0A01,X \GET LEFTDIR    
  450 STA LEFTDIR
  460 INX
  470 LDA &0A01,X \GET RIGHTDIR
  480 STA RIGHTDIR
  490 LDA PEN
  500 ASL A
  510 ASL A
  520 ORA RIGHTDIR
  530 ASL A
  540 ASL A
  550 ORA LEFTDIR
  560 STA INSTRUCTION
  570 LDA DIST
  580 STA INSTRREM
  590 LDA DIST+1
  600 STA INSTRREM+1
  610 LDX #&01
  620 STX INSTRCOUNT  
  630 DEX
  640 STX INSTRCOUNT+1
  650 \
  660 \SEND POWER ON TO MOTORS
  670 \
  680 LDA PEN
  690 ASL A
  700 ASL A
  710 ASL A
  720 ASL A
  730 ORA #&0F
  740 STA OUTBYTE
  750 JSR SENDBYTE
  760 LDX #STARTLO
  770 LDY #STARTHI
  780 JSR SETTIMER 
  790.LOOP
  800 LDA DIST
  810 CMP INSTRCOUNT
  820 LDA DIST+1
  830 SBC INSTRCOUNT+1
  840 BCC GOFINISH
  850 LDA &FF
  860 AND #&80
  870 BEQ NONFINISHED
  880.GOFINISH
  890 JMP FINISHED
  900.NONFINISHED
  910 INC INSTRCOUNT
  920 BNE NOINC1
  930 INC INSTRCOUNT+1
  940.NOINC1
  950 LDA INSTRREM
  960 SEC
  970 SBC #&01
  980 STA INSTRREM
  990 LDA INSTRREM+1
 1000 SBC #&00
 1010 STA INSTRREM+1
 1020 \
 1030 \SET DRIVE TO NORMAL, WAVE OR HALFSTEP
 1040 \
 1050 LDA #WAVETHRESHOLD
 1060 CMP INSTRCOUNT
 1070 LDA #&00
 1080 SBC INSTRCOUNT+1
 1090 BCS NONWAVE
 1100 LDA #WAVETHRESHOLD
 1110 CMP INSTRREM
 1120 LDA #&00
 1130 SBC INSTRREM+1
 1140 BCS NONWAVE
 1150 LDA #WAVEMODE
 1160 JMP SENDIT
 1170.NONWAVE
 1180 LDA #&00
 1190 CMP INSTRREM+1
 1200 BNE NONEQUAL
 1210 LDA #WAVETHRESHOLD
 1220 CMP INSTRREM
 1230 BNE NONEQUAL
 1240 \
 1250 LDA #HALFMODE
 1260 ORA INSTRUCTION 
 1270 STA OUTBYTE  
 1280 JSR WAITTIMER
 1290 JSR SENDBYTE
 1300 JSR FINDDELAY
 1310 TXA
 1320 ASL A
 1330 TAX
 1340 TYA
 1350 ROL A
 1360 TAY
 1370 JSR SETTIMER
 1380.NONEQUAL
 1390 LDA #NORMALMODE
 1400.SENDIT
 1410 ORA INSTRUCTION
 1420 STA OUTBYTE
 1430 JSR WAITTIMER
 1440 JSR SENDBYTE
 1450 JSR FINDDELAY
 1460 JSR SETTIMER
 1470 JMP LOOP
 1480 \
 1490 \FINISHED SENDING LETS STOP
 1500 \
 1510.FINISHED
 1520 LDA PEN
 1530 ASL A
 1540 ASL A
 1550 ASL A
 1560 ASL A
 1570 ORA #&0F
 1580 STA OUTBYTE
 1590 JSR WAITTIMER
 1600 JSR SENDBYTE
 1610 LDX #STARTLO
 1620 LDY #STARTHI
 1630 JSR SETTIMER
 1640 LDA PEN
 1650 ASL A
 1660 ASL A
 1670 ASL A
 1680 ASL A
 1690 STA OUTBYTE
 1700 JSR WAITTIMER
 1710 JSR SENDBYTE
 1720 LDX #STARTHI
 1730 LDY #STARTLO
 1740 JSR SETTIMER
 1750 RTS
 1760 \****************************
 1770 \** SUBROUTINES START HERE **
 1780 \****************************
 1790 \
 1800 \GET APPROPRIATE DELAY VALUE BEFORE  SENDING NEXT BYTE
 1810 \
 1820.FINDDELAY
 1830 LDA #&00
 1840 CMP INSTRCOUNT+1
 1850 BNE NONACC
 1860 LDA #ACCTHRESHOLD
 1870 CMP INSTRCOUNT
 1880 BCC NONACC
 1890 LDA INSTRREM
 1900 CMP INSTRCOUNT 
 1910 LDA INSTRREM+1
 1920 SBC INSTRCOUNT+1
 1930 BCC NONACC
 1940 \
 1950 \TURTLE IS ACCELERATING
 1960 \
 1970 LDA INSTRCOUNT
 1980 SEC
 1990 SBC #&01
 2000 ASL A 
 2010 TAX    
 2020 LDA DELAYTAB,X 
 2030 LDY DELAYTAB+1,X
 2040 TAX
 2050 JMP GOTDELAY
 2060.NONACC
 2070 \
 2080 \TURTLE NOT ACCELERATING
 2090 \
 2100 LDA #&00
 2110 CMP INSTRREM+1
 2120 BNE NONDEC
 2130 LDA #ACCTHRESHOLD
 2140 CMP INSTRREM
 2150 BCC NONDEC
 2160 LDA INSTRREM
 2170 CMP INSTRCOUNT
 2180 LDA INSTRREM+1
 2190 SBC INSTRCOUNT+1
 2200 BCS NONDEC
 2210 \
 2220 \TURTLE IS DECCELERATING
 2230 \
 2240 LDA INSTRREM
 2250 ASL A
 2260 TAX
 2270 LDA DELAYTAB,X
 2280 LDY DELAYTAB+1,X
 2290 TAX
 2300 JMP GOTDELAY
 2310.NONDEC
 2320 \
 2330 \TURTLE IN CONSTANT MOTION
 2340 \
 2350 LDA #ACCTHRESHOLD
 2360 ASL A
 2370 TAX
 2380 LDA DELAYTAB,X
 2390 LDY DELAYTAB+1,X
 2400 TAX
 2410.GOTDELAY
 2420 RTS
 2430.SETTIMER
 2440 \
 2450 \
 2460 \SET CIA TIMER
 2470 \
 2480 \
 2490 TYA
 2500 PHA
 2510 TXA
 2520 TAY
 2530 LDX #T2CL
 2540 LDA #WRITESHEILA
 2550 JSR OSBYTE
 2560 PLA
 2570 TAY
 2580 LDX #T2CH
 2590 LDA #WRITESHEILA
 2600 JSR OSBYTE
 2610 RTS
 2620.WAITTIMER
 2630 \
 2640 \
 2650 \WAIT FOR TIMER TO FINISH
 2660 \
 2670 \
 2680 LDA #RDSHEILA
 2690 LDX #REGINTF 
 2700 JSR OSBYTE
 2710 TYA
 2720 AND #WAITMASK
 2730 BEQ WAITTIMER
 2740 RTS
 2750.SENDBYTE
 2760 \
 2770 \
 2780 \SEND BYTE TO RS423
 2790 \
 2800 \
 2810 LDA OUTBYTE
 2820 JSR OSWRCH
 2830 RTS
 2840.LEFTDIR NOP
 2850.RIGHTDIR NOP
 2860.DIST NOP
 2870 NOP
 2880.INSTRCOUNT NOP
 2890 NOP
 2900.INSTRREM NOP
 2910 NOP
 2920.INSTRUCTION NOP
 2930.OUTBYTE NOP
 2940.PEN NOP
 2950.DELAYTAB
 2960 NOP
 2970 NOP
 2980 NOP
 2990NOP 
 3000NOP 
 3010NOP 
 3020NOP 
 3030NOP
 3040NOP
 3050NOP
 3060NOP
 3070NOP
 3080NOP
 3090NOP
 3100NOP
 3110NOP
 3120NOP
 3130NOP
 3140NOP
 3150NOP
 3160NOP
 3170NOP
 3180NOP
 3190NOP
 3200NOP
 3210NOP 
 3220NOP 
 3230NOP
 3240NOP
 3250NOP 
 3260NOP
 3270NOP
 3280NOP
 3290NOP
 3300NOP
 3310NOP
 3320NOP
 3330NOP
 3340NOP
 3350NOP
 3360 ]
 3370 NEXT OPT%
 3380 ENDPROC
 3390 DEFPROCmessage
 3400 *FX154,11
 3410 CLS
 3420 FOR JOE=2TO3:PRINTTAB(3,JOE);CHR$(141);CHR$(130);"VALIANT TURTLE MOVER PROGRAM":NEXT JOE
 3430 PRINTTAB(5,4);" BBC Microcomputer Version"
 3440 PRINTTAB(4,7);" (C) Valiant Designs Ltd 1984"
 3450 PRINTTAB(14,15);"PLEASE WAIT" 
 3460 ENDPROC

