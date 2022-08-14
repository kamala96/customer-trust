
import string
from flask import Blueprint, jsonify, request, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user
from customer_trust.forms import GneratorForm
from customer_trust.models import Ecommerce_products, Sentiments, Trust_factors
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import nltk
from operator import itemgetter

nltk.download('stopwords')

csrf = CSRFProtect()

stopword = nltk.corpus.stopwords.words('english')
ps = nltk.PorterStemmer()

generator = Blueprint('generator', __name__)


@login_required
def clean(text):
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text, flags=re.I)
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('<.*?>+', '', text)
    text = str(text).lower()
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    return text


@login_required
def tokenization(text):
    pattern = r'\W+'
    text = re.split(pattern, text)
    return text


@login_required
def remove_stopwords(text):
    text = [word for word in text if word not in stopword]
    return text


@login_required
def stemming1(text):
    text = [ps.stem(word) for word in text]
    return text


@login_required
def sentiment_scores(sentence):
    sentence = str(sentence)
    # sentence = clean(sentence)
    # sentence = tokenization(sentence.lower())
    # sentence = remove_stopwords(sentence)
    # sentence = stemming1(sentence)
    analyser = SentimentIntensityAnalyzer()
    s = analyser.polarity_scores(sentence)
    score = s['compound']
    if score >= 0.05:
        return 3
    elif score <= (-0.05):
        return 1
    else:
        return 2


@generator.route('/api/trust/generate', methods=['POST'])
# @login_required
def generate_trust():
    if not current_user.is_authenticated:
        root_url = request.url_root
        login_url = url_for('auth.login').strip("/")
        url = root_url + login_url
        return jsonify(
            status=False,
            message='login_required',
            url=str(url),
        )
    else:
        try:
            form = GneratorForm()
            if form.validate():
                product = Ecommerce_products.query.filter_by(
                    product_id=form.product.data).first()
                factor = Trust_factors.query.filter_by(
                    factor_id=form.factor.data).first()

                if not(product and factor):
                    return jsonify(status=False, message='Invalid Inputs')
                else:
                    if product.product_platform:
                        if product.product_name not in factor.factor_products:
                            message = '<i class="text-danger"> ' + factor.factor_name + '</i>' + ' is not activated on ' + \
                                '<i class="text-danger"> ' + product.product_name + \
                                '</i>' + ', please contact our help desk'
                            return jsonify(status=False, message=message)
                        else:
                            sentiments = Sentiments.query.filter_by(
                                sentiment_factor=factor.factor_id, sentiment_product=product.product_id).all()
                            if not sentiments:
                                message = 'Oops!, currently the trust factor named <i class="text-danger"> ' + factor.factor_name + \
                                    '</i> on the product named ' + '<i class="text-danger"> ' + \
                                    product.product_name + '</i> has no data for analysis'
                                return jsonify(status=False, message=message)
                            else:
                                response = dict()
                                platforms_on_product = product.product_platform
                                all_platforms_on_product = platforms_on_product.split(
                                    '_')
                                scores = [{'platform': k, 'count': 0, 'total': 0}
                                          for k in all_platforms_on_product]

                                for sentiment in sentiments:
                                    if sentiment.platform.platform_name in all_platforms_on_product:
                                        for score in scores:
                                            if sentiment.platform.platform_name == score.get('platform'):
                                                score['count'] += 1
                                                score['total'] += int(
                                                    sentiment.sentiment_score)
                                                break

                                for s in scores:
                                    if s['count'] > 0:
                                        expected = s['count'] * 3
                                        actual = s['total']
                                        percent = (actual/expected) * 100
                                        s['total'] = round(percent, 2)

                                scores = sorted(scores, key=itemgetter(
                                    'total'), reverse=True)
                                response["product"] = product.product_name
                                response["factor"] = factor.factor_name
                                response["data"] = scores

                                # print(scores)
                                return jsonify(
                                    status=True,
                                    message="Success",
                                    data=response
                                )
                    else:
                        message = '<i class="text-danger"> ' + product.product_name + '</i>' + \
                            ' has no any active e-commerce platform, please contact our help desk'
                        return jsonify(status=False, message=message)

            else:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">' +
                    str(form.errors) + '</p>'
                )
        except Exception as e:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + str(e) + '</p>'
            )
