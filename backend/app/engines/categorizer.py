"""Small, transparent seed-trained NLP baseline, not a claimed accuracy benchmark."""
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

EXAMPLES = {
    'Groceries': ['grocery supermarket milk bread eggs rice vegetables fruit', 'market butter cheese flour lentils food mart'],
    'Dining': ['restaurant cafe coffee pizza lunch dinner burger', 'bakery takeaway tea sandwich meal bistro'],
    'Transport': ['petrol diesel fuel gas station taxi uber', 'train bus metro ticket parking toll transport'],
    'Shopping': ['clothing shirt shoes apparel jeans store', 'electronics laptop phone charger books retail'],
    'Health': ['pharmacy medicine hospital doctor clinic', 'medical tablets vitamins dental health'],
    'Utilities': ['electricity water internet broadband bill', 'utility mobile recharge telephone energy'],
}
model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), MultinomialNB(alpha=0.3))
model.fit([s for samples in EXAMPLES.values() for s in samples], [c for c, samples in EXAMPLES.items() for _ in samples])

def categorize(text: str):
    probabilities = model.predict_proba([text])[0]
    score = float(max(probabilities))
    return {'category': str(model.classes_[probabilities.argmax()]) if score >= .27 else 'Other', 'score': round(score, 3), 'method': 'TF-IDF + Naive Bayes; small seed-trained baseline. Review suggested category.'}
