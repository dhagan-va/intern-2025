from pathlib import Path

def split_edi_transactions(content):
    transactions = []
    current_transaction = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        current_transaction.append(line)
        
        if line.startswith('IEA*'):
            transactions.append('\n'.join(current_transaction) + '\n')
            current_transaction = []
    
    return transactions

def load_payloads():
    payloads_dir = Path(__file__).parent / "payloads"
    transactions = []
    
    if payloads_dir.exists():
        for file_path in payloads_dir.glob("*.edi"):
            with open(file_path, 'r') as f:
                content = f.read()
                transactions.extend(split_edi_transactions(content))
    
    return {270: transactions if transactions else [_fallback_270()]}

def _fallback_270():
    return (
        "ISA*00*          *00*          *ZZ*1234567        *ZZ*11111          *170508*1141*^*00501*000000101*1*P*:~\n"
        "GS*HC*XXXXXXX*XXXXX*20170617*1741*101*X*005010X279A1~\n"
        "ST*270*1234*005010X279A1~\n"
        "BHT*0022*13*10001234*20060501*1319~\n"
        "HL*1**20*1~\n"
        "NM1*PR*2*ABC COMPANY*****PI*842610001~\n"
        "HL*2*1*21*1~\n"
        "NM1*1P*2*BONE AND JOINT CLINIC*****SV*2000035~\n"
        "HL*3*2*22*0~\n"
        "TRN*1*93175-012547*9877281234~\n"
        "NM1*IL*1*SMITH*ROBERT****MI*11122333301~\n"
        "DMG*D8*19430519~\n"
        "DTP*291*D8*20060501~\n"
        "EQ*30~\n"
        "SE*13*1234~\n"
        "GE*1*101~\n"
        "IEA*1*000000101~\n"
    )

payloads = load_payloads()
print(payloads[270][0])