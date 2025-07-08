# Test Suite Guide

Script to generate EDI files for testing and validation.

## Configuration

| Variable          | Description                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| `FAKER_SEED`      | Seed for consistent fake data generation                                                                  |
| `RANDOM_SEED`     | Seed for deterministic random behavior                                                                    |
| `NUMBER_OF_TESTS` | Number of EDI 834 messages to generate (Based on Binomial distribution given the average number of tests) |
| `DIRECTORY_NAME`  | Output folder name for the generated EDI file                                                             |
| `USER_LIMIT`      | Max number of users to simulate                                                                           |

## How to use it

```sh
python TestSuite.py
```

This (currently) generates an 834 file in the DIRECTORY_NAME with log information under TestSuite.log
