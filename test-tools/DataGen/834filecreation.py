import os
import random
from datetime import datetime
from faker import Faker
import uuid

random.seed(52)

# Reused vars
ISA05_07 = "ZZ"
ISA06 = "83-1002022"
ISA08 = "841439824"
AMT_CODES = ['D2', 'FK', 'R', 'C1', 'P3', 'B9']

# Date vars
now = datetime.now()
ISA13 = now.strftime("%Y%m%d1")
ccyymmdd = now.strftime("%Y%m%d")
yymmdd = now.strftime("%y%m%d")
hhmm = now.strftime("%H%M")
hhmmss = now.strftime("%H%M%S")

# Faker vars
fake = Faker()
Faker.seed(49245)

# Create new file directory for tests if not there before
file_directory = '834Test_Files'
if not os.path.exists(file_directory):
    os.mkdir(file_directory)
    print("New file directory created for: 834 EDI files")

file_name = f"834.VFMP.{now.year}.{yymmdd}.{hhmm}.{ISA13}.edi"
file_path = os.path.join(file_directory, file_name)

# Write to file
f = open(file_path, "w")

ISA = (f"ISA*00*          *00*          *{ISA05_07}*{ISA06:<15}*{ISA05_07}*{ISA08:<15}*{yymmdd}*{hhmm}*$*00501"
       f"*{ISA13}*0*T*:~\n")
GS = f"GS*BE*{ISA06}*{ISA08}*{ccyymmdd}*{hhmmss}*61*X*005010X220A1~\n"
f.write(ISA)
f.write(GS)

# number of tests
n = 100_000

for interval in range(1, n + 1):
    amt_segments = []
    segment_count = 0
    ssn = fake.ssn()
    phone = fake.basic_phone_number()

    # Lookup uses ID instead of SSN

    # INS01 always yes?
    # INS02 18, 19, 01?
    # INS03 001, 021?
    # INS05 always A?
    # INS08 always AC?
    # can add apartment number for N302
    segments = [f"ST*834*{interval:04}~\n",
                f"BGN*00*{uuid.uuid4().hex.upper()}*{ccyymmdd}*{hhmmss}*UT***2~\n",
                f"N1*P5*{fake.company()}*FI*{random.randint(100_000_000, 999_999_999)}~\n",
                f"N1*IN*{fake.company()}*FI*{random.randint(100_000_000, 999_999_999)}~\n",
                f"INS*Y*18*001**A***AC~\n",
                f"REF*0F*{random.randint(100_000_000, 999_999_999)}V{random.randint(100_000_000, 999_999_999)}~\n",
                f"REF*6O*{random.randint(100_000_000, 999_999_999)}V{random.randint(100_000_000, 999_999_999)}~\n",
                f"NM1*IL*1*{fake.last_name().upper()}*{fake.first_name().upper()}*{fake.first_name().upper()}***34*{ssn.replace("-", "")}~\n",
                f"PER*IP**TE*{phone.replace("-", "")}~\n",
                f"N3*{fake.street_address().upper()}*~\n",
                f"N4*{fake.city().upper()}*{fake.state_abbr().upper()}*{fake.zipcode()}~\n"
                ]
    # add AMT values
    for code in AMT_CODES:
        value = random.randint(0, 9)
        if value == 0:
            continue
        amt_segments.append(f"AMT*{code}*{value}~\n")
    segments += amt_segments
    # is HD03 always MM
    # add rest of  message
    segment_count += len(segments)
    segments += [f"HD*001**MM*MCVA1003~\n",
                 f"DTP*348*D8*{ccyymmdd}~\n",
                 f"SE*{segment_count + 3}*{interval:04}~\n"
                 ]

    f.writelines(segments)

    if interval % 10_000 == 0:
        print(f"Generated Message Number {interval}")

GE = f"GE*{n}*61~\n"
IEA = f"IEA*1*{ISA13}~"
f.write(GE)
f.write(IEA)

# close out of file
f.close()
# display amount of time it takes to create
END_TIME = datetime.now() - now
print("It took: ", end='')
print(END_TIME)
