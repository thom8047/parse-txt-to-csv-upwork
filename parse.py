import os
import re
import sys
from datetime import date

##
# Custom Parser Exception
#


class ParsingError(Exception):
    def __init__(self, message=None, name="ParsingError"):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for my custom properties...
        self.message = message
        self.name = name

##
# Parser method
# @param {str} path - The (absolute|relative) path of the file
#


def parseTextFileToRawCSV(path):
    try:
        # Assume success, if error is thrown, we catch and return
        success = True
        data = {
            "transaction": "",
            "date": "",
            "total": "",
            "card": "",
            "items_purchased": ""
        }

        with open(path, "r") as file:
            debit = False
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
                if (debit == True):
                    data["card"] = line
                    debit = False

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
                    match = re.search(r'\s*:\s\D*(.*)', line)
                    debit = True if not match else (
                        True if not match.group(1) else False)
                    data["card"] = "" if not match else match.group(
                        1)
                    continue
        if ("" in data.values()):
            # This error tells us we have a column that wasn't found in the receipt
            raise ParsingError(
                f"Did not find all expected data in file: {path}")
        return [success, data]
    except Exception as e:
        return [False, e]


def parse(pythonFile, directory=os.getcwd()):
    rawCSVString = "Transaction Number,Date,Total Amount Spent,Ending 4-digits of Card,Number of Items Purchased\n"

    for file in os.listdir(directory):
        if file == pythonFile:
            continue
        file_path = os.path.join(directory, file)
        success, textOrError = parseTextFileToRawCSV(file_path)
        if (success):
            rawCSVString += f"{textOrError['transaction']},{textOrError['date']},{textOrError['total']},{textOrError['card']},{textOrError['items_purchased']}\n"
        else:
            raise(textOrError)

    return rawCSVString


if __name__ == "__main__":
    try:
        rawCSVString = ""
        today = date.today().isoformat()
        _, receiptDirectoryPath, parsedFilePath = None, None, None

        try:
            if len(sys.argv) != 3:
                raise ParsingError("", "arg")
            _, receiptDirectoryPath, parsedFilePath = sys.argv
        except ValueError:
            print("Paths cannot be read, check the paths again")
        except ParsingError:
            _ = sys.argv[0]
        finally:
            print(f"No path given, assuming python file is inside the folder of receipts")

        if (receiptDirectoryPath == None):
            rawCSVString = parse(_)
        else:
            rawCSVString = parse(_, receiptDirectoryPath)

        # By now we would've caught any issues with parsing
        print(f"\nCreating receipts_{today}.csv file...\n")
        parsedCSVFile = open(f"{parsedFilePath}/receipts_{today}.csv",
                             "w+") if parsedFilePath else open(f"receipts_{today}.csv", "w+")
        # print(f"Writing data to receipts_{today}.csv...\n")
        parsedCSVFile.writelines(rawCSVString)
        # print(f"Saving receipts_{today}.csv file...\n")
        parsedCSVFile.close()
        print(f"Upload successful!")

    except Exception as error:
        print(error)
