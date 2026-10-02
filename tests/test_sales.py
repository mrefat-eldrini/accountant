import importlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///'+str(tmp_path/'test.db'))
    import main
    main=importlib.reload(main)
    with TestClient(main.app) as client:
        response=client.post('/login',data={'username':'admin','password':'Admin123!'},follow_redirects=False)
        assert response.status_code==303
        yield client,main
    main.engine.dispose()


def token(response):
    return re.search(r"name='token' value='([^']+)'",response.text).group(1)


def create(client,kind='Sales Invoice',terms='Credit',paid='0',lines=None):
    csrf=token(client.get('/sales/new'))
    lines=lines or [{'code':'S01','description':'Service','unit':'pcs','quantity':'2','price':'500','discount':'0','tax_rate':'15'}]
    response=client.post('/sales/new',data={'token':csrf,'kind':kind,'terms':terms,'customer_id':'1',
        'document_date':'2026-10-02','due_date':'2026-10-30','paid':paid,'lines':json.dumps(lines),'notes':'Test'},follow_redirects=False)
    assert response.status_code==303,response.text
    return int(response.headers['location'].split('/')[-1])


def action(client,doc_id,action,data=None):
    csrf=token(client.get(f'/sales/{doc_id}'))
    return client.post(f'/sales/{doc_id}/{action}',data=dict(data or {},token=csrf),follow_redirects=False)


def test_quotation_conversion_is_idempotent_and_updates_dashboard(app_client):
    client,main=app_client
    initial=main.q('SELECT COUNT(*) count FROM invoices',one=True)['count']
    doc_id=create(client,kind='Quotation')
    assert main.q('SELECT COUNT(*) count FROM invoices',one=True)['count']==initial
    csrf=token(client.get(f'/sales/{doc_id}'))
    first=client.post(f'/sales/{doc_id}/convert',data={'token':csrf},follow_redirects=False)
    second=client.post(f'/sales/{doc_id}/convert',data={'token':csrf},follow_redirects=False)
    assert first.headers['location']==second.headers['location']
    assert main.q('SELECT COUNT(*) count FROM invoices',one=True)['count']==initial+1
    doc=main.q("SELECT * FROM sales_documents WHERE kind='Sales Invoice'",one=True)
    assert Decimal(str(doc['total']))==Decimal('1150')
    assert client.get('/').status_code==200
    assert client.get('/sales/statements?customer_id=1').status_code==200


def test_cash_sale_and_partial_return(app_client):
    client,main=app_client
    doc_id=create(client,terms='Cash')
    assert action(client,doc_id,'return',{'return_0':'1','reason':'Item returned'}).status_code==303
    doc=main.q('SELECT * FROM sales_documents WHERE id=:id',{'id':doc_id},True)
    inv=main.q('SELECT * FROM invoices WHERE id=:id',{'id':doc['invoice_id']},True)
    assert Decimal(str(inv['total']))==Decimal('575')
    assert Decimal(str(inv['paid']))==Decimal('575')
    refund=main.q('SELECT * FROM sales_payments WHERE amount<0',one=True)
    assert Decimal(str(refund['amount']))==Decimal('-575')
    assert refund['method']=='Refund pending'
    assert action(client,doc_id,f"refund/{refund['id']}").status_code==303
    assert main.q('SELECT method FROM sales_payments WHERE id=:id',{'id':refund['id']},True)['method']=='Refund'
    assert action(client,doc_id,'return',{'return_0':'2','reason':'Too many'}).status_code==400
    assert action(client,doc_id,'return',{'return_0':'1','reason':'Remaining'}).status_code==303
    assert Decimal(str(main.q('SELECT total FROM invoices WHERE id=:id',{'id':doc['invoice_id']},True)['total']))==0
    assert action(client,doc_id,'return',{'return_0':'1','reason':'Repeated'}).status_code==400


def test_payment_and_overpayment(app_client):
    client,main=app_client
    doc_id=create(client)
    assert action(client,doc_id,'payment',{'amount':'500','payment_date':'2026-10-02','method':'Cash'}).status_code==303
    assert action(client,doc_id,'payment',{'amount':'651','payment_date':'2026-10-02','method':'Cash'}).status_code==400
    assert action(client,doc_id,'payment',{'amount':'650','payment_date':'2026-10-02','method':'Cash'}).status_code==303
    assert main.q('SELECT COUNT(*) count FROM transactions WHERE reference LIKE :ref',{'ref':'SI-%'},True)['count']==1


