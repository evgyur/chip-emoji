import importlib.util,json,unittest
from pathlib import Path
p=Path(__file__).with_name('mosaic.py')
s=importlib.util.spec_from_file_location('mosaic',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
    def setUp(self):self.manifest=json.loads((p.parent.parent/'assets/human20-mosaic.json').read_text())
    def test_mascot(self):
        r=m.compose(self.manifest);self.assertEqual(len(r['entities']),99)
        self.assertEqual([len(x.replace('\u200b','')) for x in r['text'].splitlines()],[9]*11)
        self.assertEqual([e['custom_emoji_id'] for e in r['entities']],self.manifest['emoji_ids'])
    def test_rich_prefix(self):
        b='🦀 Заголовок';e={'type':'bold','offset':3,'length':9}
        r=m.compose(self.manifest,b,'Хвост',[e]);self.assertEqual(r['entities'][0],e)
        self.assertEqual(r['entities'][1]['offset'],m.units(b+'\n\u200b'))
        raw=r['text'].encode('utf-16-le')
        for x in r['entities'][1:]:self.assertEqual(raw[x['offset']*2:(x['offset']+2)*2].decode('utf-16-le'),'🎨')
        self.assertTrue(r['text'].endswith('\nХвост'))
    def test_bad_ids(self):
        self.manifest['emoji_ids']=[]
        with self.assertRaises(ValueError):m.compose(self.manifest)
    def test_bad_entity(self):
        with self.assertRaises(ValueError):m.compose(self.manifest,'x',entities=[{'offset':3,'length':1}])
    def test_too_long(self):
        with self.assertRaises(ValueError):m.compose(self.manifest,'x'*4096)
    def test_bad_geometry(self):
        with self.assertRaises(ValueError):m.prepare('missing','unused',cols=10)
if __name__=='__main__':unittest.main()
