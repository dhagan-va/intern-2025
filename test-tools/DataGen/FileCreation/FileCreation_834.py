import os
import random
from faker import Faker
from datetime import datetime
import uuid
from collections import Counter
import logging
import config

logger = logging.getLogger(__name__)


class Make834:
    def __init__(self, faker_seed=config.FAKER_SEED, random_seed=config.RANDOM_SEED, n=1):
        self.time = datetime.now()
        self.fake = Faker()
        Faker.seed(faker_seed)
        random.seed(random_seed)
        self.counts = Counter()
        self.n = n

        self.ISA05_07 = "ZZ"
        self.ISA06 = "83-1002022"
        self.ISA08 = "841439824"
        self.AMT_CODES = ['D2', 'FK', 'R', 'C1', 'P3', 'B9']
        self.INS02_VAL = ['18', '19', '25', '26', '01', 'G8', 'null']
        self.weights = [0.8] + [0.2 / (len(self.INS02_VAL) - 1)] * (len(self.INS02_VAL) - 1)

        now = self.time
        self.ISA13 = now.strftime("%Y%m%d1")
        self.ccyymmdd = now.strftime("%Y%m%d")
        self.yymmdd = now.strftime("%y%m%d")
        self.hhmm = now.strftime("%H%M")
        self.hhmmss = now.strftime("%H%M%S")

        logger.debug("Make834 initialized")

    def make_dir(self, file_directory):
        if not os.path.exists(file_directory):
            os.mkdir(file_directory)
            logger.debug(f"New file directory created called: {file_directory}")

    def make_file_path(self, file_directory):
        edi_name = f"834.VFMP.{self.time.year}.{self.yymmdd}.{self.hhmm}.{self.ISA13}.edi"
        logger.debug(f"New file created named: {edi_name} at {file_directory}")
        return os.path.join(file_directory, edi_name)

    def makeISA(self):
        return (
            f"ISA*00*          *00*          *{self.ISA05_07}*{self.ISA06:<15}*{self.ISA05_07}*{self.ISA08:<15}*{self.yymmdd}*{self.hhmm}*$*00501"
            f"*{self.ISA13}*0*T*:~\n")

    def makeGS(self):
        return f"GS*BE*{self.ISA06}*{self.ISA08}*{self.ccyymmdd}*{self.hhmmss}*61*X*005010X220A1~\n"

    def makeGE(self, num):
        return f"GE*{num}*61~\n"

    def makeIEA(self):
        return f"IEA*1*{self.ISA13}~"

    def getIns02(self):
        return random.choices(self.INS02_VAL, weights=self.weights, k=1)[0]

    def getFid(self):
        return random.randint(100_000_000, 999_999_999)

    def getPolicyID2(self):
        return random.randint(10_000_000, 99_999_999)

    def makeMessage(self, num):
        amt_segments = []
        segment_count = 0
        # half the time has second address
        n302 = f"{self.fake.secondary_address().replace(".", "")}" if random.random() < 0.5 else ""
        ins02 = self.getIns02()
        self.counts[ins02] += 1

        # INS02 null, 01, 18, 19, 25, 26, G8
        # INS08 always null, AC, TE
        segments = [f"ST*834*{num:04}~\n",
                    f"BGN*00*{uuid.uuid4().hex.upper()}*{self.ccyymmdd}*{self.hhmmss}*UT***2~\n",
                    f"N1*P5*{self.fake.company()}*FI*{self.getFid()}~\n",
                    f"N1*IN*{self.fake.company()}*FI*{self.getFid()}~\n",
                    f"INS*Y*{self.getIns02()}*001**A***AC~\n",
                    f"REF*0F*1111111111V{self.getPolicyID2()}~\n",
                    f"REF*6O*1111111111V{self.getPolicyID2()}~\n",
                    f"NM1*IL*1*{self.fake.last_name().upper()}*{self.fake.first_name().upper()}*{self.fake.first_name().upper()}***34*{self.fake.ssn()}~\n",
                    f"PER*IP**TE*{self.fake.basic_phone_number()}~\n",
                    f"N3*{self.fake.building_number()} {self.fake.street_name()}*{n302}~\n",
                    f"N4*{self.fake.city().upper()}*{self.fake.state_abbr().upper()}*{self.fake.zipcode()}~\n"
                    ]
        # add AMT values
        for code in self.AMT_CODES:
            # if AMT = D2, FK, R ($)
            value = random.randint(0, 9)
            if value == 0:
                continue
            amt_segments.append(f"AMT*{code}*{value}~\n")
        segments += amt_segments
        segment_count += len(segments)
        segments += [f"HD*001**MM*MCVA1003~\n",
                     f"DTP*348*D8*{self.ccyymmdd}~\n",
                     f"SE*{segment_count + 3}*{num:04}~\n"
                     ]
        return segments

        # Lookup sponsor ID instead of SSN
        # keep track of sponsor ID, first, middle, last name, address, SSN, beneficiary ID, phone [hashtable/dict]
