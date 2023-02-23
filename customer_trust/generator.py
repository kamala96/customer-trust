# import string
from flask import Blueprint, jsonify, request, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user
from customer_trust.forms import GeneratorForm
from customer_trust.models import Ecommerce_products, Ecommerce_platforms, Sentiments, Trust_factors
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# import re
# import nltk
from operator import itemgetter

# nltk.download('stopwords')

csrf = CSRFProtect()

# stopword = nltk.corpus.stopwords.words('english')
# ps = nltk.PorterStemmer()

generator = Blueprint('generator', __name__)


# @login_required
# def clean(text):
#     text = re.sub('https?://\S+|www\.\S+', '', text)
#     text = re.sub(r'\s+', ' ', text, flags=re.I)
#     text = re.sub('\[.*?\]', '', text)
#     text = re.sub('\n', '', text)
#     text = re.sub('\w*\d\w*', '', text)
#     text = re.sub('<.*?>+', '', text)
#     text = str(text).lower()
#     text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
#     return text


# @login_required
# def tokenization(text):
#     pattern = r'\W+'
#     text = re.split(pattern, text)
#     return text


# @login_required
# def remove_stopwords(text):
#     text = [word for word in text if word not in stopword]
#     return text


# @login_required
# def stemming1(text):
#     text = [ps.stem(word) for word in text]
#     return text


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
            form = GeneratorForm()
            if form.validate():
                product = Ecommerce_products.query.filter_by(
                    product_id=form.product.data).first()

                if not (product):
                    return jsonify(status=False, message='Product not found')
                else:
                    if product.product_platform:
                        factors = Trust_factors.query.all()
                        if not factors:
                            message = '<i class="text-danger"> No any added trust factor, please contact our help desk team'
                            return jsonify(status=False, message=message)
                        else:
                            response = {
                                'factors': [],
                                'product': product.product_name,
                                'overall': ''
                            }
                            overall = {}
                            for factor in factors:
                                product_name = product.product_name
                                factor_active_products = factor.factor_products.split(
                                    "_")
                                if product_name not in factor_active_products:
                                    # Not in active in this factor
                                    print(product_name +
                                          'is not active in ' + factor.factor_name)
                                else:
                                    factor_id = factor.factor_id
                                    factor_rating = str(
                                        factor.factor_rating)+'0'
                                    factor_rating = int(factor_rating)
                                    product_id = product.product_id
                                    platforms = product.product_platform.split(
                                        "_")
                                    # initializing factor response
                                    factor_resp = {factor.factor_slug: []}

                                    for platform in platforms:
                                        search = platform.strip().lower().replace(" ", "_")
                                        pl = Ecommerce_platforms.query.filter_by(
                                            platform_slug=search).first()
                                        platform_id = pl.platform_id
                                        if platform_id is None:
                                            pass
                                        else:
                                            # checking if platform is available in overall data
                                            spn = pl.platform_name
                                            if overall.get(spn) is not None:
                                                pass
                                            else:
                                                overall[spn] = 0
                                            # initializing platform response
                                            plt_data = {
                                                pl.platform_name: {
                                                    'count': 0,  'score': 0, 'percent': 0, 'trust': 0
                                                }
                                            }

                                            sentiments = Sentiments.query.filter_by(
                                                sentiment_factor=factor_id, sentiment_product=product_id, sentiment_platform=platform_id
                                            ).all()
                                            if not sentiments:
                                                print(
                                                    f'Log: {product_name} on (Factor-{factor.factor_name}) and (Platform-{pl.platform_name}) has got no any sentiment')
                                            else:
                                                # initializing sentiments response to platform
                                                sentiments_count = 0
                                                sentiments_score = 0
                                                percent = 0
                                                trust = 0

                                                for sentiment in sentiments:
                                                    sentiments_count += 1
                                                    sentiments_score += int(
                                                        sentiment.sentiment_score)

                                                if sentiments_count > 0:
                                                    expected = sentiments_count * 3
                                                    actual = sentiments_score
                                                    percent = (
                                                        actual / expected) * 100
                                                    percent = round(
                                                        percent, 2)
                                                    trust = round(
                                                        (actual/expected) * factor_rating)

                                                # adding final sentiments response to platform
                                                plt_data[pl.platform_name]['count'] = sentiments_count
                                                plt_data[pl.platform_name]['score'] = sentiments_score
                                                plt_data[pl.platform_name]['percent'] = percent
                                                plt_data[pl.platform_name]['trust'] = trust

                                                # adding overall score
                                                overall[spn] += trust

                                        # appending final platform response
                                        factor_resp[factor.factor_slug].append(
                                            plt_data)

                                # appending final factor response
                                response['factors'].append(factor_resp)

                            # print(overall)
                            # convert overall results to percentage
                            total = sum(overall.values())
                            for k, value in overall.items():
                                k_percent = round((value / total) * 100)
                                overall[k] = k_percent
                            # sort overall by value and then key
                            # print(overall)
                            overall = dict(
                                sorted(overall.items(), key=lambda item: item[1], reverse=True))
                            # print(overall)
                            # assign overall trust to the response payload
                            response['overall'] = overall
                        return jsonify(
                            status=True,
                            message="Success",
                            data=response,
                        )
                    else:
                        message = '<i class="text-danger"> ' + product.product_name + '</i>' + \
                            ' has got no any active e-commerce platform, please contact our help desk team'
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
                message='<p class="text-danger">' + str(e) + '</p>')


