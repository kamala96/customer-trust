import os
import pandas as pd
from customer_trust.forms import AddFactorForm, AddPlatformForm, AddProductForm, DeleteIDForm, ImportSentimentsForm
from customer_trust.generator import sentiment_scores
from . import UPLOAD_FOLDER, db
from flask import Blueprint, jsonify, render_template, request, g
from flask_login import login_required

from customer_trust.models import Ecommerce_platforms, Ecommerce_products, Sentiments, Trust_factors
from flask_wtf.csrf import CSRFProtect
from flask_expects_json import expects_json
from werkzeug.utils import secure_filename
import textwrap

from . import PORTAL_TITLE

csrf = CSRFProtect()

main = Blueprint("main", __name__)

# JSON SCHEMAS
schema_add_plt_to_prod = {
    'type': 'object',
    'properties': {
        'product': {'type': 'number'},
        "platform": {"type": "number"},
    },
    'required': ['product', 'platform']
}
schema_addDel_keyword_to_prod = {
    'type': 'object',
    'properties': {
        'product': {'type': 'number'},
        "keyword": {"type": "string"},
    },
    'required': ['product', 'keyword']
}
schema_delete_plt_from_prod = {
    'type': 'object',
    'properties': {
        'product': {'type': 'number'},
        "platform": {"type": "string"},
    },
    'required': ['product', 'platform']
}
schema_add_prod_to_factor = {
    'type': 'object',
    'properties': {
        'factor': {'type': 'number'},
        "product": {"type": "number"},
    },
    'required': ['factor', 'product']
}
schema_delete_prod_from_factor = {
    'type': 'object',
    'properties': {
        'factor': {'type': 'number'},
        "product": {"type": "string"},
    },
    'required': ['factor', 'product']
}
schema_addDel_keyword_to_factor = {
    'type': 'object',
    'properties': {
        'factor': {'type': 'number'},
        "keyword": {"type": "string"},
    },
    'required': ['factor', 'keyword']
}


@main.route('/')
def index():
    title = PORTAL_TITLE + ' - Home Page'
    factors = Trust_factors.query.order_by(
        Trust_factors.factor_name.asc()).all()
    products = Ecommerce_products.query.order_by(
        Ecommerce_products.product_name.asc()).all()
    return render_template(
        'index.html',
        title=title,
        factors=[factor.to_dict() for factor in factors],
        products=[product.to_dict() for product in products],
    )


@main.route('/resources')
@login_required
def resources():
    title = PORTAL_TITLE + ': Resources Page'
    return render_template(
        'resources.html',
        title=title,
        pltform=AddPlatformForm(),
        productform=AddProductForm(),
        factorform=AddFactorForm(),
        sentimentForm=ImportSentimentsForm())


@main.route('/api/platforms-data-short-display', methods=['GET'])
@login_required
def platforms_data_short_display():
    try:
        query = Ecommerce_platforms.query
        if query:
            return jsonify(
                status=True,
                message='Platforms found',
                data=[platforms.to_dict_select() for platforms in query]
            )
        else:
            return jsonify(
                status=False,
                message='Platforms not found',
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/platforms-data')
@login_required
def platforms_data():
    query = Ecommerce_platforms.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Ecommerce_platforms.platform_name.like(f'%{search}%'),
            Ecommerce_platforms.date_created.like(f'%{search}%')
        ))

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['platform_name', 'date_created']:
            col_name = 'platform_name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Ecommerce_platforms, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [platforms.to_dict() for platforms in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Ecommerce_platforms.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@main.route('/api/platforms-data/add', methods=['POST'])
