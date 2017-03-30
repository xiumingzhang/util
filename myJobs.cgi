#!/usr/bin/env python

# Author: Xiuming Zhang, MIT CSAIL
# Date: March 29, 2017

import cgi, cgitb
import os 

CPU_STATUS_DIR = '/data/vision/billf/object-properties/lib/updater/vision_machines'
CPU_MACHINE_NAMES = ['asia', 'monday', 'vision01', 'vision07', 'vision13', 'vision19', 'vision25', 'vision31', 'vision37', 'visiongpu05', 'visiongpu11', 'visiongpu17',
    'africa', 'tuesday', 'vision02', 'vision08', 'vision14', 'vision20', 'vision26', 'vision32', 'vision38', 'visiongpu06', 'visiongpu12', 'visiongpu18',
    'america', 'wednesday', 'vision03', 'vision09', 'vision15', 'vision21', 'vision27', 'vision33', 'visiongpu01', 'visiongpu07', 'visiongpu13', 'visiongpu19',
    'europe', 'thursday', 'vision04', 'vision10', 'vision16', 'vision22', 'vision28', 'vision34', 'visiongpu02', 'visiongpu08', 'visiongpu14', 'visiongpu20',
    'antarctica', 'friday', 'vision05', 'vision11', 'vision17', 'vision23', 'vision29', 'vision35', 'visiongpu03', 'visiongpu09', 'visiongpu15',
    'australia', 'saturday', 'vision06', 'vision12', 'vision18', 'vision24', 'vision30', 'vision36', 'visiongpu04', 'visiongpu10', 'visiongpu16'];
GPU_STATUS_DIR = '/data/vision/billf/object-properties/lib/updater/visiongpu_machines'
GPU_MACHINE_NAMES = ['visiongpu01', 'visiongpu07', 'visiongpu13', 'visiongpu19', 'visiongpu02', 'visiongpu08', 'visiongpu14', 'visiongpu20',
    'visiongpu03', 'visiongpu09', 'visiongpu15', 'visiongpu04', 'visiongpu10', 'visiongpu16', 'visiongpu05', 'visiongpu11',
    'visiongpu17', 'visiongpu06', 'visiongpu12', 'visiongpu18'];

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
refresh = form.getvalue('refresh')
user = form.getvalue('user')

print 'Content-type:text/html\r\n\r\n'
print '<html>'
print '<center>'
print '<head>'
if refresh:
    print '<meta http-equiv="refresh" content="30">'
# Table style
print '''
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 800px;
}
td, th {
    border: 1px solid #dddddd;
    text-align: center;
    padding: 6px;
}
tr:nth-child(even) {
    background-color: #dddddd;
}
</style>'''
print '<title>Jobs by %s</title>' % user
print '</head>'
# Simulates clicking C/GPU column twice (descending C/GPU)
print '<body onload="sortTable(3); sortTable(3); sortTable2(2); sortTable2(2)" link="red">'
print '<h1>%s on MIT Vision Machines</h1>' % user
# Sort by C/GPU usage by default
currentURL = os.environ['REQUEST_URI']
if refresh:
    newURL = currentURL.replace('refresh=1&', '')
    print '<p>Auto Refreshing: On. <a href="%s">[Turn Off]</a></p>' % newURL
else:
    idx = currentURL.find('?')
    newURL = currentURL[:(idx + 1)] + 'refresh=1&' + currentURL[(idx + 1):]
    print '<p>Auto Refreshing: Off. <a href="%s">[Turn On]</a></p>' % newURL
print '<p>Default: sorted by descending CPU or GPU. Click on <font color="blue">blue</font> to re-sort or toggle between ascending and descending orders.</p>'

