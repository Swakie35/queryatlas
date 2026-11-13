import sqlite3
import pytest
from queryatlas.warehouse import connect,initialize,upsert_events,synthetic_events,report,demo

def test_incremental_upsert_idempotent():
    con=connect(':memory:');initialize(con)
    data=synthetic_events(days=3)
    upsert_events(con,data);upsert_events(con,data)
    assert con.execute('SELECT COUNT(*) FROM fact_sales_events').fetchone()[0]==len(data)
    record=dict(data[0]);record['unit_price_pence']=999
    upsert_events(con,[record])
    assert con.execute('SELECT unit_price_pence FROM fact_sales_events WHERE event_id=?',(record['event_id'],)).fetchone()[0]==999

def test_refund_netting_and_cohorts():
    con=connect(':memory:');initialize(con)
    events=[dict(event_id='a',event_day='2025-01-01',site_id=1,product_id=1,customer_key='fake-1',kind='SALE',quantity=2,unit_price_pence=100),
            dict(event_id='b',event_day='2025-01-01',site_id=1,product_id=1,customer_key='fake-1',kind='REFUND',quantity=1,unit_price_pence=100),
            dict(event_id='c',event_day='2025-01-02',site_id=1,product_id=1,customer_key='fake-1',kind='SALE',quantity=1,unit_price_pence=100)]
    upsert_events(con,events)
    assert report(con)[0]['net_revenue_pence']==100
    assert report(con,'retention_report')[0]['returning_customers']==1

def test_data_contract():
    con=connect(':memory:');initialize(con)
    with pytest.raises(ValueError):upsert_events(con,[{'event_id':'oops'}])

def test_demo(tmp_path):
    r=demo(tmp_path/'test.sqlite',tmp_path/'daily.csv')
    assert r['fact_rows']>100
    assert (tmp_path/'daily.csv').exists()
    assert (tmp_path/'retention.csv').exists()