@login_required
def add_platform():
    try:
        form = AddPlatformForm()
        if form.validate():
            platform = Ecommerce_platforms.query.filter_by(
                platform_name=form.platform_name.data).first()
            if not platform:
                slug = form.platform_name.data
                slug = slug.strip().lower().replace(" ", "_")

                new_platform = Ecommerce_platforms(
                    platform_name=form.platform_name.data, platform_desc=form.platform_description.data, platform_slug=slug)
                db.session.add(new_platform)
                db.session.commit()
                message = 'Success!, <i class="font-weight-bold text-success">' + \
                    form.platform_name.data + '</i> entry has been saved'
                return jsonify(
                    status=True,
                    message=message
                )
            else:
                return jsonify(
                    status=False,
                    message='Oops!, <i class="font-weight-bold text-danger">' +
                    form.platform_name.data + '</i> arleady exist'
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + form.id.errors + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/platforms-data/delete', methods=['POST'])
@login_required
def delete_platform():
    try:
        form = DeleteIDForm()
        if form.validate():
            platform = Ecommerce_platforms.query.get_or_404(form.id.data)
            if not platform:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, no such entry</p>'
                )
            else:
                platform_to_remove = platform.platform_name
                all_product_with_plt_to_remove = Ecommerce_products.query.filter(db.or_(
                    Ecommerce_products.product_platform.like(
                        f'%{platform_to_remove}%')
                ))
                for product in all_product_with_plt_to_remove:
                    prod = Ecommerce_products.query.filter_by(
                        product_id=product.product_id).first()
                    current_platforms = prod.product_platform
                    new_platforms = current_platforms.replace(
                        platform_to_remove, '')
                    new_platforms = new_platforms.replace('__', '_')
                    new_platforms = new_platforms.lstrip('_')
                    new_platforms = new_platforms.removesuffix('_')
                    prod.product_platform = new_platforms
                    db.session.commit()

                db.session.delete(platform)
                db.session.commit()
                # flash('Your post has been deleted!', 'success')
                # return redirect(url_fif not result:or('main.resources'))
                message = 'Success!, <i class="font-weight-bold text-success">' + \
                    platform.platform_name + '</i> entry has been removed'
                return jsonify(
                    status=True,
                    message=message
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + form.id.errors + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data-short-display', methods=['GET'])
@login_required
def products_data_short_display():
    try:
        query = Ecommerce_products.query
        if query:
            return jsonify(
                status=True,
                message='Platforms found',
                data=[products.to_dict_select() for products in query]
            )
        else:
            return jsonify(
                status=False,
                message='Products list not found',
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data')
@login_required
def products_data():
    query = Ecommerce_products.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Ecommerce_products.product_name.like(f'%{search}%'),
            Ecommerce_products.product_platform.like(f'%{search}%'),
            Ecommerce_products.date_created.like(f'%{search}%')
        ))

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['product_name', 'product_platform', 'date_created']:
            col_name = 'product_name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Ecommerce_products, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [products.to_dict() for products in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Ecommerce_products.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@main.route('/api/products-data/add', methods=['POST'])
