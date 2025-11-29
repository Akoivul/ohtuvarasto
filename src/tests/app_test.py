import unittest
from app import app, warehouses, warehouse_id_counter


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        warehouses.clear()
        warehouse_id_counter[0] = 0

    def tearDown(self):
        warehouses.clear()
        warehouse_id_counter[0] = 0

    def test_index_empty(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)
        self.assertIn(b'No warehouses yet', response.data)

    def test_create_warehouse_get(self):
        response = self.client.get('/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse_post(self):
        response = self.client.post('/create', data={
            'name': 'Test Warehouse',
            'capacity': '100',
            'initial_balance': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertEqual(len(warehouses), 1)
        warehouse = warehouses[1]
        self.assertEqual(warehouse['name'], 'Test Warehouse')
        self.assertAlmostEqual(warehouse['varasto'].tilavuus, 100)
        self.assertAlmostEqual(warehouse['varasto'].saldo, 50)

    def test_view_warehouse(self):
        self.client.post('/create', data={
            'name': 'My Warehouse',
            'capacity': '200',
            'initial_balance': '75'
        })
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Warehouse', response.data)
        self.assertIn(b'75.0', response.data)
        self.assertIn(b'200.0', response.data)

    def test_view_warehouse_not_found(self):
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)

    def test_edit_warehouse_get(self):
        self.client.post('/create', data={
            'name': 'Edit Test',
            'capacity': '100',
            'initial_balance': '0'
        })
        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Warehouse', response.data)
        self.assertIn(b'Edit Test', response.data)

    def test_edit_warehouse_post(self):
        self.client.post('/create', data={
            'name': 'Original Name',
            'capacity': '100',
            'initial_balance': '30'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': 'Updated Name',
            'capacity': '150'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Name', response.data)
        self.assertAlmostEqual(warehouses[1]['varasto'].tilavuus, 150)

    def test_edit_warehouse_not_found(self):
        response = self.client.get('/warehouse/999/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)

    def test_add_to_warehouse(self):
        self.client.post('/create', data={
            'name': 'Add Test',
            'capacity': '100',
            'initial_balance': '20'
        })
        response = self.client.post('/warehouse/1/add', data={
            'amount': '30'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 50)

    def test_add_to_warehouse_not_found(self):
        response = self.client.post('/warehouse/999/add', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)

    def test_remove_from_warehouse(self):
        self.client.post('/create', data={
            'name': 'Remove Test',
            'capacity': '100',
            'initial_balance': '50'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 30)

    def test_remove_from_warehouse_not_found(self):
        response = self.client.post('/warehouse/999/remove', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)

    def test_delete_warehouse(self):
        self.client.post('/create', data={
            'name': 'Delete Test',
            'capacity': '100',
            'initial_balance': '0'
        })
        self.assertEqual(len(warehouses), 1)
        response = self.client.post('/warehouse/1/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_delete_warehouse_not_found(self):
        response = self.client.post('/warehouse/999/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)

    def test_index_with_warehouses(self):
        self.client.post('/create', data={
            'name': 'Warehouse 1',
            'capacity': '100',
            'initial_balance': '25'
        })
        self.client.post('/create', data={
            'name': 'Warehouse 2',
            'capacity': '200',
            'initial_balance': '100'
        })
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse 1', response.data)
        self.assertIn(b'Warehouse 2', response.data)
        self.assertNotIn(b'No warehouses yet', response.data)

    def test_capacity_usage_percentage(self):
        self.client.post('/create', data={
            'name': 'Usage Test',
            'capacity': '100',
            'initial_balance': '90'
        })
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'90.0%', response.data)
        self.assertIn(b'Almost full', response.data)

    def test_edit_reduces_capacity_below_balance(self):
        self.client.post('/create', data={
            'name': 'Reduce Test',
            'capacity': '100',
            'initial_balance': '80'
        })
        self.client.post('/warehouse/1/edit', data={
            'name': 'Reduce Test',
            'capacity': '50'
        })
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 50)
        self.assertAlmostEqual(warehouses[1]['varasto'].tilavuus, 50)
