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

        # Now for your custom code...
        self.message = message
        self.name = name

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


def parseTextFileToRawCSV(path: str) -> tuple[bool, str | Exception]:
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
            raise ParsingError(
                f"Did not find all expected data in file: {path}")
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
        parsedCSVFile = open(f"{parsedFilePath}/receipts_{today}.csv", "w+")
        print(f"Writing data to receipts_{today}.csv...\n")
        parsedCSVFile.writelines(rawCSVString)
        print(f"Saving receipts_{today}.csv file...")
        parsedCSVFile.close()

    except Exception as error:
        message: str
        try:
            message = error.message
        except Exception:
            message = "No message"
        print(
            f"\n/**\n * Failed to parse receipts\n *\n * Error name:\n * \t{error.__class__.__name__}\n * Error message:\n * \t{message}\n *\n */")
