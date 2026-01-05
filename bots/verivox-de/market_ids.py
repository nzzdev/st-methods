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

if (date >= pd.to_datetime('2022-09-01')) & (date <= pd.to_datetime('2022-09-30')):
    market_id = '5429405'

# from https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5439161

if (date >= pd.to_datetime('2022-10-01')) & (date <= pd.to_datetime('2022-10-31')):
    market_id = "5439161"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5460494

if (date >= pd.to_datetime('2022-11-01')) & (date <= pd.to_datetime('2022-11-30')):
    market_id = "5460494"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5477499

if (date >= pd.to_datetime('2022-12-01')) & (date <= pd.to_datetime('2022-12-31')):
    market_id = "5477499"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5493476

if (date >= pd.to_datetime('2023-01-01')) & (date <= pd.to_datetime('2023-01-31')):
    market_id = "5493476"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5508663

if (date >= pd.to_datetime('2023-02-01')) & (date <= pd.to_datetime('2024-02-28')):
    market_id = "5508663"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5519350

if (date >= pd.to_datetime('2023-03-01')) & (date <= pd.to_datetime('2023-03-31')):
    market_id = "5519350"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5544919

if (date >= pd.to_datetime('2023-04-01')) & (date <= pd.to_datetime('2023-04-30')):
    market_id = "5544919"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5564180

if (date >= pd.to_datetime('2023-05-01')) & (date <= pd.to_datetime('2023-05-31')):
    market_id = "5564180"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5577209

if (date >= pd.to_datetime('2023-06-01')) & (date <= pd.to_datetime('2023-06-30')):
    market_id = "5577209"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5586285

if (date >= pd.to_datetime('2023-07-01')) & (date <= pd.to_datetime('2023-07-31')):
    market_id = "5586285"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5600523

if (date >= pd.to_datetime('2023-08-01')) & (date <= pd.to_datetime('2023-08-31')):
    market_id = "5600523"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5614690

if (date >= pd.to_datetime('2023-09-01')) & (date <= pd.to_datetime('2023-09-30')):
    market_id = "5614690"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5640640

if (date >= pd.to_datetime('2023-10-01')) & (date <= pd.to_datetime('2023-10-31')):
    market_id = "5640640"

# https://www.theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5667240

if (date >= pd.to_datetime('2023-11-01')) & (date <= pd.to_datetime('2023-11-29')):
    market_id = "5667240"

if (date >= pd.to_datetime('2023-11-30')) & (date <= pd.to_datetime('2023-12-31')):
    market_id = "5696271"


if (date >= pd.to_datetime('2024-01-01')) & (date <= pd.to_datetime('2024-01-31')):
    market_id = "5714606"

if (date >= pd.to_datetime('2024-02-01')) & (date <= pd.to_datetime('2024-02-29')):
    market_id = "5733529"

if (date >= pd.to_datetime('2024-03-01')) & (date <= pd.to_datetime('2024-03-31')):
    market_id = "5756699"

if (date >= pd.to_datetime('2024-04-01')) & (date <= pd.to_datetime('2024-04-30')):
    market_id = "5776658"

if (date >= pd.to_datetime('2024-05-01')) & (date <= pd.to_datetime('2024-05-31')):
    market_id = "5786631"

if (date >= pd.to_datetime('2024-06-01')) & (date <= pd.to_datetime('2024-06-30')):
    market_id = "5786630"

if (date >= pd.to_datetime('2024-07-01')) & (date <= pd.to_datetime('2024-07-31')):
    market_id = "5786628"

if (date >= pd.to_datetime('2024-08-01')) & (date <= pd.to_datetime('2024-08-31')):
    market_id = "5786634"

if (date >= pd.to_datetime('2024-09-01')) & (date <= pd.to_datetime('2024-09-30')):
    market_id = "5786633"

if (date >= pd.to_datetime('2024-10-01')) & (date <= pd.to_datetime('2024-10-31')):
    market_id = "5786632"

if (date >= pd.to_datetime('2024-11-01')) & (date <= pd.to_datetime('2024-11-30')):
    market_id = "5786629"

if (date >= pd.to_datetime('2024-12-01')) & (date <= pd.to_datetime('2024-12-31')):
    market_id = "5798617"


if (date >= pd.to_datetime('2025-01-01')) & (date <= pd.to_datetime('2025-01-31')):
    market_id = "5815810"

if (date >= pd.to_datetime('2025-02-01')) & (date <= pd.to_datetime('2025-02-28')):
    market_id = "5844634"

if (date >= pd.to_datetime('2025-03-01')) & (date <= pd.to_datetime('2025-03-31')):
    market_id = "5863238"

if (date >= pd.to_datetime('2025-04-01')) & (date <= pd.to_datetime('2025-04-30')):
    market_id = "5878892"

if (date >= pd.to_datetime('2025-05-01')) & (date <= pd.to_datetime('2025-05-31')):
    market_id = "5899671"

if (date >= pd.to_datetime('2025-06-01')) & (date <= pd.to_datetime('2025-06-30')):
    market_id = "5927115"

if (date >= pd.to_datetime('2025-07-01')) & (date <= pd.to_datetime('2025-07-31')):
    market_id = "5959809"

if (date >= pd.to_datetime('2025-08-01')) & (date <= pd.to_datetime('2025-08-31')):
    market_id = "5980688"

if (date >= pd.to_datetime('2025-09-01')) & (date <= pd.to_datetime('2025-09-30')):
    market_id = "6006994"

if (date >= pd.to_datetime('2025-10-01')) & (date <= pd.to_datetime('2025-10-31')):
    market_id = "6036837"

if (date >= pd.to_datetime('2025-11-01')) & (date <= pd.to_datetime('2025-11-30')):
    market_id = "6058601"

if (date >= pd.to_datetime('2025-12-01')) & (date <= pd.to_datetime('2025-12-31')):
    market_id = "6089679"

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