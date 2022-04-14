import os
import re
import sys
from datetime import date

##
# Parser method
# @param {str} path - The absolute path of the file
#
# @todo
#  - We could just leave this file in the same directory as the
#    receipts, inside the one drive. If it lives in the one drive
#    you wouldn't have to pass the file, worry about different
#    locations, or need to every mess with where files are written.
#  - If we need a check on the date, that can easily be done.
#    We can take another input from the user to get what month to
#    to look for.
#  - Add file checking. We need as many lines as files processed
#    and each line should containe all information


def parseTextFileToRawCSV(path: str) -> tuple:
    try:
        # Assume success, if error is thrown, we catch and return
        success: bool = True
        data: dict = {
            "transaction": "",
            "date": "",
            "total": "",
            "card": "",
            "items_purchased": ""
        }

        with open(path, "r") as file:
            total = False
            for line in file.readlines():
                line = line.lower().strip()

                # Here's where shit get's regex
                if (total == True):
                    match = re.search(r'\$\s*(.*)', line)
                    data["total"] = "" if not match else match.group(
                        1).replace(",", "")
                    total = False
                    continue
                if ("transaction #" in line):
                    match = re.search(r'\s*:\s*(.*)', line)
                    data["transaction"] = "" if not match else match.group(1)
                    continue
                elif ("order date" in line):
                    if ("order date" == line):
                        continue
                    match = re.search(r'\s*:\s*(.*)\s', line)
                    data["date"] = "" if not match else match.group(1)
                    continue
                elif ("total" == line):
                    total = True
                    continue
                elif ("total # of items purchased" in line):
                    match = re.search(r'\s*:\s*(.*)', line)
                    data["items_purchased"] = "" if not match else match.group(
                        1)
                    continue
                elif ("payment" in line):
                    match = re.search(r'\s*:\s\D*(.*)',
                                      "Payment: LCC ending in 4570")
                    data["card"] = "" if not match else match.group(
                        1)
                    continue
        return [success, data]
    except Exception as e:
        return [False, e]


if __name__ == "__main__":
    try:
        rawCSVString: str = "Transaction Number,Date,Total Amount Spent,Ending 4-digits of Card,Number of Items Purchased\n"
        today: str = date.today().isoformat()
        fileName, receiptDirectoryPath, parsedFilePath = sys.argv

        for file in os.listdir(receiptDirectoryPath):
            file_path: str = receiptDirectoryPath + file
            success, textOrError = parseTextFileToRawCSV(file_path)
            if (success):
                rawCSVString += f"{textOrError['transaction']},{textOrError['date']},{textOrError['total']},{textOrError['card']},{textOrError['items_purchased']}\n"
            else:
                raise(textOrError)

        # By now we would've caught any issues with parsing
        print(f"\nCreating receipts_{today}.csv file...\n")
        parsedCSVFile = open(
            f"{parsedFilePath}/receipts_{today}.csv", "w+")
        print(f"Writing data to receipts_{today}.csv...\n")
        parsedCSVFile.writelines(rawCSVString)
        print(f"Saving receipts_{today}.csv file...")
        parsedCSVFile.close()
    except ValueError:
        print(f"\n/**\n * This program needs 2 arguments passed to it:\n * \n * -- e.g. ---\n * python3 parse.py Desktop\\foldeOfReceipts Desktop\\folderOfCSV\n * -----------\n * - The path of the directory where the receipts reside\n * - The path of the CSV file that is generated from this program\n */")
    except Exception as error:
        print(
            f"\n/**\n * Failed to parse receipts\n *\n * Error:\n * {error}\n */")
