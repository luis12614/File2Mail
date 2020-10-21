# File2Mail

Sent files in specificied directory under user home directory by email, and move sent files to sent directory.

## The aim of this project
This project written for an all-in-one printer, which has no "forward incoming faxes by email" feature. But you can use anywhere else.

## Security Warning

On this project, you have to write your e-mail password into configuration file wide open. 
There is no any cryptography added for hiding your secret. Will be changed this approach on future versions.  

## Requirements

Make sure [*Python 2.7*](https://www.python.org/downloads/) installed on your system.

## Usage / Installation

* Clone the project by git or download it as ZIP package. 
* Place the files where ever you want.
* Rename *file2mail-example.conf* to *file2mail.conf*
* Make necessary changes in file2mail.conf file 
* Add file2mail.py as scheduled tasks.
* While creating a new scheduled task make sure *"C:\Python27\python.exe"* added to **Program/Script** line, and
"C:\Users\user\path_to\File2Mail\file2mail.py"* added to **Add Arguments (Optional)** line.

["How To" link for "Scheduled Task"](http://windows.microsoft.com/en-us/windows/schedule-task#1TC=windows-7)

## Notes:

This project written as a *Windows* project. Not tested yet, but it may able to run under *Linux*.

File2Mail by Sencer Hamarat - 2015 
