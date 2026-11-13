import argparse
from .warehouse import demo
p=argparse.ArgumentParser(description='Build local analytics warehouse and export SQL reports')
p.add_argument('--db',default='warehouse.sqlite');p.add_argument('--out',default='reports/generated/daily.csv')
a=p.parse_args();print(demo(a.db,a.out))
