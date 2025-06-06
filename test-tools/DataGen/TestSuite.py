from FileCreation.FileCreation_834 import Make834
from datetime import datetime
import config
from config import get_logger

# 1. determine which distribution of tests to do (high-low error prob)
# 2. randomize error dist (if there is one error on a file, it cant have another error)
# 3. Set number of tests
# 4. Track Personal info based on Sponsor ID, each key will have a value of

# Setup/Initialization
now = datetime.now()
directory = config.DIRECTORY_NAME
n = config.NUMBER_OF_TESTS
logger = get_logger(__name__)

# Make 834 file
gen = Make834()
gen.make_dir(directory)
f = open(gen.make_file_path(directory), 'w')
segments = [gen.makeISA(), gen.makeGS()]
for i in range(n):
    segments += gen.makeMessage(i)

    if i % 10_000 == 0:
        logger.info(f"Generated Message Number {i}")

segments += [gen.makeGE(n), gen.makeIEA()]

f.writelines(segments)
f.close()
# display amount of time it takes to create
END_TIME = datetime.now() - now
logger.info('It took: %d', END_TIME)

# Correct/Wrong
# test_dist = [85/15, 90/10, 92/8, 95/5, 98/2]