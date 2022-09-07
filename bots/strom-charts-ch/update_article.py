from datetime import datetime as dt
from helpers import *

def run(futures, spotmarket, atomstrom_fr, speicherseen):
    # set date
    q_date = 'Stand: '+ dt.now().strftime("%-d. %-m. %Y")    
    q_date_ = 'Preise für die Schweiz erst ab März 2022 verfügbar. <br>Stand: '+ dt.now().strftime("%-d. %-m. %Y") 

    # Futures
    update_chart(id = "de091de1c8d4f5042323dbd9e08c9548", 
                data = futures,
                notes = q_date_)

    # Spotmarket
    update_chart(id = "046c2f2cc67578f60cc5c36ce55d27ae", 
                data = spotmarket,
                notes = q_date)

    # Atomkraft Fr
    update_chart(id = "4d6b0595264016839099c06df6bdd6af", 
                data = atomstrom_fr,
                notes = q_date)

    # Speicherseen
    update_chart(id = '69bd37806691fc0c2e6786eb38efea63', 
                data = speicherseen.pivot(index=['Jahr_Woche'], columns='Jahr', values='TotalCH_prct').iloc[:,-4:].reset_index(),
                notes = q_date)

