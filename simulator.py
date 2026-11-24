import json, logging, sys
from pathlib import Path

logging.basicConfig(filename='activity.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def cpu(bursts, policy, quantum=2):
    if not bursts or any(type(b) is not int or b <= 0 for b in bursts):
        raise ValueError('Positive integer bursts required')
    if policy not in ('FCFS', 'SJF', 'RR') or quantum <= 0:
        raise ValueError('Invalid policy or quantum')
    queue = list(range(len(bursts)))
    if policy == 'SJF':
        queue.sort(key=lambda i: bursts[i])
    remaining, finish, trace = bursts[:], {}, []
    t = 0
    while queue:
        i = queue.pop(0)
        duration = min(quantum, remaining[i]) if policy == 'RR' else remaining[i]
        trace.append([i+1, t, t+duration])
        t += duration
        remaining[i] -= duration
        if remaining[i]:
            queue.append(i)
        else:
            finish[i] = t
    return {'trace': trace, 'wait': sum(finish[i]-b for i,b in enumerate(bursts))/len(bursts),
            'turnaround': sum(finish.values())/len(bursts)}

def memory(refs, capacity, policy):
    if type(capacity) is not int or capacity < 1 or not refs:
        raise ValueError('Positive capacity and nonempty references required')
    if policy not in ('FIFO', 'LRU') or any(type(x) is not int or x < 0 for x in refs):
        raise ValueError('Invalid page or policy')
    frames, faults, trace = [], 0, []
    for page in refs:
        hit = page in frames
        if hit and policy == 'LRU':
            frames.remove(page)
            frames.append(page)
        if not hit:
            faults += 1
            if len(frames) == capacity:
                frames.pop(0)
            frames.append(page)
        trace.append([page, frames[:], 'hit' if hit else 'fault'])
    return {'faults': faults, 'hits': len(refs)-faults, 'trace': trace}

def banker(available, allocation, maximum):
    m, n = len(available), len(allocation)
    if not m or not n or len(maximum) != n:
        raise ValueError('Invalid matrix dimensions')
    rows = allocation + maximum + [available]
    if any(len(r)!=m or any(type(x) is not int or x<0 for x in r) for r in rows):
        raise ValueError('Invalid resource values')
    need = [[maximum[i][j]-allocation[i][j] for j in range(m)] for i in range(n)]
    if any(x<0 for r in need for x in r):
        raise ValueError('Allocation exceeds maximum')
    work, sequence = available[:], []
    while len(sequence)<n:
        i = next((i for i in range(n) if i not in sequence and
                  all(x<=y for x,y in zip(need[i],work))), None)
        if i is None:
            break

        sequence.append(i)
        work = [x+y for x,y in zip(work,allocation[i])]
    return {'safe': len(sequence)==n, 'sequence': [i+1 for i in sequence]}

def disk(head, requests, policy, limit=199):
    if not requests or policy not in ('FCFS','SSTF') or any(type(x) is not int or not 0<=x<=limit for x in [head]+requests):
        raise ValueError('Invalid cylinder or policy')
    pending, order, movement = requests[:], [], 0
    while pending:
        i = 0 if policy=='FCFS' else min(range(len(pending)), key=lambda i: abs(pending[i]-head))
        target = pending.pop(i)
        movement += abs(target-head)
        head = target
        order.append(target)
    return {'order': order, 'movement': movement}

def run(data, choice='5'):
    result = {}
    if choice in ('1','5'):
        result['CPU'] = {p:cpu(data['bursts'],p) for p in ('FCFS','SJF','RR')}
    if choice in ('2','5'):
        result['Memory'] = {p:memory(data['pages'],data['frames'],p) for p in ('FIFO','LRU')}
    if choice in ('3','5'):
        result['Deadlock'] = banker(data['available'],data['allocation'],data['maximum'])
    if choice in ('4','5'):
        result['Disk'] = {p:disk(data['head'],data['requests'],p) for p in ('FCFS','SSTF')}
    return result

def main():
    try:
        data = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else 'sample.json').read_text())
        while True:
            choice = '5' if '--all' in sys.argv else input('1 CPU | 2 Memory | 3 Deadlock | 4 Disk | 5 All | 0 Exit: ')
            if choice == '0':
                 return 0
            if choice not in ('1','2','3','4','5'):
                 logging.warning('Invalid menu choice')
                 print('Invalid choice')
                 continue
            result = run(data,choice)
            output = json.dumps(result,indent=2)
            print(output)
            Path('results.json').write_text(output)
            logging.info('Completed option %s',choice)
            if '--all' in sys.argv:
                 return 0
    except (ValueError, TypeError, KeyError, OSError, EOFError) as exc:
        logging.error('%s',exc)
        print('Error:',exc,file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
