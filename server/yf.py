import yfinance as yf
import csv
from db import StockFinancialData, db
from app import app

# stock = yf.Ticker('GOOGL')
# # dividend_yield = stock.info['dividendYield']
# # print(dividend_yield)
# print(stock.info)

stocks_list = []


# Replace 'your_file.csv' with the actual name of your CSV file
with open('/Users/rodrigocruzsouza/Downloads/stocks_listed_us - listed_cos.csv', 'r') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        stocks_list.append({
            "ticker_symbol": row['ticker_symbol'],
            "company_name": row['company_name'],
            "stock_exchange": row['stock_exchange']
        })

with app.app_context():
    for stock_data in stocks_list:
        try:
            stock = yf.Ticker(stock_data["ticker_symbol"])
            
            # Get stock info
            sector = stock.info.get('sector')
            # if not sector:  # Skip if there is no data available for this stock
            #     raise ValueError('No data available')
            
            dividend_yield = stock.info.get('dividendYield')
            trailing_pe_ratio = stock.info.get('trailingPE')
            forward_pe_ratio = stock.info.get('forwardPE')
            market_cap = stock.info.get('marketCap')
            fifty_two_week_low = stock.info.get('fiftyTwoWeekLow')
            fifty_two_week_high = stock.info.get('fiftyTwoWeekHigh')
            enterprise_to_revenue_ratio = stock.info.get('enterpriseToRevenue')
            enterprise_to_ebitda_ratio = stock.info.get('enterpriseToEbitda')
            ebitda = stock.info.get('ebitda'),
            ebitda_margin = stock.info.get('ebitdaMargins'),
            net_income_margin = stock.info.get('profitMargins'),
            total_revenue = stock.info.get('totalRevenue'),
            return_on_equity = stock.info.get('returnOnEquity'),
            earnings_growth = stock.info.get('earningsGrowth'),
            revenue_growth = stock.info.get('revenueGrowth'),
            gross_margin = stock.info.get('grossMargins'),
            operating_margin = stock.info.get('operatingMargins')

            # Create StockFinancialData object with fetched data
            stock_financial_data = StockFinancialData(
                ticker_symbol=stock_data["ticker_symbol"],
                company_name=stock_data["company_name"],
                stock_exchange=stock_data["stock_exchange"],
                sector=sector,
                dividend_yield=dividend_yield,
                trailing_pe_ratio=trailing_pe_ratio,
                forward_pe_ratio=forward_pe_ratio,
                market_cap=market_cap,
                fifty_two_week_low=fifty_two_week_low,
                fifty_two_week_high=fifty_two_week_high,
                enterprise_to_revenue_ratio=enterprise_to_revenue_ratio,
                enterprise_to_ebitda_ratio=enterprise_to_ebitda_ratio,
                ebitda=ebitda,
                ebitda_margin=ebitda_margin,
                net_income_margin=net_income_margin,
                total_revenue=total_revenue,
                return_on_equity=return_on_equity,
                earnings_growth=earnings_growth,
                revenue_growth=revenue_growth,
                gross_margin=gross_margin,
                operating_margin=operating_margin,
            )
            # Add object to database session and commit
            db.session.add(stock_financial_data)
            db.session.commit()
        
        except Exception as e:
            print(f"Could not fetch data for {stock_data['ticker_symbol']}: {e}")
