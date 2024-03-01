import serial
import os
import sys
import time
import logging


def read_microtops_serial(port, outfile, comment=None, gui=False):
    # Open the given serial port
    ser = serial.Serial(port, timeout=1)
    logging.info("Initiated communication")
    time.sleep(0.5)
    # Send a Windows-style newline to get it to wake up
    ser.write("\r\n")
    logging.info("Reading data")
    # All of the lines that are produced then are the menu list (Press A for this, B for that etc)
    menu = ser.readlines()
    # We want to print the data in the memory, which is option P
    ser.write("P")
    # Get this data
    data = ser.readlines()
    # Remember to close the serial port or we'll have problems!
    ser.close()
    # We don't want the first two lines of the data
    # (just tells us that it is Microtops data) or the last one (just says END)
    data = data[2:-1]

    if gui is True:
        # Replace all \r (carriage return) and \n (newline) characters
        # and then add the comment to the end of the line
        print("An overview of the AOT and PWC data are below:")
        for line in data:
            spl = line.split(",")
            print((spl[26] + "\t" + spl[-2]))
        print("")
        comment = input("Enter a comment for the data:\n")
    elif comment is not None:
        data = [line.replace("\r", "").replace("\n", "") + ",%s\n" % comment for line in data]

    if os.path.exists(outfile):
        logging.info("File already exists, so appending.")
        # Already has header, so we don't need to write a header again
        # - so remove the first line from the list
        towrite = data[1:]
    else:
        # Doesn't have a header, so write everything
        towrite = data
        if comment is not None:
            # We need to replace the comment that was added to the header line above
            # with the header for that field - in this case COMMENT
            towrite[0] = towrite[0].replace(comment, "COMMENT")

    # Open a file and write the lines to it
    logging.info("Writing data")
    f = open(outfile, 'a')
    f.writelines(towrite)
    f.close()
    print("Data saved to %s. Exiting" % outfile)


def read_microtops_gui():
    print("MICROTOPS II Reading Software")
    print("by Robin Wilson")
    print("-----------------------------")
    # Get the parameters either from the command-line or by asking the user

    port = input("Enter the serial port to use (eg. COM8 or /dev/serial):\n")
    outfile = input("Enter the full path to the file to write to:\n")

    print("Reading data...")
    read_microtops_serial(outfile, port, gui=True)


def main():
    if len(sys.argv) == 3:
        port = sys.argv[1]
        outfile = sys.argv[2]
        read_microtops_serial(port, outfile)
    else:
        read_microtops_gui()


if __name__ == '__main__':
    main()
