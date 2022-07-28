from customer_trust.forms import AddPlatformForm, DeleteIDForm
from . import db
from flask import Blueprint, jsonify, flash, redirect, render_template, request, url_for
from flask_login import login_required

from customer_trust.models import Ecommerce_platforms, Ecommerce_products, Trust_facors
from flask_wtf.csrf import CSRFProtect

from . import PORTAL_TITLE

csrf = CSRFProtect()

main = Blueprint("main", __name__)


@main.route('/')
def index():
    title = PORTAL_TITLE + ' - Home Page'
    return render_template('index.html', title=title)


@main.route('/resources')
@login_required
def resources():
    # platforms = Ecommerce_platforms.query
    products = Ecommerce_products.query
    trust_factors = Trust_facors.query
    title = PORTAL_TITLE + ' - Resources Page'
    pltform = AddPlatformForm()
    return render_template(
        'resources.html',
        title=title,
        products=products,
        trust_factors=trust_factors,
        pltform=pltform)


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
                    message='No such entry'
                )
            else:
                db.session.delete(platform)
                db.session.commit()
                # flash('Your post has been deleted!', 'success')
                # return redirect(url_fif not result:or('main.resources'))
                message = 'Success!, <i>' + platform.platform_name + '</i> entry has been removed'
                return jsonify(
                    status=True,
                    message=message
                )
        else:
            return jsonify(
                status=False,
                message=form.id.errors
            )
    except Exception as e:
        return jsonify(
            status=False,
            message=str(e)
        )


@main.route('/api/platforms-data/add', methods=['POST'])
@login_required
def add_platform():
    try:
        form = AddPlatformForm()
        if form.validate():
            platform = Ecommerce_platforms.query.filter_by(
                platform_name=form.platform_name.data).first()
            if platform:
                return jsonify(
                    status=False,
                    message='This entry arleady exist'
                )
            else:
                slug = form.platform_name.data
                slug = slug.strip().lower().replace(" ", "_")

                new_platform = Ecommerce_platforms(
                    platform_name=form.platform_name.data, platform_desc=form.platform_description.data, platform_slug=slug)
                db.session.add(new_platform)
                db.session.commit()
                message = 'Success!, <i>' + form.platform_name.data + '</i> entry has been saved'
                return jsonify(
                    status=True,
                    message=message
                )
        else:
            return jsonify(
                status=False,
                message=form.id.errors
            )
    except Exception as e:
        return jsonify(
            status=False,
            message=str(e)
        )