#---------------------------------------------------- Main
# For debug
import sys
import traceback
print
sys.stderr = sys.stdout
try:
    #---------------------------- CPU
    print '<h2>CPU Jobs</h2>'
    # Read status files
    entries = []
    machinesNotRead_CPU = []
    for machineName in CPU_MACHINE_NAMES:
        statusFile = os.path.join(CPU_STATUS_DIR, machineName)
        if os.path.exists(statusFile):
            with open(statusFile, 'r') as f:
                lines = f.readlines()
            lines = [l.strip() for l in lines] # remove whitespace characters like \n
            # Each line is a process
            for line in lines:
                if user in line:
                    entries.append(machineName + ' ' + line)
        else: # file doesn't exist
            machinesNotRead_CPU.append(machineName)
    # Print to table
    print '''<table id="myTable"><tr>
        <th onclick="sortTable(0)" style="color:blue;">Machine</th>
        <th onclick="sortTable(1)" style="color:blue;">PID</th>
        <th onclick="sortTable(2)" style="color:blue;">Command</th>
        <th onclick="sortTable(3)" style="color:blue;">CPU (%)</th>
        <th onclick="sortTable(4)" style="color:blue;">Memory</th>
        <th onclick="sortTable(5)" style="color:blue;">RSS</th>
        <th onclick="sortTable(6)" style="color:blue;">Time</th>
        </tr>'''
    for line in entries:
        machineName, _, _, time, CPU, mem, RSS, PID, cmd = line.split() # delimiter: white spaces
        # Convert memory
        if 't' in mem:
            mem = mem.replace('t', ' TB')
        elif 'g' in mem:
            mem = mem.replace('g', ' GB')
        elif 'm' in mem:
            mem = mem.replace('m', ' MB')
        else:
            mem += ' B'
        if 't' in RSS:
            RSS = RSS.replace('t', ' TB')
        elif 'g' in RSS:
            RSS = RSS.replace('g', ' GB')
        elif 'm' in RSS:
            RSS = RSS.replace('m', ' MB')
        else:
            RSS += ' B'
        print '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (machineName, PID, cmd, CPU, mem, RSS, time)
    print '</table>'
    #---------------------------- GPU
    print '<h2>GPU Jobs</h2>'
    # Read status files
    entries = []
    machinesNotRead_GPU = []
    for machineName in GPU_MACHINE_NAMES:
        statusFile = os.path.join(GPU_STATUS_DIR, machineName)
        if os.path.exists(statusFile):
            with open(statusFile, 'r') as f:
                lines = f.readlines()
            lines = [l.strip() for l in lines] # remove whitespace characters like \n
            # Each line is a process
            for line in lines:
                if user in line:
                    entries.append(machineName + ' ' + line)
        else: # file doesn't exist
            machinesNotRead_GPU.append(machineName)
    # Print to table
    print '''<table id="myTable2"><tr>
        <th onclick="sortTable2(0)" style="color:blue;">Machine</th>
        <th onclick="sortTable2(1)" style="color:blue;">PID</th>
        <th onclick="sortTable2(2)" style="color:blue;">GPU (%)</th>
        <th onclick="sortTable2(3)" style="color:blue;">Memory</th>
        </tr>'''
    for line in entries:
        machineName, _, _, GPU, mem, PID = line.split() # delimiter: white spaces
        # Convert memory
        if 't' in mem:
            mem = mem.replace('t', ' TB')
        elif 'g' in mem:
            mem = mem.replace('g', ' GB')
        elif 'm' in mem:
            mem = mem.replace('m', ' MB')
        else:
            mem += ' B'
        print '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (machineName, PID, GPU, mem)
    print '</table><br><br><br>'
    #---------------------------- Failures
    if len(machinesNotRead_CPU) > 0:
        print '<table><tr><th>Failed to Read CPU Status File(s) of</th></tr>'
        for machineNotRead in machinesNotRead_CPU:
            print '<tr><td>%s</td></tr>' % machineNotRead
    if len(machinesNotRead_GPU) > 0:
        print '<tr><th>Failed to Read GPU Status File(s) of</th></tr>'
        for machineNotRead in machinesNotRead_GPU:
            print '<tr><td>%s</td></tr>' % machineNotRead
    print '</table>'
except:
    print '\n\n<PRE>'
    traceback.print_exc()
print '<script>'
#---------------------------- Sorting function for CPU
print '''
function sortTable(n) {
  var table, rows, switching, i, x, xValue, y, yValue, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTable");
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.getElementsByTagName("TR");
    /*Loop through all table rows (except the first, which contains table headers):*/
    for (i = 1; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare, one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      switch(n) {
        // Float number
        case 1: // fall-through
        case 3:
          xValue = parseFloat(x.innerHTML);
          yValue = parseFloat(y.innerHTML);
          break;
        // TB, MB, KB, B
        case 4: // fall-through
        case 5:
          var arr = x.innerHTML.split(" ");
          xValue = parseFloat(arr[0]);
          unit = arr[1];
          if (unit === "TB") {
            xValue *= 1e12; // to Bytes
          } else if (unit === "GB") {
            xValue *= 1e9;
          } else if (unit === "MB") {
            xValue *= 1e6;
          }
          arr = y.innerHTML.split(" ");
          yValue = parseFloat(arr[0]);
          unit = arr[1];
          if (unit === "TB") {
            yValue *= 1e12; // to Bytes
          } else if (unit === "GB") {
            yValue *= 1e9;
          } else if (unit === "MB") {
            yValue *= 1e6;
          }
          break;
        // mm:ss
        case 6:
          var arr = x.innerHTML.split(":");
          mm = parseFloat(arr[0]);
          ss = parseFloat(arr[1]);
          xValue = mm * 60 + ss; // to seconds
          arr = y.innerHTML.split(":");
          mm = parseFloat(arr[0]);
          ss = parseFloat(arr[1]);
          yValue = mm * 60 + ss; // to seconds
          break;
        // Strings
        default:
          xValue = x.innerHTML.toLowerCase()
          yValue = y.innerHTML.toLowerCase() 
      }
      /*check if the two rows should switch place, based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (xValue > yValue) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (xValue < yValue) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++; 
    } else {
      /*If no switching has been done AND the direction is "asc", set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
'''
#---------------------------- Sorting function for GPU
print '''
function sortTable2(n) {
  var table, rows, switching, i, x, xValue, y, yValue, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTable2");
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.getElementsByTagName("TR");
    /*Loop through all table rows (except the first, which contains table headers):*/
    for (i = 1; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare, one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      switch(n) {
        // Float number
        case 1: // fall-through
        case 2:
          xValue = parseFloat(x.innerHTML);
          yValue = parseFloat(y.innerHTML);
          break;
        // TB, MB, KB, B
        case 3:
          var arr = x.innerHTML.split(" ");
          xValue = parseFloat(arr[0]);
          unit = arr[1];
          if (unit === "TB") {
            xValue *= 1e12; // to Bytes
          } else if (unit === "GB") {
            xValue *= 1e9;
          } else if (unit === "MB") {
            xValue *= 1e6;
          }
          arr = y.innerHTML.split(" ");
          yValue = parseFloat(arr[0]);
          unit = arr[1];
          if (unit === "TB") {
            yValue *= 1e12; // to Bytes
          } else if (unit === "GB") {
            yValue *= 1e9;
          } else if (unit === "MB") {
            yValue *= 1e6;
          }
          break;
        // Strings
        default:
          xValue = x.innerHTML.toLowerCase()
          yValue = y.innerHTML.toLowerCase() 
      }
      /*check if the two rows should switch place, based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (xValue > yValue) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (xValue < yValue) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++; 
    } else {
      /*If no switching has been done AND the direction is "asc", set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
'''
print '</script>'
#---------------------------------------------------------

print '</body>'
print '</center>'
print '</html>'
