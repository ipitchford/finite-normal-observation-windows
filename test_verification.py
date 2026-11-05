#!/usr/bin/env python3
"""Normal/-O positive replay and corrupted-example rejection; retain exact logs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    tests=[('positive','raise SystemExit(v.main())',True),
           ('corrupt_simpson','v.simpson=lambda *a,**k:999\nraise SystemExit(v.main())',False),
           ('corrupt_series','v.multiply_series=lambda l,r,d:[v.F(0)]*(d+1)\nraise SystemExit(v.main())',False),
           ('invalid_panels','v.simpson(lambda t:t,1,panels=3)',False),
           ('nan_integral','v.require_close(float("nan"),0)',False)]
    records=[]
    for mode,flags in [('normal',[]),('optimized',['-O'])]:
        for name,body,success in tests:
            target=args.out/(mode+'-'+name)
            target.mkdir()
            output=target/'results.json'
            program=('import sys\nsys.path.insert(0,sys.argv[1])\nimport verify_normal_frames as v\n'
                     'sys.argv=["test","--output",sys.argv[2]]\n'+body+'\n')
            command=[sys.executable,'-B',*flags,'-c',program,str(HERE),str(output)]
            result=subprocess.run(command,capture_output=True,text=True,timeout=60)
            (target/'command.json').write_text(json.dumps(command,indent=2)+'\n')
            (target/'stdout.txt').write_text(result.stdout)
            (target/'stderr.txt').write_text(result.stderr)
            data=json.loads(output.read_text()) if output.exists() else None
            failed_guard=('VerificationError:' in result.stderr or
                          (data is not None and any('VerificationError:' in c.get('error','') for c in data['checks'])))
            passed=(result.returncode==0 and data is not None and data['all_passed']) if success else (result.returncode!=0 and failed_guard)
            records.append({'case':target.name,'expected_success':success,'exit_code':result.returncode,'passed':passed,
                            'filesSha256':{p.name:digest(p) for p in sorted(target.iterdir()) if p.is_file()}})
    normal=json.loads((args.out/'normal-positive/results.json').read_text())
    optimized=json.loads((args.out/'optimized-positive/results.json').read_text())
    agreement=normal==optimized
    receipt={'recordedAt':datetime.now(timezone.utc).isoformat(),'python':sys.version,
             'codeSha256':{p.name:digest(p) for p in [HERE/'verify_normal_frames.py',Path(__file__).resolve()]},
             'cases':records,'normalOptimizedExactAgreement':agreement,
             'passed':agreement and all(r['passed'] for r in records),
             'scope':'Example checks and deliberate corruption rejection only; no abstract theorem or novelty verification.'}
    (args.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if not receipt['passed']:
        raise SystemExit(1)

if __name__=='__main__':
    main()
