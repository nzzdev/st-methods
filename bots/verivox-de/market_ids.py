#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 16:12:07 2022

@author: florianseliger
"""

from datetime import date
import pandas as pd

date = pd.to_datetime(date.today())


# Market IDs from https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5429405

if (date >= pd.to_datetime('2026-01-01')) & (date <= pd.to_datetime('2026-01-31')):
    market_id = "6117262"
if (date >= pd.to_datetime('2026-02-01')) & (date <= pd.to_datetime('2026-02-28')):
    market_id = "6142642"
if (date >= pd.to_datetime('2026-03-01')) & (date <= pd.to_datetime('2026-03-31')):
    market_id = "6164787"
if (date >= pd.to_datetime('2026-04-01')) & (date <= pd.to_datetime('2026-04-30')):
    market_id = "6187520"
if (date >= pd.to_datetime('2026-05-01')) & (date <= pd.to_datetime('2026-05-31')):
    market_id = "6214891"
if (date >= pd.to_datetime('2026-06-01')) & (date <= pd.to_datetime('2026-06-30')):
    market_id = "6243134"
if (date >= pd.to_datetime('2026-07-01')) & (date <= pd.to_datetime('2026-07-31')):
    market_id = "6277386"
if (date >= pd.to_datetime('2026-08-01')) & (date <= pd.to_datetime('2026-08-31')):
    market_id = "6277387"
if (date >= pd.to_datetime('2026-09-01')) & (date <= pd.to_datetime('2026-09-30')):
    market_id = "6277388"
if (date >= pd.to_datetime('2026-10-01')) & (date <= pd.to_datetime('2026-10-31')):
    market_id = "6277389"
if (date >= pd.to_datetime('2026-11-01')) & (date <= pd.to_datetime('2026-11-30')):
    market_id = "6277390"
if (date >= pd.to_datetime('2026-12-01')) & (date <= pd.to_datetime('2026-12-31')):
    market_id = "6277391"
if (date >= pd.to_datetime('2027-01-01')) & (date <= pd.to_datetime('2027-01-31')):
    market_id = "6277392"
if (date >= pd.to_datetime('2027-02-01')) & (date <= pd.to_datetime('2027-02-28')):
    market_id = "6277393"