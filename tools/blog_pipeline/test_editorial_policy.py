import copy,importlib.util,json,unittest
from pathlib import Path

candidate=Path(__file__).resolve().parents[2]
ROOT=candidate if (candidate/'editorial').is_dir() else Path('/Users/satoshioka/mirai-toushi-navi')
def module(path,name):
  spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.ROOT=ROOT;m.HERE=ROOT/'tools/blog_pipeline';m.DATA=ROOT/'editorial'
  return m
p=module(ROOT/'tools/blog_pipeline/pipeline.py','new_pipeline')
policy=p.editorial_policy
history=p.articles()

def future(short):
  a=copy.deepcopy(next(x for x in history if x['id']=='2026-10-01-'+short))
  a['id']='2026-10-02-'+short;a['date']='2026-10-02';a['design']['policy_version']=2
  for figure in a['design']['diagrams'].values():
    figure['relation']=policy.RELATIONS[figure['layout']]
    figure['reason']='本文の情報の関係が一目で読み取れる構図を選択する'
  ids=[x['id'] for x in policy.recent_articles(a,history)]
  a['editorial_quality']={
    'voice_reference':policy.VOICE_REFERENCE,
    'analogy':{'quote':a['lead'][1],'limit':'例えでは制度の例外条件を全部表せないため本文で補う'},
    'example':{'quote':a['sections'][1]['paragraphs'][0],'kind':'walkthrough'},
    'action':a['sections'][4]['paragraphs'][0],
    'hero_review':{'recent_article_ids':ids,'traits':{'viewpoint':'屋外の広い景色' if short.startswith('sbi') else '書類を真上から見る','people':'手元のみ','objects':short,'setting':'記事固有の場面'},'selection_reason':'直近の記事とは主要小物と背景が異なる構図にする'},
    'diagram_review':{'recent_article_ids':ids,'selection_reason':'分け方と時間、または書類と条件の関係を異なる構図で示す'}}
  return a

class EditorialPolicyTests(unittest.TestCase):
  def setUp(self):self.a=future('sbi-individual-government-bond-buy')

  def test_future_draft_requires_review(self):
    del self.a['editorial_quality']
    with self.assertRaisesRegex(ValueError,'voice reference'):policy.validate_articles(history+[self.a])

  def test_real_passages_and_distinct_layouts_pass(self):
    b=future('pension-withholding-slip-check')
    report=policy.validate_articles(history+[self.a,b])
    self.assertEqual(len(report['checked']),2)

  def test_missing_or_invented_analogy_stops(self):
    self.a['editorial_quality']['analogy']['quote']='本文には存在しない例え話の記録'
    with self.assertRaisesRegex(ValueError,'absent'):policy.validate_articles(history+[self.a])

  def test_single_repeated_layout_stops(self):
    figures=self.a['design']['diagrams'];figures['5']=copy.deepcopy(figures['1'])
    with self.assertRaisesRegex(ValueError,'different layouts'):policy.validate_articles(history+[self.a])

  def test_stale_seven_article_review_stops(self):
    self.a['editorial_quality']['hero_review']['recent_article_ids'].pop()
    with self.assertRaisesRegex(ValueError,'latest seven'):policy.validate_articles(history+[self.a])

  def test_same_day_photo_composition_stops(self):
    b=future('pension-withholding-slip-check')
    b['editorial_quality']['hero_review']['traits']=copy.deepcopy(self.a['editorial_quality']['hero_review']['traits'])
    with self.assertRaisesRegex(ValueError,'composition'):policy.validate_articles(history+[self.a,b])

  def test_repeated_combination_needs_a_reason(self):
    prior=[]
    for i in range(3):
      a=copy.deepcopy(history[-1]);a.update(id='test-prior-'+str(i),date='2026-10-01',design=copy.deepcopy(self.a['design']));prior.append(a)
    articles=history+prior
    ids=[a['id'] for a in policy.recent_articles(self.a,articles)]
    for key in ('hero_review','diagram_review'):self.a['editorial_quality'][key]['recent_article_ids']=ids
    with self.assertRaisesRegex(ValueError,'justification'):policy.validate_articles(articles+[self.a])
    self.a['editorial_quality']['diagram_repeat_reason']='今回も支出時期による分類と換金の期間が主題なので、この関係を正しく示すために選ぶ'
    self.assertEqual(len(policy.validate_articles(articles+[self.a])['checked']),1)

  def test_diagram_labels_are_topic_data(self):
    for a in [self.a,future('pension-withholding-slip-check')]:
      for figure in a['design']['diagrams'].values():
        f=copy.deepcopy(figure);f['note']='記事固有の確認先と手順を示す補足説明'
        if f['layout']=='timeline':
          f.update(axis=['申込日','照合日','完了日'],periods=['確認の前','確認の後'])
          result=p.render_diagram(f);self.assertIn('照合日',result);self.assertNotIn('発行日',result)
        if f['layout']=='document':
          f['document_heading']=['口座の確認書類','確認箇所の模式図']
          result=p.render_diagram(f);self.assertIn('口座の確認書類',result);self.assertNotIn('公的年金等の源泉徴収票',result)
        if f['layout']=='decision':
          f['outcomes']=[['合致する','受付内容を確認する'],['合致しない','確認窓口へ照合する']]
          result=p.render_diagram(f);self.assertIn('受付内容を確認する',result);self.assertNotIn('所得税の確定申告不要制度の対象',result)

  def test_missing_timeline_labels_stops(self):
    del self.a['design']['diagrams']['5']['axis']
    with self.assertRaisesRegex(ValueError,'axis'):p.design_content(self.a)

  def test_semantic_labels_cannot_inject_html(self):
    f=copy.deepcopy(self.a['design']['diagrams']['5']);f['axis'][0]='<script>bad</script>'
    self.assertIn('&lt;script&gt;',p.render_diagram(f));self.assertNotIn('<script>',p.render_diagram(f))

if __name__=='__main__':unittest.main()