@login_required
def add_product():
    try:
        form = AddProductForm()
        if form.validate():
            product = Ecommerce_products.query.filter_by(
                product_name=form.product_name.data).first()
            if not product:
                slug = form.product_name.data
                slug = slug.strip().lower().replace(" ", "_")

                new_product = Ecommerce_products(
                    product_name=form.product_name.data, product_desc=form.product_description.data, product_slug=slug)
                db.session.add(new_product)
                db.session.commit()
                message = 'Success!, <i class="font-weight-bold text-success">' + \
                    form.product_name.data + '</i> entry has been saved'
                return jsonify(
                    status=True,
                    message=message
                )
            else:
                return jsonify(
                    status=False,
                    message='Oops!, <i class="font-weight-bold text-danger">' +
                    form.product_name.data + '</i> arleady exist'
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + form.id.errors + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data/delete', methods=['POST'])
@login_required
def delete_product():
    try:
        form = DeleteIDForm()
        if form.validate():
            product = Ecommerce_products.query.get_or_404(form.id.data)
            if not product:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, no such entry</p>'
                )
            else:
                product_to_remove = product.product_name
                all_factors_with_prod_to_remove = Trust_factors.query.filter(db.or_(
                    Trust_factors.factor_products.like(
                        f'%{product_to_remove}%')
                ))
                for factor in all_factors_with_prod_to_remove:
                    _factor = Trust_factors.query.filter_by(
                        factor_id=factor.factor_id).first()
                    current_products = _factor.factor_products
                    new_products = current_products.replace(
                        product_to_remove, '')
                    new_products = new_products.replace('__', '_')
                    new_products = new_products.lstrip('_')
                    new_products = new_products.removesuffix('_')
                    _factor.factor_products = new_products
                    db.session.commit()

                db.session.delete(product)
                db.session.commit()
                message = 'Success!, <i class="font-weight-bold text-success">' + \
                    product.product_name + '</i> entry has been removed'
                return jsonify(
                    status=True,
                    message=message
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + form.id.errors + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data/add-platfrom', methods=['POST'])
@login_required
@expects_json(schema_add_plt_to_prod)
def product_add_platform():
    try:
        # product = Ecommerce_products.query.filter_by(product_id=g.data['product']).first()
        product = Ecommerce_products.query.get_or_404(g.data['product'])
        platform = Ecommerce_platforms.query.get_or_404(g.data['platform'])

        if not (product and platform):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_platforms = product.product_platform
            new_platform_input = platform.platform_name

            if not current_platforms:
                product.product_platform = new_platform_input
                db.session.commit()
                return jsonify(
                    status=True,
                    message='Congrats!, your changes has been saved successfully',
                )
            else:
                if new_platform_input not in current_platforms:
                    product.product_platform = new_platform_input + '_' + current_platforms
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Congrats!, your changes has been saved successfully',
                        data=current_platforms
                    )
                else:
                    return jsonify(
                        status=False,
                        message='<p class="text-danger"> Oops!, arleady exist </p>',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data/add-keyword', methods=['POST'])
@login_required
@expects_json(schema_addDel_keyword_to_prod)
def product_add_keyword():
    try:
        product = Ecommerce_products.query.get_or_404(g.data['product'])
        keyword = g.data['keyword']

        if not (product and keyword):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_keywords = product.product_keywords
            new_keyword_input = keyword.lower()
            new_keyword_input = new_keyword_input.replace('**', '')

            if not current_keywords:
                product.product_keywords = new_keyword_input
                db.session.commit()
                return jsonify(
                    status=True,
                    message='Congrats!, your changes has been saved successfully',
                )
            else:
                if new_keyword_input not in current_keywords:
                    product.product_keywords = new_keyword_input + '**' + current_keywords
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Congrats!, your changes has been saved successfully',
                        data=current_keywords
                    )
                else:
                    return jsonify(
                        status=False,
                        message='<p class="text-danger"> Oops!, arleady exist </p>',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data/delete-platfrom', methods=['POST'])
@login_required
@expects_json(schema_delete_plt_from_prod)
def product_delete_platform():
    try:
        product = Ecommerce_products.query.get_or_404(g.data['product'])
        platform = Ecommerce_platforms.query.filter_by(
            platform_name=g.data['platform']).first()

        if not (product and platform):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_platforms = product.product_platform
            platform_to_remove = platform.platform_name

            if not current_platforms:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                )
            else:
                if platform_to_remove not in current_platforms:
                    return jsonify(
                        status=False,
                        message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                    )
                else:
                    new_platforms = current_platforms.replace(
                        platform_to_remove, '')
                    new_platforms = new_platforms.replace('__', '_')
                    new_platforms = new_platforms.lstrip('_')
                    new_platforms = new_platforms.removesuffix('_')
                    product.product_platform = new_platforms
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Success!, <i class="font-weight-bold text-success">' +
                        platform_to_remove + '</i> entry has been removed',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/products-data/delete-keyword', methods=['POST'])
@login_required
@expects_json(schema_addDel_keyword_to_prod)
def product_delete_keyword():
    try:
        product = Ecommerce_products.query.get_or_404(g.data['product'])
        keyword = g.data['keyword']

        if not (product and keyword):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_keywords = product.product_keywords
            keyword_to_remove = keyword

            if not current_keywords:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                )
            else:
                if keyword_to_remove not in current_keywords:
                    return jsonify(
                        status=False,
                        message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                    )
                else:
                    new_keywords = current_keywords.replace(
                        keyword_to_remove, '')
                    new_keywords = new_keywords.replace('****', '**')
                    new_keywords = new_keywords.lstrip('**')
                    new_keywords = new_keywords.removesuffix('**')
                    product.product_keywords = new_keywords
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Success!, <i class="font-weight-bold text-success">' +
                        keyword_to_remove + '</i> entry has been removed',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/factors-data')
@login_required
def factors_data():
    query = Trust_factors.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Trust_factors.factor_name.like(f'%{search}%'),
            Trust_factors.factor_products.like(f'%{search}%'),
            Trust_factors.date_created.like(f'%{search}%')
        ))

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['factor_name', 'factor_products', 'date_created']:
            col_name = 'factor_name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Trust_factors, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [factors.to_dict() for factors in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Trust_factors.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@main.route('/api/factors-data/add', methods=['POST'])
