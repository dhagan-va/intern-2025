import os
import random
from datetime import datetime

random.seed(52)

# Reused vars
ISA05_07 = "ZZ"
ISA06 = "83-1002022"
ISA08 = "841439824"

now = datetime.now()
isa13 = now.strftime("%Y%m%d1")
ccyymmdd = now.strftime("%Y%m%d")
yymmdd = now.strftime("%y%m%d")
hhmm = now.strftime("%H%M")
hhmmssss = f"{hhmm}{now.second}{int(now.microsecond / 10_000):02}"

file_directory = '834Test_Files'
if not os.path.exists(file_directory):
    os.mkdir(file_directory)
    print("New file directory created for: 834 EDI files")

file_name = f"834.VFMP.{now.year}.{yymmdd}.{hhmm}.{isa13}.edi"
file_path = os.path.join(file_directory, file_name)

f = open(file_path, "w")

ISA = (f"ISA*00*          *00*          *{ISA05_07}*{ISA06:<15}*{ISA05_07}*{ISA08:<15}"
       f"*{yymmdd}*{hhmm}*$*00501*000000061*0*T*:~\n")
GS = f"GS*BE*{ISA06}*{ISA08}*{ccyymmdd}*{hhmmssss}*61*X*005010X220A1~\n"
f.write(ISA)
f.write(GS)

for interval in range(1):
    ST = f"ST*834*{interval:04}~\n"
    message = """\
BGN*00*0D0AACD687DA4FDEA7B90769916E6B06*20210427*203926*MT***2~
N1*P5*OCC*FI*123456678~
N1*IN*XX*FI*123356678~
INS*Y*18*001**A***AC~
REF*0F*0032938645V20940530~
REF*6O*0048933446V10367343~
NM1*IL*1*BLACK*DEBORAH*AMANDA***34*900823589~
PER*IP**TE*6735697183~
N3*4898 PINE BLVD*APARTMENT 6381~
N4*ARLINGTON*GA*12956~
AMT*D2*4~
AMT*FK*0~
AMT*R*7~
AMT*C1*6~
AMT*P3*3~
AMT*B9*5~
HD*001**MM*MCVA1003~
DTP*348*D8*20040726~\n"""
    SE = f"SE*20*{interval:04}\n"

    f.write(ST)
    f.write(message)
    f.write(SE)

    if interval % 10_000 == 0:
        print(f"Generated Message Number {interval}")

GE = f"GE*1*61~\n"
IEA = f"IEA*1*000000061\n"
f.write(GE)
f.write(IEA)

f.close()
END_TIME = datetime.now() - now
print("It took: ", end='')
print(END_TIME)
