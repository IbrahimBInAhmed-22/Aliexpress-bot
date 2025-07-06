
import pandas as pd
def save_data(records):

    data = pd.DataFrame(records)
    with pd.ExcelWriter("Aliexpress.xlsx", engine="openpyxl") as writer:
        data.to_excel(writer, index =False)
    print("=" *40,">")
    print("Data is saved...")