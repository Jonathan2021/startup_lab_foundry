"""Read-only verification of adoption, current record identities and backup."""
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

HERE=Path(__file__).resolve().parent
adoption=json.loads((HERE/'adoption-result.json').read_text())
working=Path(adoption['target'])
backup=working.parent/'backups/2026-10-02-console-complete.local.db'
report={'source_databases':{},'csv_sources':{},'working_database':str(working),'backup':str(backup)}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def connect(path):
    return sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)

with connect(working) as current:
    assert current.execute('PRAGMA integrity_check').fetchone()==('ok',)
    assert current.execute('PRAGMA foreign_key_check').fetchall()==[]
    report['counts']={table:current.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in ['ideas','ventures','reference_sources','step_runs','evidence','decisions','artifacts']}
    assert report['counts']['ideas']==250
    assert report['counts']['ventures']==5
    assert report['counts']['reference_sources']==99
    assert report['counts']['step_runs']==8
    report['revision']=current.execute('SELECT version_num FROM alembic_version').fetchone()[0]
    assert report['revision']=='7ce261002001'
    for path,expected in adoption['source_sha256'].items():
        path=Path(path)
        assert digest(path)==expected
        verified=0
        with connect(path) as old:
            tables=[row[0] for row in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('alembic_version','sqlite_sequence')")]
            for table in tables:
                assert table.replace('_','').isalnum()
                ids={row[0] for row in old.execute('SELECT id FROM '+table)}
                retained={row[0] for row in current.execute('SELECT id FROM '+table)}
                assert ids<=retained,(table,ids-retained)
                verified+=len(ids)
        report['source_databases'][str(path)]={'sha256':expected,'unchanged':True,'retained_record_ids':verified}
    for source in current.execute("SELECT title,content_digest,notes FROM reference_sources WHERE kind='spreadsheet'"):
        title,expected,notes=source
        name=title.split(' (',1)[0]
        path=Path('/home/jonathan/Downloads')/name
        assert digest(path)==expected
        with path.open(encoding='utf-8-sig',newline='') as stream:
            rows=list(csv.reader(stream))
        assert rows==json.loads(notes)['rows']
        report['csv_sources'][name]={'sha256':expected,'rows_retained':len(rows)}
    with connect(backup) as saved:
        assert saved.execute('PRAGMA integrity_check').fetchone()==('ok',)
        assert saved.execute('PRAGMA foreign_key_check').fetchall()==[]
        for table in ['ideas','ventures','reference_sources','step_runs','evidence','decisions','artifacts']:
            assert saved.execute('SELECT count(*) FROM '+table).fetchone()[0]==report['counts'][table]
    for idea in ['D001','D002','D003']:
        assert current.execute('SELECT count(*) FROM idea_relations WHERE source_idea_id=?',(idea,)).fetchone()[0]>0
report['backup_sha256']=digest(backup)
report['integrity']='ok'
report['foreign_keys']='ok'
(HERE/'state-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
