import importlib.util
import tempfile
import unittest
from pathlib import Path
import pandas as pd

MODULE = Path(__file__).resolve().parents[2] / "python-ai" / "chatbot" / "queries.py"
spec = importlib.util.spec_from_file_location("retailai_queries", MODULE)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

class QueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for p in q.SOURCES.values():
            (self.root / p).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([
            ["2023-09-14","S001","P0001","Food","North",10,5,"Sunny",True,5,"Autumn"],
            ["2023-09-15","S001","P0001","Food","North",8,7,"Rainy",False,0,"Autumn"],
            ["2023-09-14","S002","P0001","Food","South",20,2,"Sunny",False,0,"Autumn"],
            ["2023-09-14","S001","P0002","Home","North",4,9,"Sunny",True,10,"Autumn"],
        ], columns=["Date","Store ID","Product ID","Category","Region","Inventory Level","Units Sold","Weather Condition","Holiday/Promotion","Discount","Seasonality"]).to_csv(self.root/q.SOURCES["inventory"], index=False)
        pd.DataFrame([["2023-09-14","S001","P0001",5,6.5]],columns=["Date","Store ID","Product ID","Actual Units Sold","Forecast Units Sold"]).to_csv(self.root/q.SOURCES["forecast"],index=False)
        pd.DataFrame([["2023-09-14","S001","P0001","REORDER_NOW",12]],columns=["Date","Store ID","Product ID","recommendation_status","suggested_order_quantity"]).to_csv(self.root/q.SOURCES["reorder"],index=False)
        pd.DataFrame([["2023-09-14","S001","P0001","STOCKOUT_RISK",1.2]],columns=["Date","Store ID","Product ID","stockout_status","days_of_cover"]).to_csv(self.root/q.SOURCES["stockout"],index=False)
    def tearDown(self): self.tmp.cleanup()
    def test_inventory_filters_store_product(self):
        self.assertEqual(len(q.inventory_level(store_id="s001",product_id="p0001",data_dir=self.root)),2)
    def test_inventory_as_of_date(self):
        self.assertEqual(len(q.inventory_level(store_id="S001",as_of_date="2023-09-15",data_dir=self.root)),1)
    def test_sales_summary_observed_units(self):
        self.assertEqual(q.sales_summary(store_id="S001",data_dir=self.root)["units_sold"],21)
    def test_top_products_ranked(self):
        result = q.top_selling_products(
            store_id="S001",
            limit=2,
            data_dir=self.root
        )
        self.assertEqual(result.iloc[0]["Product ID"], "P0001")
        self.assertEqual(result.iloc[1]["Product ID"], "P0002")
    def test_forecast_requires_ids(self):
        with self.assertRaises(q.QueryDataError): q.demand_forecast(store_id="S001",product_id="",data_dir=self.root)
    def test_forecast_scoped_to_pair(self):
        self.assertEqual(len(q.demand_forecast(store_id="S001",product_id="P0001",data_dir=self.root)),1)
    def test_reorder_result(self):
        self.assertEqual(q.reorder_recommendations(store_id="S001",product_id="P0001",data_dir=self.root).iloc[0]["recommendation_status"],"REORDER_NOW")
    def test_stockout_result(self):
        self.assertEqual(q.stockout_status(store_id="S001",product_id="P0001",data_dir=self.root).iloc[0]["stockout_status"],"STOCKOUT_RISK")
    def test_factor_analysis(self):
        self.assertIn("Holiday/Promotion",q.sales_factor_analysis(factor="promotion",store_id="S001",data_dir=self.root).columns)
    def test_unknown_factor_rejected(self):
        with self.assertRaises(q.QueryDataError): q.sales_factor_analysis(factor="profit",data_dir=self.root)
    def test_reversed_dates_rejected(self):
        with self.assertRaises(q.QueryDataError): q.sales_summary(start_date="2023-09-20",end_date="2023-09-01",data_dir=self.root)
    def test_limit_maximum(self):
        with self.assertRaises(q.QueryDataError): q.top_selling_products(limit=101,data_dir=self.root)
    def test_missing_file_error(self):
        with self.assertRaises(q.QueryDataError): q.inventory_level(data_dir=self.root/"missing")
    def test_data_availability_not_live(self):
        result=q.data_availability(self.root)
        self.assertFalse(result["live_data_connected"])
        self.assertTrue(result["inventory"]["available"])

if __name__ == "__main__": unittest.main()
