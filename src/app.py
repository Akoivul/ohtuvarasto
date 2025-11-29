from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto


app = Flask(__name__)

warehouses = {}
warehouse_id_counter = [0]


def get_next_id():
    warehouse_id_counter[0] += 1
    return warehouse_id_counter[0]


@app.route('/')
def index():
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))
    warehouse = warehouses[warehouse_id]
    return render_template('warehouse.html',
                           warehouse=warehouse,
                           warehouse_id=warehouse_id)


@app.route('/create', methods=['GET', 'POST'])
def create_warehouse():
    if request.method == 'POST':
        name = request.form.get('name', 'Unnamed')
        capacity = float(request.form.get('capacity', 100))
        initial_balance = float(request.form.get('initial_balance', 0))
        warehouse_id = get_next_id()
        warehouses[warehouse_id] = {
            'name': name,
            'varasto': Varasto(capacity, initial_balance)
        }
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))
    return render_template('create.html')


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))
    warehouse = warehouses[warehouse_id]
    if request.method == 'POST':
        warehouse['name'] = request.form.get('name', warehouse['name'])
        new_capacity = float(request.form.get('capacity',
                                              warehouse['varasto'].tilavuus))
        warehouse['varasto'].tilavuus = max(0.0, new_capacity)
        warehouse['varasto'].saldo = min(warehouse['varasto'].saldo,
                                         warehouse['varasto'].tilavuus)
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))
    return render_template('edit.html',
                           warehouse=warehouse,
                           warehouse_id=warehouse_id)


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_to_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))
    amount = float(request.form.get('amount', 0))
    warehouses[warehouse_id]['varasto'].lisaa_varastoon(amount)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_from_warehouse(warehouse_id):
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))
    amount = float(request.form.get('amount', 0))
    warehouses[warehouse_id]['varasto'].ota_varastosta(amount)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    if warehouse_id in warehouses:
        del warehouses[warehouse_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