@login_required
def add_factors():
    try:
        form = AddFactorForm()
        if form.validate():
            factor = Trust_factors.query.filter_by(
                factor_name=form.factor_name.data).first()
            if not factor:
                slug = form.factor_name.data
                slug = slug.strip().lower().replace(" ", "_")

                new_factor = Trust_factors(
                    factor_name=form.factor_name.data, factor_desc=form.factor_description.data, factor_slug=slug)
                db.session.add(new_factor)
                db.session.commit()
                message = 'Success!, <i class="font-weight-bold text-success">' + \
                    form.factor_name.data + '</i> entry has been saved'
                return jsonify(
                    status=True,
                    message=message
                )
            else:
                return jsonify(
                    status=False,
                    message='Oops!, <i class="font-weight-bold text-danger">' +
                    form.factor_name.data + '</i> arleady exist'
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + str(form.errors) + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/factors-data/delete', methods=['POST'])
@login_required
def delete_factor():
    try:
        form = DeleteIDForm()
        if form.validate():
            factor = Trust_factors.query.get_or_404(form.id.data)
            if not factor:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, no such entry</p>'
                )
            else:
                db.session.delete(factor)
                db.session.commit()
                # flash('Your post has been deleted!', 'success')
                # return redirect(url_fif not result:or('main.resources'))
                message = 'Success!, <i class="font-weight-bold text-success">' + \
                    factor.factor_name + '</i> entry has been removed'
                return jsonify(
                    status=True,
                    message=message
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + form.id.errors + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/factors-data/add-product', methods=['POST'])
@login_required
@expects_json(schema_add_prod_to_factor)
def factor_add_product():
    try:
        factor = Trust_factors.query.filter_by(
            factor_id=g.data['factor']).first()
        product = Ecommerce_products.query.filter_by(
            product_id=g.data['product']).first()
        # product = Ecommerce_products.query.get_or_404(g.data['product'])

        if not (factor and product):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_products = factor.factor_products
            new_product_input = product.product_name

            if not current_products:
                factor.factor_products = new_product_input
                db.session.commit()
                return jsonify(
                    status=True,
                    message='Success!, <i class="font-weight-bold text-success">' +
                    new_product_input + '</i> entry has been saved',
                )
            else:
                if new_product_input not in current_products:
                    factor.factor_products = new_product_input + '_' + current_products
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Success!, <i class="font-weight-bold text-success">' +
                        new_product_input + '</i> entry has been saved',
                    )
                else:
                    return jsonify(
                        status=False,
                        message='Oops!, <i class="font-weight-bold text-danger">' +
                        new_product_input + '</i> entry arleady exist </p>',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/factors-data/add-keyword', methods=['GET', 'POST'])
@login_required
@expects_json(schema_addDel_keyword_to_factor)
def factor_add_keyword():
    try:
        factor = Trust_factors.query.filter_by(
            factor_id=g.data['factor']).first()
        keyword = g.data['keyword']

        if not (factor and keyword):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_keywords = factor.factor_keywords
            new_keyword_input = keyword.lower()
            new_keyword_input = new_keyword_input.replace('**', '')

            if not current_keywords:
                factor.factor_keywords = new_keyword_input
                db.session.commit()
                return jsonify(
                    status=True,
                    message='Success!, <i class="font-weight-bold text-success">' +
                    new_keyword_input + '</i> entry has been saved',
                )
            else:
                if new_keyword_input not in current_keywords:
                    factor.factor_keywords = new_keyword_input + '**' + current_keywords
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Success!, <i class="font-weight-bold text-success">' +
                        new_keyword_input + '</i> entry has been saved',
                    )
                else:
                    return jsonify(
                        status=False,
                        message='Oops!, <i class="font-weight-bold text-danger">' +
                        new_keyword_input + '</i> entry arleady exist </p>',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/factors-data/delete-product', methods=['POST'])
@login_required
@expects_json(schema_delete_prod_from_factor)
def factor_delete_product():
    try:
        factor = Trust_factors.query.filter_by(
            factor_id=g.data['factor']).first()
        product = Ecommerce_products.query.filter_by(
            product_name=g.data['product']).first()

        if not (factor and product):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_products = factor.factor_products
            product_to_remove = product.product_name

            if not current_products:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                )
            else:
                if product_to_remove not in current_products:
                    return jsonify(
                        status=False,
                        message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                    )
                else:
                    new_products = current_products.replace(
                        product_to_remove, '')
                    new_products = new_products.replace('__', '_')
                    new_products = new_products.lstrip('_')
                    new_products = new_products.removesuffix('_')
                    factor.factor_products = new_products
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Success!, <i class="font-weight-bold text-success">' +
                        product_to_remove + '</i> entry has been removed',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/factors-data/delete-keyword', methods=['POST'])
