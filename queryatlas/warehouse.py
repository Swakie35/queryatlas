"""Runnable retail warehouse exercise with incremental upserts and window reports."""
from __future__ import annotations
import csv
from importlib import resources
from pathlib import Path
import random
import sqlite3
from datetime import date,timedelta

SQL=resources.files('queryatlas').joinpath('sql')

def connect(db:str|Path):
    con=sqlite3.connect(str(db))
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def initialize(con):
    con.executescript(SQL.joinpath('schema.sql').read_text())
    with con:
        con.executemany('INSERT INTO dim_site VALUES(?,?) ON CONFLICT(site_id) DO UPDATE SET site_name=excluded.site_name',
                        [(1,'City Centre'),(2,'Riverside'),(3,'West End')])
        con.executemany('INSERT INTO dim_product VALUES(?,?,?) ON CONFLICT(product_id) DO UPDATE SET product_name=excluded.product_name,category=excluded.category',
                        [(1,'Coffee','Drinks'),(2,'Tea','Drinks'),(3,'Wrap','Food'),(4,'Salad','Food'),(5,'Juice','Drinks')])

def upsert_events(con,events:list[dict])->int:
    fields=('event_id','event_day','site_id','product_id','customer_key','kind','quantity','unit_price_pence')
    if not events:return 0
    for event in events:
        if any(k not in event for k in fields):raise ValueError('missing event fields')
        date.fromisoformat(event['event_day'])
        if not event['event_id'] or not event['customer_key']:raise ValueError('empty id')
        if event['kind'] not in {'SALE','REFUND'} or event['quantity']<=0 or event['unit_price_pence']<0:
            raise ValueError('invalid transaction')
    with con:
        con.executemany('''INSERT INTO fact_sales_events(event_id,event_day,site_id,product_id,customer_key,kind,quantity,unit_price_pence)
                           VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(event_id) DO UPDATE SET
                           event_day=excluded.event_day,site_id=excluded.site_id,product_id=excluded.product_id,
                           customer_key=excluded.customer_key,kind=excluded.kind,
                           quantity=excluded.quantity,unit_price_pence=excluded.unit_price_pence,
                           updated_at=CURRENT_TIMESTAMP''', [tuple(e[k] for k in fields) for e in events])
    return len(events)

def synthetic_events(days:int=90,seed:int=11):
    rng=random.Random(seed);events=[];start=date(2025,1,1)
    for day_no in range(days):
        day=str(start+timedelta(days=day_no))
        for site in (1,2,3):
            for j in range(rng.randint(7,14)):
                product=rng.randint(1,5)
                events.append(dict(event_id=f'{day}-{site}-{j}',event_day=day,site_id=site,
                                   product_id=product,customer_key=f'demo-customer-{rng.randint(1,130)}',
                                   kind='REFUND' if rng.random()<.065 else 'SALE',quantity=rng.randint(1,3),
                                   unit_price_pence={1:320,2:290,3:580,4:650,5:410}[product]))
    return events

def report(con,name='daily_report'):
    if name not in ('daily_report','retention_report'):raise ValueError('unknown report')
    return [dict(x) for x in con.execute(SQL.joinpath(f'{name}.sql').read_text())]

def export_csv(rows,path):
    if not rows:return
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def demo(db='warehouse.sqlite',out='reports/generated/daily.csv'):
    con=connect(db);initialize(con);events=synthetic_events();upsert_events(con,events)
    daily=report(con);export_csv(daily,out)
    retention=report(con,'retention_report');export_csv(retention,str(Path(out).with_name('retention.csv')))
    count=con.execute('SELECT COUNT(*) FROM fact_sales_events').fetchone()[0]
    con.close()
    return {'fact_rows':count,'daily_rows':len(daily),'cohort_rows':len(retention),'report':out}
