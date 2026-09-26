import argparse
import json

from .controller import Controller
from .inventory import run_inventory
from .recompute import recompute_run


def main():
    parser=argparse.ArgumentParser(description='SC Lab1 Goal1: raw diagnostics and bounded live roles')
    parser.add_argument('mode',choices=['inventory','live','recompute'])
    parser.add_argument('--run-id')
    parser.add_argument('--enable-live',action='store_true',help='explicit existing-account model use; otherwise blocked')
    parser.add_argument('--stop-after',type=int,help='checkpoint after this many completed roles; resume using the same run ID')
    args=parser.parse_args()
    if args.mode=='inventory':
        result=run_inventory();result.pop('dt_counts',None)
    elif args.mode=='live':
        if not args.enable_live or not args.run_id:parser.error('live requires --enable-live and --run-id')
        result=Controller(args.run_id).run(stop_after=args.stop_after)
        result={k:result[k] for k in ('run_id','status','phase','calls','errors')}
    else:
        if not args.run_id:parser.error('recompute requires --run-id')
        result=recompute_run(args.run_id)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
