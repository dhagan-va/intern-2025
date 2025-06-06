import os
import random
from datetime import datetime
from faker import Faker
import uuid
from collections import Counter

# Seeds and Initialization
fake = Faker()
Faker.seed(49245)
random.seed(52)
counts = Counter()

ISA05_07 = "ZZ"
ISA06 = "83-1002022"
ISA08 = "841439824"
AMT_CODES = ['D2', 'FK', 'R', 'C1', 'P3', 'B9']
INS02_VALUES = ['18', '19', '25', '26', '01', 'G8', 'null']

# 1. determine which distribution of tests to do (high-low error prob)
# 2. randomize error dist (if there is one error on a file, it cant have another error)
# 3. Set number of tests
# 4. Track Personal info based on Sponsor ID, each key will have a value of 

# add a test distribution (< .5% for missing value, format error, invalid value; < 1% for negative value)
# Correct/Wrong test distributions
test_dist = [85/15, 90/10, 92/8, 95/5, 98/2]
# Tests need to have a Binom dist for number of beneficiaries (need to make another py to make this happen)
# 80% of 100,000 people have at least 1 beneficiary; ~31008 ppl are sponsors
# INS02 value distribution, this means that 18 needs to be created before rest of them are created
weights = [0.8] + [0.2 / (len(INS02_VALUES) - 1)] * (len(INS02_VALUES) - 1)

# Date vars
now = datetime.now()
ISA13 = now.strftime("%Y%m%d1")
ccyymmdd = now.strftime("%Y%m%d")
yymmdd = now.strftime("%y%m%d")
hhmm = now.strftime("%H%M")
hhmmss = now.strftime("%H%M%S")

# Create new file directory for tests if not there before
file_directory = '834Test_Files'
if not os.path.exists(file_directory):
    os.mkdir(file_directory)
    print(f"New file directory created called: {file_directory}")

edi_name = f"834.VFMP.{now.year}.{yymmdd}.{hhmm}.{ISA13}.edi"
edi_path = os.path.join(file_directory, edi_name)

f = open(edi_path, "w")

ISA = (f"ISA*00*          *00*          *{ISA05_07}*{ISA06:<15}*{ISA05_07}*{ISA08:<15}*{yymmdd}*{hhmm}*$*00501"
       f"*{ISA13}*0*T*:~\n")
GS = f"GS*BE*{ISA06}*{ISA08}*{ccyymmdd}*{hhmmss}*61*X*005010X220A1~\n"
f.write(ISA)
f.write(GS)

# number of tests
n = 1


def getIns02():
    return random.choices(INS02_VALUES, weights=weights, k=1)[0]


def getFid():
    return random.randint(100_000_000, 999_999_999)


def getPolicyID2():
    return random.randint(10_000_000, 99_999_999)


for interval in range(1, n + 1):
    amt_segments = []
    segment_count = 0
    # half the time has second address
    n302 = f"{fake.secondary_address().replace(".", "")}" if random.random() < 0.5 else ""
    ins02 = getIns02()
    counts[ins02] += 1

    # INS02 null, 01, 18, 19, 25, 26, G8
    # INS08 always null, AC, TE
    segments = [f"ST*834*{interval:04}~\n",
                f"BGN*00*{uuid.uuid4().hex.upper()}*{ccyymmdd}*{hhmmss}*UT***2~\n",
                f"N1*P5*{fake.company()}*FI*{getFid()}~\n",
                f"N1*IN*{fake.company()}*FI*{getFid()}~\n",
                f"INS*Y*{getIns02()}*001**A***AC~\n",
                f"REF*0F*1111111111V{getPolicyID2()}~\n",
                f"REF*6O*1111111111V{getPolicyID2()}~\n",
                f"NM1*IL*1*{fake.last_name().upper()}*{fake.first_name().upper()}*{fake.first_name().upper()}***34*{fake.ssn()}~\n",
                f"PER*IP**TE*{fake.basic_phone_number()}~\n",
                f"N3*{fake.building_number()} {fake.street_name()}*{n302}~\n",
                f"N4*{fake.city().upper()}*{fake.state_abbr().upper()}*{fake.zipcode()}~\n"
                ]
    # add AMT values
    for code in AMT_CODES:
        # if AMT = D2, FK, R ($)
        value = random.randint(0, 9)
        if value == 0:
            continue
        amt_segments.append(f"AMT*{code}*{value}~\n")
    segments += amt_segments
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

# Lookup sponsor ID instead of SSN
# keep track of sponsor ID, first, middle, last name, address, SSN, beneficiary ID, phone [hashtable/dict]

f.close()
# display amount of time it takes to create
END_TIME = datetime.now() - now
print("It took: ", end='')
print(END_TIME)

print("The distribution of INS02 is as follows: ")
for k, v in counts.items():
    print(f"{k}: {v}")