# def generate_trust():
#     if not current_user.is_authenticated:
#         root_url = request.url_root
#         login_url = url_for('auth.login').strip("/")
#         url = root_url + login_url
#         return jsonify(
#             status=False,
#             message='login_required',
#             url=str(url),
#         )
#     else:
#         try:
#             form = GeneratorForm()
#             if form.validate():
#                 product = Ecommerce_products.query.filter_by(
#                     product_id=form.product.data).first()
#                 factor = Trust_factors.query.filter_by(
#                     factor_id=form.factor.data).first()

#                 if not(product and factor):
#                     return jsonify(status=False, message='Invalid Inputs')
#                 else:
#                     if product.product_platform:
#                         if factor.factor_products is None:
#                             message = '<i class="text-danger"> ' + factor.factor_name + '</i>' + \
#                                 ' has no any active e-commerce product, please contact our help desk team'
#                             return jsonify(status=False, message=message)
#                         else:
#                             print('---Here1')
#                             if product.product_name not in factor.factor_products:
#                                 message = '<i class="text-danger"> ' + factor.factor_name + '</i>' + ' is not activated on ' + \
#                                     '<i class="text-danger"> ' + product.product_name + \
#                                     '</i>' + ', please contact our help desk'
#                                 return jsonify(status=False, message=message)
#                             else:
#                                 print('---Here2')
#                                 sentiments = Sentiments.query.filter_by(
#                                     sentiment_factor=factor.factor_id, sentiment_product=product.product_id).all()
#                                 if not sentiments:
#                                     message = 'Oops!, currently the trust factor named <i class="text-danger"> ' + factor.factor_name + \
#                                         '</i> on the product named ' + '<i class="text-danger"> ' + \
#                                         product.product_name + '</i> has no data for analysis'
#                                     return jsonify(status=False, message=message)
#                                 else:
#                                     response = dict()
#                                     platforms_on_product = product.product_platform
#                                     all_platforms_on_product = platforms_on_product.split(
#                                         '_')
#                                     scores = [{'platform': k, 'count': 0, 'total': 0}
#                                               for k in all_platforms_on_product]

#                                     for sentiment in sentiments:
#                                         if sentiment.platform.platform_name in all_platforms_on_product:
#                                             for score in scores:
#                                                 if sentiment.platform.platform_name == score.get('platform'):
#                                                     score['count'] += 1
#                                                     score['total'] += int(
#                                                         sentiment.sentiment_score)
#                                                     break

#                                     for s in scores:
#                                         if s['count'] > 0:
#                                             expected = s['count'] * 3
#                                             actual = s['total']
#                                             percent = (actual/expected) * 100
#                                             s['total'] = round(percent, 2)

#                                     scores = sorted(scores, key=itemgetter(
#                                         'total'), reverse=True)
#                                     response["product"] = product.product_name
#                                     response["factor"] = factor.factor_name
#                                     response["data"] = scores

#                                     # print(scores)
#                                     return jsonify(
#                                         status=True,
#                                         message="Success",
#                                         data=response
#                                     )
#                     else:
#                         message = '<i class="text-danger"> ' + product.product_name + '</i>' + \
#                             ' has no any active e-commerce platform, please contact our help desk'
#                         return jsonify(status=False, message=message)

#             else:
#                 return jsonify(
#                     status=False,
#                     message='<p class="text-danger">' +
#                     str(form.errors) + '</p>'
#                 )
#         except Exception as e:
#             return jsonify(
#                 status=False,
#                 message='<p class="text-danger">' + str(e) + '</p>')
