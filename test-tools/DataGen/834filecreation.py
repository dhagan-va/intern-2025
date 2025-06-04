import os
import random
from datetime import datetime

random.seed(52)

# Reused vars
ISA05_07 = "ZZ"
ISA06 = "83-1002022"
ISA08 = "841439824"
ISA12 = "00501"
GS08 = "005010X220A1"
ST01 = "834"

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

for interval in range(10):
    with open(file_path, 'w') as f:
        f.write("ISA*00*          ")  # ISA01/ISA02
        f.write("*00*          ")  # ISA03/ISA04
        f.write("*" + ISA05_07)  # ISA05
        f.write("*" + ISA06 + "     ")  # ISA06
        f.write("*" + ISA05_07)  # ISA07
        f.write("*" + ISA08 + "      ")  # ISA08
        f.write("*" + yymmdd)  # ISA09
        f.write("*" + hhmm)  # ISA10
        f.write("*$")  # ISA11
        f.write("*00501")  # ISA12
        f.write("*000000061")  # ISA13
        f.write("*0")  # ISA14
        f.write("*T")  # ISA15
        f.write("*:~\n")  # ISA16
        f.write("GS*BE")  # GS01
        f.write("*" + ISA06)  # GS02
        f.write("*" + ISA08)  # GS03
        f.write("*" + ccyymmdd)  # GS04
        f.write("*" + hhmmssss)  # GS05
        f.write("*61")  # GS06
        f.write("*X")  # GS07
        f.write("*" + GS08)  # GS08

    if interval % 10_000 == 0:
        print(f"Generated: {file_name}")

END_TIME = datetime.now() - now
print("It took: ", end='')
print(END_TIME)