def test_partial_return_rounding_exact(app_client):
    client,main=app_client
    doc_id=create(client,lines=[{'description':'Fractional','unit':'pcs','quantity':'3','price':'.01','tax_rate':'15'}])
    for _ in range(3):
        assert action(client,doc_id,'return',{'return_0':'1','reason':'Partial'}).status_code==303
    returned=main.q("SELECT SUM(total) value FROM sales_documents WHERE kind='Credit Note'",one=True)['value']
    sold=main.q("SELECT total FROM sales_documents WHERE kind='Sales Invoice'",one=True)['total']
    assert Decimal(str(returned))==Decimal(str(sold))


@pytest.mark.parametrize('bad', ['-1','NaN','Infinity','10000000000000'])
def test_invalid_values_rejected(app_client,bad):
    client,main=app_client
    csrf=token(client.get('/sales/new'))
    response=client.post('/sales/new',data={'token':csrf,'kind':'Sales Invoice','terms':'Credit','customer_id':'1',
        'document_date':'2026-10-02','due_date':'2026-10-30','paid':'0',
        'lines':json.dumps([{'description':'Invalid','unit':'pcs','quantity':'1','price':bad}])},follow_redirects=False)
    assert response.status_code==400
    assert not main.q('SELECT id FROM sales_documents')


def test_xss_escaping_and_csv_safety(app_client):
    client,main=app_client
    main.execq("UPDATE customers SET name=:name WHERE id=1",{'name':'=HYPERLINK("test")'})
    doc_id=create(client,lines=[{'description':'<script>alert(1)</script>','unit':'pcs','quantity':'1','price':'50'}])
    page=client.get(f'/sales/{doc_id}')
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in page.text
    assert '<script>alert(1)</script>' not in page.text
    response=client.get('/sales/reports?format=csv')
    assert "'=HYPERLINK" in response.text


def test_backup_restore_preserves_document_links(app_client):
    client,main=app_client
    main.execq('DELETE FROM customers WHERE id=2')
    doc_id=create(client)
    backup=client.get('/backup/download')
    data=backup.json()
    assert data['meta']['version']=='0.7.0'
    assert data['tables']['sales_documents'][0]['customer_id']==1
    response=client.post('/backup/restore',data={'confirm':'RESTORE'},files={'backup_file':('backup.json',backup.content,'application/json')},follow_redirects=False)
    assert response.status_code==303
    assert main.q('SELECT id FROM sales_documents',one=True)['id']==doc_id
    assert action(client,doc_id,'payment',{'amount':'50','payment_date':'2026-10-02','method':'Cash'}).status_code==303
    assert not main.q("SELECT id FROM system_logs WHERE event='DATABASE_RESTORE_FAILED'")


def test_viewer_read_only_and_unauthenticated(app_client):
    client,main=app_client
    doc_id=create(client)
    client.post('/users',data={'username':'brother-test','first_name':'Brother','last_name':'Test','password':'TestPassword123!','role':'Viewer'},follow_redirects=False)
    client.get('/logout');client.post('/login',data={'username':'brother-test','password':'TestPassword123!'},follow_redirects=False)
    for path in ('/sales','/sales/reports','/sales/statements',f'/sales/{doc_id}'):
        assert client.get(path).status_code==200
    assert client.get('/sales/new',follow_redirects=False).status_code==303
    assert client.post('/sales/new',data={},follow_redirects=False).status_code==303
    for verb in ('convert','return','payment'):
        assert client.post(f'/sales/{doc_id}/{verb}',data={},follow_redirects=False).status_code==303
    client.get('/logout')
    assert client.get('/sales',follow_redirects=False).status_code==303


def test_date_filter_and_export(app_client):
    client,main=app_client
    create(client)
    assert 'SI-' in client.get('/sales/reports?from=2026-10-01&to=2026-10-31&format=csv').text
    assert 'SI-' not in client.get('/sales/reports?from=2026-11-01&format=csv').text
    assert client.get('/sales/reports?from=2026-11-01&to=2026-10-01').status_code==400
