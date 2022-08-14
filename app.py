from customer_trust import create_app, db
from flask_statistics import Statistics
from flask_login import current_user
from flask import redirect, url_for
from customer_trust.auth import check_if_user_is_admin

from customer_trust.models import Request

app = create_app()


statistics = Statistics(app, db, Request, check_if_user_is_admin)

if __name__ == "__main__":
    app.run(debug=True)
