from flask import Blueprint, jsonify, request
from flask_security import auth_required
import openfoodfacts
import barcodenumber
from models import db, Item, SubItem


bp_api_v1_items = Blueprint("bp_api_v1_items", __name__)


@bp_api_v1_items.route("/api/v1/items/new/search", methods=["GET"])
@auth_required()
def search():
    """
    Search an item from OpenFoodFacts
    ---
    tags:
        - Items
            parameters:
    - name: q
          in: query
          type: string
          required: true
          description: search string
    responses:
        200:
            description: returns result of OpenFoodFacts search

    """

    query = request.args.get("q", None)
    if not query:
        return jsonify({"count": 0, "results": []})

    is_barcode = barcodenumber.check_code("ean13", query.strip())

    results = openfoodfacts.products.search(query)

    if results["count"] == 0 and is_barcode:
        # try a match from barcode
        product = openfoodfacts.products.get_product(query)
        if product["status"] == 1:
            results = {"count": 1, "page": 1, "page_size": 20, "products": [product["product"]]}
        else:
            results = {"count": 0, "page": 1, "page_size": 20, "products": []}

    return jsonify(
        {"count": int(results["count"]), "page_size": int(results["page_size"]), "results": results["products"]}
    )


@bp_api_v1_items.route("/api/v1/items/new", methods=["POST"])
@auth_required()
def add():
    """
    Add an item into the shelf
    ---
    tags:
        - Items
    responses:
        200:
            description: item has been added

    """
    datas = request.get_json()

    openfoodfactsid = datas.get('openFoodFactsId', None)
    if not openfoodfactsid:
        return jsonify({"error": "no_openfoodfacts_id"}), 400

    qty = datas.get('qty', 1)
    if int(qty) <= 0:
        qty = 1

    expiry = datas.get('expiry', None)

    off = openfoodfacts.products.get_product(openfoodfactsid)
    if off["status"] == 1:
        off = off["product"]
    else:
        off = None

    # Try to get item matching OFF ID
    item = Item.query.filter(Item.openfoodfacts_id == openfoodfactsid).first()
    if not item:
        # create it
        item = Item(openfoodfacts_id=openfoodfactsid, openfoodfacts_product=off)
        db.session.add(item)
        subitem = SubItem(qty=qty, expiry=expiry, item=item)
        db.session.add(subitem)
    else:
        # just add another sub item
        subitem = SubItem(qty=qty, expiry=expiry, item=item)
        db.session.add(subitem)

    db.session.commit()

    return jsonify({"state": "added", "item_id": item.flake_id})


@bp_api_v1_items.route("/api/v1/items", methods=["GET"])
@auth_required()
def shelf():
    """
    Get all items of the shelf
    ---
    tags:
        - Items
    parameters:
        - name: page
          in: query
          type: integer
          description: page number
    responses:
        200:
            description: list of items

    """
    page = int(request.args.get("page", 1))
    q = Item.query.order_by(Item.openfoodfacts_product['product_name']).paginate(page=page, per_page=20)

    results = []
    for i in q.items:
        qty_total = 0
        expiries = []
        for si in i.sub_items:
            qty_total += si.qty
            if si.expiry:
                expiries.append(si.expiry.strftime('%a %d/%m/%y'))
        expiries = list(set(expiries))  # dedup
        results.append({
            'item': i.openfoodfacts_product['product_name'],
            'flake_id': i.flake_id,
            'qty': qty_total,
            'expiries': expiries,
            'openfoodfacts_product': i.openfoodfacts_product
        })

    return jsonify({"page": page, "page_size": 20, "count": q.total, "items": results, "total_pages": q.pages})
