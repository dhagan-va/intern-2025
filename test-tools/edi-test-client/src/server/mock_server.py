from flask import Flask

app = Flask(__name__)

SAMPLE_271 = (
    f"ISA*00*          *00*          *ZZ*1234567        *ZZ*11111          *170508*1141*>*00501*000000101*1*P*:~\n"
    "GS*HC*XXXXXXX*XXXXX*20170617*1741*101*X*005010X279A1~\n"
    "ST*271*4321*005010X279A1~\n"
    "BHT*0022*11*10001234*20060501*1319~\n"
    "HL*1**20*1~\n"
    "NM1*PR*2*ABC COMPANY*****PI*842610001~\n"
    "HL*2*1*21*1~\n"
    "NM1*1P*2*BONE AND JOINT CLINIC*****SV*2000035~\n"
    "HL*3*2*22*0~\n"
    "TRN*2*93175-012547*9877281234~\n"
    "NM1*IL*1*SMITH*JOHN****MI*123456789~\n"
    "N3*15197 BROADWAY AVENUE*APT 215~\n"
    "N4*KANSAS CITY*MO*64108~\n"
    "DMG*D8*19630519*M~\n"
    "DTP*346*D8*20060101~\n"
    "EB*1**30**GOLD 123 PLAN~\n"
    "EB*L~\n"
    "EB*1**1>33>35>47>86>88>98>AL>MH>UC~\n"
    "EB*B**1>33>35>47>86>88>98>AL>MH>UC*HM*GOLD 123 PLAN*27*10*****Y~\n"
    "EB*B**1>33>35>47>86>88>98>AL>MH>UC*HM*GOLD 123 PLAN*27*30*****N~\n"
    "LS*2120~\n"
    "NM1*P3*1*JONES*MARCUS****SV*0202034~\n"
    "LE*2120~\n"
    "SE*22*4321~\n"
    "GE*1*101~\n"
    "IEA*1*000000101~\n"
)

@app.post("/270/")
def endpoint():
    return SAMPLE_271