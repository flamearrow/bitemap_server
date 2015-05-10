#!/bin/bash
basename=/lamp/foodtrucksmap/foodtrucksmap/trucks/
get_schedules_script=get_schedules.bash

export PYTHONPATH=$PYTHONPATH:/lamp/foodtrucksmap/foodtrucksmap/stuff/script/

for path in $basename/*; do
        [ -d "${path}" ] || continue # if not a directory, skip
        dirname=$path
        if [ -f $dirname/$get_schedules_script ]
        then
            echo run /$dirname/$get_schedules_script
            bash /$dirname/$get_schedules_script
	    if [ $? -ne 0 ]
	    then 
	        echo FAILED
 	    fi
        fi
done