@login_required
@expects_json(schema_addDel_keyword_to_factor)
def factor_delete_keyword():
    try:
        factor = Trust_factors.query.filter_by(
            factor_id=g.data['factor']).first()
        keyword = g.data['keyword']

        if not (factor and keyword):
            return jsonify(
                status=False,
                message='<p class="text-danger">Oops!, Invalid inputs</p>'
            )
        else:
            current_keywords = factor.factor_keywords
            keyword_to_remove = keyword

            if not current_keywords:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                )
            else:
                if keyword_to_remove not in current_keywords:
                    return jsonify(
                        status=False,
                        message='<p class="text-danger">Oops!, we gotta nothing to do.</p>',
                    )
                else:
                    new_keywords = current_keywords.replace(
                        keyword_to_remove, '')
                    new_keywords = new_keywords.replace('****', '**')
                    new_keywords = new_keywords.lstrip('**')
                    new_keywords = new_keywords.removesuffix('**')
                    factor.factor_keywords = new_keywords
                    db.session.commit()
                    return jsonify(
                        status=True,
                        message='Success!, <i class="font-weight-bold text-success">' +
                        keyword_to_remove + '</i> entry has been removed',
                    )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/sentiments-data')
@login_required
def sentiments_data():
    query = Sentiments.query
    # query = Sentiments.query.order_by(Sentiments.date_created.desc())
    # for row in query:
    #     print(row.factor.factor_desc)

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Sentiments.sentiment_text.like(f'%{search}%'),
            # Sentiments.sentiment_platform.like(f'%{search}%'),
            # Sentiments.sentiment_product.like(f'%{search}%'),
            # Sentiments.sentiment_factor.like(f'%{search}%'),
            Sentiments.date_created.like(f'%{search}%')
        ))

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['sentiment_text', 'sentiment_factor', 'sentiment_product', 'sentiment_platform', 'date_created']:
            col_name = 'sentiment_text'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Sentiments, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # print(json.dumps([
    #     {
    #         'sentiment_id': row.sentiment_id,
    #         'sentiment_text': row.sentiment_text,
    #         'sentiment_factor': row.factor.factor_name,
    #         'sentiment_product': row.product.product_name,
    #         'sentiment_platform': row.platform.platform_name,
    #         'date_created': row.date_created.strftime('%d %B, %Y %H:%M:%S'),
    #     } for row in query]))

    return {
        'data': [
            {
                'sentiment_id': row.sentiment_id,
                'sentiment_text': textwrap.shorten(row.sentiment_text, width=51, placeholder="..."),
                'sentiment_score': 'Positive' if row.sentiment_score == 3 else ('Neutral' if row.sentiment_score == 2 else 'Negative'),
                'sentiment_factor': row.factor.factor_name,
                'sentiment_product': row.product.product_name,
                'sentiment_platform': row.platform.platform_name,
                'date_created': row.date_created.strftime('%d %B, %Y %H:%M:%S'),
            }
            for row in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Sentiments.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@login_required
def parseFile(filePath):
    try:
        col_names = ['sentiment', 'factor', 'product', 'platform']
        fileData = pd.read_csv(filepath_or_buffer=filePath, encoding="utf-8")
        if set(col_names).issubset(fileData.columns):
            data_rows = []
            errors = []
            # Add score column
            fileData['score'] = fileData['sentiment'].apply(
                lambda x: sentiment_scores(x))
            # Loop through the Rows
            for i, row in fileData.iterrows():
                sentiment = row['sentiment']
                factor = row['factor']
                product = row['product']
                platform = row['platform']

                check_sentiment = Sentiments.query.filter_by(
                    sentiment_text=sentiment).first()
                check_factor = Trust_factors.query.filter_by(
                    factor_slug=factor).first()
                check_product = Ecommerce_products.query.filter_by(
                    product_slug=product).first()
                check_platform = Ecommerce_platforms.query.filter_by(
                    platform_slug=platform).first()

                if not check_factor:
                    error = ' Invalid factor entry => <i class="font-weight-bold text-danger">'+factor+'</i> :: Row: <i class="font-weight-bold text-danger">' + \
                        str(i+1) + '</i>'
                    errors.append(error)
                if not check_product:
                    error = ' Invalid product entry => <i class="font-weight-bold text-danger">'+product+'</i> :: Row: <i class="font-weight-bold text-danger">' + \
                        str(i+1) + '</i>'
                    errors.append(error)
                if not check_platform:
                    error = ' Invalid platform entry => <i class="font-weight-bold text-danger">'+platform+'</i> :: Row: <i class="font-weight-bold text-danger">' + \
                        str(i+1) + '</i>'
                    errors.append(error)
                if check_factor and check_product and check_platform:
                    check_sentiment = Sentiments.query.filter_by(sentiment_text=sentiment, sentiment_factor=check_factor.factor_id,
                                                                 sentiment_product=check_product.product_id, sentiment_platform=check_platform.platform_id).first()
                    if check_sentiment:
                        error = '<i class="font-weight-bold text-danger">Arleady exist</i> :: Row: <i class="font-weight-bold text-danger">' + \
                            str(i+1) + '</i>'
                        errors.append(error)
                    else:
                        sentiment = row['sentiment']
                        new_data = Sentiments(sentiment_text=sentiment.lower(), sentiment_score=row['score'], sentiment_factor=check_factor.factor_id,
                                              sentiment_product=check_product.product_id, sentiment_platform=check_platform.platform_id)
                        data_rows.append(new_data)
            if data_rows:
                db.session.add_all(data_rows)
                db.session.commit()
                return jsonify(
                    status=True,
                    message='<p class="font-weight-bold text-success">Success, but check if the report below have some issues. If not, then your import was OK!</p>',
                    extra=errors,
                )
            else:
                return jsonify(
                    status=False,
                    message='<p class="font-weight-bold text-danger"> No data has been processed</p>',
                    extra=errors,
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger"> Oops!, please use a valid template file</p>'
            )
    except FileNotFoundError as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )
    except pd.errors.EmptyDataError:
        return jsonify(
            status=False,
            message='<p class="text-danger">Empty data set</p>'
        )
    except pd.errors.ParserError as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/sentiments-data/import-data', methods=['POST'])
@login_required
def import_sentiments():
    try:
        form = ImportSentimentsForm()
        if form.validate():
            f = form.document.data
            filename = secure_filename(f.filename)
            name, ext = filename.rsplit('.', 1)
            new_filename = 'sentiments.' + ext
            full_path = os.path.join(UPLOAD_FOLDER, 'sentiments', new_filename)
            f.save(full_path)
            return parseFile(full_path)
            # platform = Ecommerce_platforms.query.filter_by(
            #     platform_name=form.platform_name.data).first()
            # if not platform:
            #     slug = form.platform_name.data
            #     slug = slug.strip().lower().replace(" ", "_")

            #     new_platform = Ecommerce_platforms(
            #         platform_name=form.platform_name.data, platform_desc=form.platform_description.data, platform_slug=slug)
            #     db.session.add(new_platform)
            #     db.session.commit()
            #     message = 'Success!, <i class="font-weight-bold text-success">' + \
            #         form.platform_name.data + '</i> entry has been saved'
            #     return jsonify(
            #         status=True,
            #         message=message
            #     )
            # else:
            #     return jsonify(
            #         status=False,
            #         message='Oops!, <i class="font-weight-bold text-danger">' +
            #         form.platform_name.data + '</i> arleady exist'
            #     )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' +
                str(form.document.errors) + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )


@main.route('/api/sentiments-data/delete', methods=['POST'])
@login_required
def delete_sentiment():
    try:
        form = DeleteIDForm()
        if form.validate():
            sentiment = Sentiments.query.filter_by(
                sentiment_id=form.id.data).first()
            if not sentiment:
                return jsonify(
                    status=False,
                    message='<p class="text-danger">Oops!, no such entry</p>'
                )
            else:
                db.session.delete(sentiment)
                db.session.commit()
                mysentiment = sentiment.sentiment_text
                shortened_sentiment = (
                    mysentiment[:90] + '..') if len(mysentiment) > 90 else mysentiment
                message = 'Success!, sentiment <i class="font-weight-bold text-info">\"' + \
                    shortened_sentiment + '\"</i> entry has been removed'
                return jsonify(
                    status=True,
                    message=message
                )
        else:
            return jsonify(
                status=False,
                message='<p class="text-danger">' + form.id.errors + '</p>'
            )
    except Exception as e:
        return jsonify(
            status=False,
            message='<p class="text-danger">' + str(e) + '</p>'
        )
