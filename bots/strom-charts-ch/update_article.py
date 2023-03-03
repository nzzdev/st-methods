from datetime import datetime as dt, timedelta
from helpers import *

def run(futures, spotmarket, atomstrom_fr, speicherseen, bfe, bfe2):
    # set date
    q_date = 'Stand: '+ dt.now().strftime("%-d. %-m. %Y")    
    #q_date_ = 'Preise für die Schweiz erst ab März 2022 verfügbar. <br>Stand: '+ dt.now().strftime("%-d. %-m. %Y") 

    # Futures
    update_chart(id = "ac32d7e80793b5151ea699162152edd5", 
                data = futures,
                notes = q_date)

    # Spotmarket
    update_chart(id = "046c2f2cc67578f60cc5c36ce55d27ae", 
                data = spotmarket,
                notes = q_date)

    # Atomkraft Fr
    update_chart(id = "ac32d7e80793b5151ea699162154295a", 
                data = atomstrom_fr,
                notes = q_date)

    # Speicherseen
    update_chart(id = '69bd37806691fc0c2e6786eb38efea63', 
                data = speicherseen,
                notes = '¹ Minimum/Maximum der letzten 5 Jahre.<br>Stand: ' + (dt.now() - timedelta(days=1)).strftime("%-d. %-m. %Y")) 
    
    # BfE Dashboard
    update_chart(id = "e41fb785ca9af558a19582476dafef33", 
                data = bfe,
                notes = '¹ Minimum/Maximum der letzten 5 Jahre.<br>Der Landesverbrauch enthält den gesamten Verbrauch von Haushalten, Gewerbe, Landwirtschaft, Dienstleistungen, Industrie und Verkehr (sogenannter Endverbrauch) zuzüglich Übertragungs- und Verteilverluste (Netzverluste). Zudem ist der Stromverbrauch für den Betrieb von Speicherpump-Kraftwerken enthalten. <br>Stand: ' + (dt.now() - timedelta(days=1)).strftime("%-d. %-m. %Y"))  
    
    update_chart(id = "623c6f7dc5f63244c2d6ca37d0273e5c", 
                data = bfe2)  


