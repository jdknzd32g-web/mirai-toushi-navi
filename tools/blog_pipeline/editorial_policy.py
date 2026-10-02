"""Editorial acceptance rules for drafts dated 2026-10-02 onward.

Structural checks cannot judge humor, factual correctness or visual meaning;
they require the author to supply review evidence and prevent template reuse.
"""
from collections import Counter
import json
from pathlib import Path

START = '2026-10-02'
VERSION = 2
VOICE_REFERENCE = 'editorial/ryo-voice-guide.md'
RELATIONS = {'allocation':'partition','timeline':'time','document':'location',
             'decision':'condition','flow':'sequence','record':'record'}
TRAITS = ('viewpoint','people','objects','setting')

def require_text(value, label, minimum=8):
  if not isinstance(value,str) or len(value.strip()) < minimum:
    raise ValueError('Editorial policy: missing ' + label)

def recent_articles(article, articles):
  return sorted([a for a in articles if a.get('date','') < article['date']],
                key=lambda a:(a.get('date',''),a['id']),reverse=True)[:7]

def body_text(article):
  parts=list(article.get('lead',[]))
  for section in article.get('sections',[]):
    parts+=section.get('paragraphs',[])+section.get('items',[])
    for row in section.get('table',{}).get('rows',[]):parts+=row
  return '\n'.join(parts)

def signature(article):
  return tuple(sorted(f.get('layout','cards') for f in article.get('design',{}).get('diagrams',{}).values()))

def validate_articles(articles):
  checked=[]
  for article in articles:
    if article.get('date','') < START:continue
    design=article.get('design',{})
    if design.get('policy_version') != VERSION:
      raise ValueError('Editorial policy: version 2 required for ' + article['id'])
    figures=list(design.get('diagrams',{}).values())
    if not 2 <= len(figures) <= 4 or len({f.get('layout') for f in figures}) < 2:
      raise ValueError('Editorial policy: choose 2–4 useful diagrams with different layouts')
    for figure in figures:
      if figure.get('relation') != RELATIONS.get(figure.get('layout')) or figure.get('layout') not in RELATIONS:
        raise ValueError('Editorial policy: diagram relationship does not match layout')
      require_text(figure.get('reason'),'diagram selection reason')
    review=article.get('editorial_quality',{})
    if review.get('voice_reference') != VOICE_REFERENCE:
      raise ValueError('Editorial policy: use the approved archive-based voice reference')
    text=body_text(article)
    for key in ('analogy','example'):
      record=review.get(key,{})
      require_text(record.get('quote'),key+' passage')
      if record['quote'] not in text:
        raise ValueError('Editorial policy: '+key+' passage absent from article')
    require_text(review['analogy'].get('limit'),'analogy limitation')
    if review['example'].get('kind') not in ('calculation','walkthrough'):
      raise ValueError('Editorial policy: example must be a calculation or concrete walkthrough')
    if review['example']['kind']=='calculation':require_text(review['example'].get('assumptions'),'example assumptions')
    else:
      completion=review['example'].get('completion_quote')
      require_text(completion,'walkthrough completion passage')
      if completion not in text:
        raise ValueError('Editorial policy: walkthrough completion passage absent from article')
    require_text(review.get('action'),'reader action')
    if review['action'] not in text:raise ValueError('Editorial policy: reader action absent from article')
    ids=[a['id'] for a in recent_articles(article,articles)]
    for key in ('hero_review','diagram_review'):
      if review.get(key,{}).get('recent_article_ids') != ids:
        raise ValueError('Editorial policy: '+key+' must cover the actual latest seven articles')
      require_text(review[key].get('selection_reason'),key+' selection reason')
    hero=review['hero_review'].get('traits',{})
    for trait in TRAITS:require_text(hero.get(trait),'header '+trait,minimum=2)
    prior=recent_articles(article,articles)
    repeated=sum(signature(a)==signature(article) for a in prior)
    peers=[a for a in articles if a['id']!=article['id'] and a.get('date')==article['date'] and signature(a)==signature(article)]
    if repeated >= 3 or peers:
      require_text(review.get('diagram_repeat_reason'),'justification for repeating a diagram combination',minimum=20)
    for other in articles:
      if other['id']==article['id'] or other.get('date')!=article['date']:continue
      theirs=other.get('editorial_quality',{}).get('hero_review',{}).get('traits',{})
      if theirs and all(theirs.get(t)==hero[t] for t in TRAITS):
        raise ValueError('Editorial policy: same-day header composition is identical')
    checked.append({'id':article['id'],'layouts':list(signature(article)),'recent_articles':ids,'review':'complete'})
  return {'version':VERSION,'starts_on':START,'checked':checked,
          'limitation':'Human review still judges voice, useful metaphors, visual relationships and source accuracy.'}

if __name__=='__main__':
  import argparse
  parser=argparse.ArgumentParser();parser.add_argument('--date',required=True)
  args=parser.parse_args();root=Path(__file__).resolve().parents[2]
  articles=[json.loads(f.read_text()) for f in (root/'editorial/articles').glob('*.json')]
  probe={'date':args.date}
  print(json.dumps([{'id':a['id'],'title':a['title'],'layouts':list(signature(a)),
                    'hero':a['hero'],'prompt_record':a.get('hero_prompt_record')}
                   for a in recent_articles(probe,articles)],ensure_ascii=False,indent=2))
